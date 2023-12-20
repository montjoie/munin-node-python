#!/bin/bash

TARGET_DIR=/
INSTALL=install

$INSTALL -m 0755 -d /var/log/munin-node
$INSTALL -m 0755 -d $TARGET_DIR/etc/munin/plugins
$INSTALL -m 0755 -d $TARGET_DIR/etc/munin/plugin-conf.d
$INSTALL -m 0755 -d $TARGET_DIR/usr/libexec/munin/plugins
$INSTALL -m 0755 -d $TARGET_DIR/var/lib/munin/plugin-state
$INSTALL -m 0755 munin-node-python/muninnodepython.py $TARGET_DIR/usr/bin/munin-node
echo "main()" >> $TARGET_DIR/usr/bin/munin-node
$INSTALL -m 0644 etc/munin-node $TARGET_DIR/etc/munin/plugin-conf.d/
$INSTALL -m 0755 munin/plugins/node.d/df.in $TARGET_DIR/usr/libexec/munin/plugins/df_
$INSTALL -m 0755 munin/plugins/node.d/df_inode.in $TARGET_DIR/usr/libexec/munin/plugins/df_inode_
$INSTALL -m 0755 munin/plugins/node.d.linux/cpu.in $TARGET_DIR/usr/libexec/munin/plugins/cpu
$INSTALL -m 0755 munin/plugins/node.d.linux/if_.in $TARGET_DIR/usr/libexec/munin/plugins/if_
$INSTALL -m 0755 munin/plugins/node.d.linux/memory.in $TARGET_DIR/usr/libexec/munin/plugins/memory
$INSTALL -m 0755 munin/plugins/node.d.linux/sensors_.in $TARGET_DIR/usr/libexec/munin/plugins/sensors_
$INSTALL -m 0755 munin/plugins/node.d.linux/uptime.in $TARGET_DIR/usr/libexec/munin/plugins/uptime
$INSTALL -m 0644 munin/plugins/plugin.sh.in $TARGET_DIR/usr/libexec/munin/plugins/plugin.sh
sed -i 's,@@BASH@@,/bin/bash,' $TARGET_DIR/usr/libexec/munin/plugins/*
sed -i 's,@@GOODSH@@,/bin/sh,' $TARGET_DIR/usr/libexec/munin/plugins/*

