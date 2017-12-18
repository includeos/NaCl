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
	"iface"
	"lb"
	"lb_assignment_functionality"
	"lb_with_uplink"
	"log"
	"nacl"
	"nacl_one_liner"
	"nat_and_gateway"
	"syslog"
	"vlan"
)

for i in "${examples[@]}"
do
	cat ../examples/$i.nacl | ../NaCl.py $CPP_OUTPUT
	DIFFERENCE=`diff $CPP_OUTPUT ../$GOLDENFILES/$i.cpp`
	echo "$DIFFERENCE" > diff_output.txt

	if [ -z "$DIFFERENCE" ]
	then
		echo "$i: Success"
	else
		echo "$i: Failed"
	fi
done
