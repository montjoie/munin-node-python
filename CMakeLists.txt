cmake_minimum_required(VERSION 3.4)
project(munin-node-python)

set(MNP_ETC "/etc/munin-node")
set(MNP_VAR "var/lib/munin")
set(MNP_USR "/usr/libexec/munin/plugins/")
set(XYTHON_TMP "/var/lib/xython/tmp")

install(FILES etc/munin-node DESTINATION ${MNP_ETC}/plugin-conf.d/)
install(DIRECTORY munin/plugins/node.d DESTINATION ${MNP_USR})
install(DIRECTORY DESTINATION /${MNP_ETC})
install(DIRECTORY DESTINATION /${MNP_ETC}/plugin-conf.d)
