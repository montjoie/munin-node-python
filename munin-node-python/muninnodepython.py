#!/usr/bin/env python3

"""
    munin-node-python: a munin-node rewrite in python
    Copyright (C) 2023 Corentin LABBE <clabbe.montjoie@gmail.com>
    SPDX-License-Identifier: GPL-2.0
"""

import asyncio
import argparse
import os
import socket
from datetime import datetime
import re
import time
import subprocess


# Xymon use a format for day number not availlable on python
def xytime(ts):
    date = datetime.fromtimestamp(ts)
    first = date.strftime("%a %b %d").replace(" 0", ' ')
    last = date.strftime(" %H:%M:%S %Y")
    return first + last


class pymunin:
    def __init__(self):
        self.tests = []
        self.lldebug = True
        self.name = socket.gethostname()
        self.pluginconf = {}
        self.caps = []
        self.etc_plugin = "/etc/munin/plugins"
        self.plugindir = "/usr/libexec/munin/plugins"

    def debug(self, buf):
        if self.lldebug:
            print(buf)

    def log(self, facility, buf):
        f = open("%s/%s.log" % (self.xt_logdir, facility), 'a')
        f.write(f"{xytime(time.time())} {buf}\n")
        f.close()

    def error(self, buf):
        print(buf)
        self.log("error", buf)

    def set_netport(self, port):
        if port <= 0 or port > 65535:
            return False
        self.netport = port
        return True

    def exec_plugin(self, plugin, options):
        user = 'root'
        group = 'root'
        env = {}
        env["MUNIN_PLUGSTATE"] = "/var/lib/munin-node/plugin-state/"
        env["MUNIN_LIBDIR"] = "/usr/libexec/munin/"
        if "dirtyconfig" in self.caps:
            env["MUNIN_DIRTY_CONFIG"] = '1'
        # if "multigraph" in self.caps:
        #    env["MUNIN_CAP_MULTIGRAPH"] = '1'
        for k in self.pluginconf:
            r = re.match(k, plugin)
            if r is not None:
                conf = self.pluginconf[k]
                if "user" in conf:
                    user = conf["user"]
                if "group" in conf:
                    group = conf["group"]
                if "env" in conf:
                    for e in conf["env"]:
                        env[e] = conf["env"][e]
        self.debug(f"DEBUG: run {plugin} as {user}:{group}")
        ex = [plugin]
        if options:
            ex.append(options)
        try:
            ret = subprocess.run(ex, capture_output=True, env=env, user=user, group=group)
        except FileNotFoundError as e:
            data = str(e)
            return data
        data = ret.stdout.decode("UTF8") + ret.stderr.decode("UTF8")
        data += ".\n"
        if ret.returncode != 0:
            self.error(f"ERROR: failed to exec {plugin}")
            # error
            print(data)
        return data

    def parse(self, buf):
        self.debug(f"DEBUG: get {buf}END")
        if buf[:8] == 'version ':
            sbuf = f"munins node on {self.name} version: 0"
            return sbuf
        if buf[:4] == 'quit':
            return ""
        if buf[:4] == 'cap ':
            tokens = buf.split(" ")
            tokens.pop(0)
            CAPS = ['dirtyconfig']
            for cap in tokens:
                self.caps.append(cap)
                if cap in CAPS:
                    self.debug(f"DEBUG: CAP support {cap}")
                else:
                    self.debug(f"DEBUG: CAP unsupported {cap}")
            return buf
        if buf[:4] == 'list':
            dirFiles = os.listdir(self.etc_plugin)
            pluginlist = " ".join(dirFiles)
            pluginlist += "\n"
            return pluginlist
        if buf[:7] == 'config ':
            self.debug("DEBUG: handle config")
            tokens = buf.split(" ")
            if len(tokens) != 2:
                print(f"ERROR: invalid tokens len {len(tokens)}")
                # error
                return
            plugin = tokens[1].rstrip()
            data = self.exec_plugin(f"{self.etc_plugin}/{plugin}", "config")
            return data
        if buf[:6] == 'fetch ':
            self.debug("DEBUG: handle fetch")
            tokens = buf.split(" ")
            if len(tokens) != 2:
                print(f"ERROR: invalid tokens len {len(tokens)}")
                # error
                return "ERROR"
            plugin = tokens[1].rstrip()
            data = self.exec_plugin(f"{self.etc_plugin}/{plugin}", None)
            return data
        if buf == "quit":
            return ""
        return "# Unknown command. Try cap, list, nodes, config, fetch, version or quit\n"

    async def talk_to_client(self, reader, writer):
        peername = writer.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        greet = f"# munin node at {self.name}\n"
        writer.write(greet.encode("UTF8"))

        while True:
            data = await reader.read(1024)
            send = self.parse(data.decode("UTF8"))
            if send == "":
                writer.close()
                return
            writer.write(send.encode("UTF8"))
            try:
                await writer.drain()
            except ConnectionResetError:
                writer.close()
                return

    def read_conf(self):
        f = open("/etc/munin/plugin-conf.d/munin-node")
        lines = f.readlines()
        section = None
        for line in lines:
            line = line.rstrip()
            if len(line) == 0:
                continue
            if line[0] == '#':
                continue
            if line[0] == '[':
                line = line[1:]
                tokens = line.split(']')
                if len(tokens) == 0:
                    continue
                section = tokens[0]
                self.pluginconf[section] = {}
                continue
            tokens = line.split(" ")
            k = tokens.pop(0)
            if k == 'user':
                self.pluginconf[section]["user"] = tokens[0]
                continue
            if k == 'group':
                self.pluginconf[section]["group"] = tokens[0]
                continue
            if k[:4] == 'env.':
                if 'env' not in self.pluginconf[section]:
                    self.pluginconf[section]["env"] = {}
                nenv = k[4:]
                self.pluginconf[section]["env"][nenv] = " ".join(tokens)
                continue
            self.debug(f"DEBUG: unmatched {section} {line}")

    def configure(self):
        self.debug("DEBUG: CONFIGURE")
        dirFiles = os.listdir(self.plugindir)
        for plugin in dirFiles:
            if plugin in ["plugins.history", "plugin.sh"]:
                continue
            self.debug(f"TEST {plugin}")
            ret = self.exec_plugin(f"{self.plugindir}/{plugin}", "autoconf")
            if ret[:3] == 'yes':
                if plugin[-1] == '_':
                    ret = self.exec_plugin(f"{self.plugindir}/{plugin}", "suggest")
                    self.debug(ret)
                    print(ret)
                    for x in ret.split('\n'):
                        if x == '.' or len(x) == 0:
                            continue
                        print(f"ln -s {self.plugindir}/{plugin} {self.etc_plugin}/{plugin}{x}")
                else:
                    self.debug(f"USE {plugin}")
                    print(f"ln -s {self.plugindir}/{plugin} {self.etc_plugin}/{plugin}")
            else:
                self.debug(f"DEBUG: do not use {plugin}")
                self.debug(ret)

    async def run(self):
        coro = await asyncio.start_server(self.talk_to_client, 'localhost', self.netport)
        async with coro:
            await coro.serve_forever()


def main():
    print('munin-node-python v1')
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", "-d", help="increase debug level", action="store_true")
    parser.add_argument("--daemon", "-D", help="start daemon", action="store_true")
    parser.add_argument("--configure", help="Do like munin-node-configure", action="store_true")
    parser.add_argument("--netport", help="Network port", default=4950)
    parser.add_argument("--logdir", help="Override xython log directory", default="/var/log/munin-node/")
    parser.add_argument("--etcdir", help="Override xymon etc directory", default="/etc/munin/")
    parser.add_argument("--name", help="Override hostname", default=socket.gethostname())
    args = parser.parse_args()

    X = pymunin()
    X.read_conf()
    X.set_netport(int(args.netport))
    X.lldebug = args.debug
    X.xt_logdir = args.logdir
    X.etcdir = args.etcdir
    X.name = args.name

    if args.configure:
        X.configure()

    if args.daemon:
        asyncio.run(X.run())


main()
