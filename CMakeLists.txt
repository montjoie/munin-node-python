cmake_minimum_required(VERSION 3.5)
project(munin-node-python)

set(MNP_ETC "/etc/munin")
set(MNP_VAR "var/lib/munin")
set(MNP_VARLOG "var/log/munin-node")
set(MNP_USR "/usr/libexec/munin/plugins/")

install(FILES etc/munin-node DESTINATION ${MNP_ETC}/plugin-conf.d/)
install(FILES munin-node-configure DESTINATION /usr/bin/ PERMISSIONS
	OWNER_EXECUTE OWNER_WRITE OWNER_READ GROUP_READ GROUP_EXECUTE
	WORLD_READ WORLD_EXECUTE)
install(DIRECTORY munin/plugins/node.d/ DESTINATION ${MNP_USR})
install(DIRECTORY munin/plugins/node.d.linux/ DESTINATION ${MNP_USR})
install(DIRECTORY plugins/ DESTINATION ${MNP_USR})
install(FILES munin/plugins/plugin.sh.in DESTINATION ${MNP_USR})
install(DIRECTORY DESTINATION ${MNP_ETC})
install(DIRECTORY DESTINATION ${MNP_ETC}/plugin-conf.d)
install(DIRECTORY DESTINATION /${MNP_VAR})
install(DIRECTORY DESTINATION /${MNP_VAR}/plugin-state)
install(DIRECTORY DESTINATION /${MNP_VARLOG})
