#!/bin/bash

DIFFERENCE=""
CPP_OUTPUT="nacl_content.cpp"
GOLDENFILES="goldenfiles"

declare -a examples=(
	"assignments"
	"cidr"
	"config_options"
	"conntrack"
	"conntrack_with_timeout"
	"conntrack_with_timeout_assignments"
	"functions"
	"gateway_with_forward_chain"
	"gateway_with_send_time_exceeded"
	"iface_with_limits"
	"iface_without_network_configuration"
	"iface"
	"lb"
	"lb_assignment_functionality"
	"lb_assignment_functionality_2"
	"lb_with_uplink"
	"log"
	"nacl"
	"nacl_one_liner"
	"nat_and_gateway"
	"syslog"
	"timers"
	"vlan_routing"
	"vlan_with_mac"
	"vlan"
)

GREEN="\033[92m" 	# Green
RED="\033[38;5;1m" 	# Red
NO_COLOR="\033[0m" 	# No color

for i in "${examples[@]}"
do
	cat ../examples/$i.nacl | ../NaCl.py $CPP_OUTPUT
	DIFFERENCE=`diff $CPP_OUTPUT ../$GOLDENFILES/$i.cpp`
	echo "$DIFFERENCE" > diff_output.txt

	if [ -z "$DIFFERENCE" ]
	then
		echo -e "$i: ${GREEN}SUCCESS${NO_COLOR}"
	else
		echo -e "$i: ${RED}FAILED${NO_COLOR}"
	fi
done
