#!/bin/bash

DIFFERENCE=""

# TODO: For loop

# 1. examples/assignments.nacl

cat ../examples/assignments.nacl | ../NaCl.py nacl_content.cpp
DIFFERENCE=`diff nacl_content.cpp ../goldenfiles/assignments.cpp`

echo "$DIFFERENCE" > diff_output.txt

if [ -z "$DIFFERENCE" ]
then
	echo "Assignments: Success"
else
	echo "Assignments: Failed"
fi

# 2. examples/cidr.nacl

cat ../examples/cidr.nacl | ../NaCl.py nacl_content.cpp
DIFFERENCE=`diff nacl_content.cpp ../goldenfiles/cidr.cpp`

echo "$DIFFERENCE" > diff_output.txt

if [ -z "$DIFFERENCE" ]
then
	echo "Cidr: Success"
else
	echo "Cidr: Failed"
fi

# 3. examples/config_options.nacl

cat ../examples/config_options.nacl | ../NaCl.py nacl_content.cpp
DIFFERENCE=`diff nacl_content.cpp ../goldenfiles/config_options.cpp`

echo "$DIFFERENCE" > diff_output.txt

if [ -z "$DIFFERENCE" ]
then
	echo "Config options: Success"
else
	echo "Config options: Failed"
fi

# 4. examples/conntrack.nacl

cat ../examples/conntrack.nacl | ../NaCl.py nacl_content.cpp
DIFFERENCE=`diff nacl_content.cpp ../goldenfiles/conntrack.cpp`

echo "$DIFFERENCE" > diff_output.txt

if [ -z "$DIFFERENCE" ]
then
	echo "Conntrack: Success"
else
	echo "Conntrack: Failed"
fi

# 5. examples/gateway_with_send_time_exceeded.nacl

cat ../examples/gateway_with_send_time_exceeded.nacl | ../NaCl.py nacl_content.cpp
DIFFERENCE=`diff nacl_content.cpp ../goldenfiles/gateway_with_send_time_exceeded.cpp`

echo "$DIFFERENCE" > diff_output.txt

if [ -z "$DIFFERENCE" ]
then
	echo "Gateway with send time exceeded: Success"
else
	echo "Gateway with send time exceeded: Failed"
fi

# 6. examples/iface.nacl

cat ../examples/iface.nacl | ../NaCl.py nacl_content.cpp
DIFFERENCE=`diff nacl_content.cpp ../goldenfiles/iface.cpp`

echo "$DIFFERENCE" > diff_output.txt

if [ -z "$DIFFERENCE" ]
then
	echo "Iface: Success"
else
	echo "Iface: Failed"
fi

# 7. examples/log.nacl

cat ../examples/log.nacl | ../NaCl.py nacl_content.cpp
DIFFERENCE=`diff nacl_content.cpp ../goldenfiles/log.cpp`

echo "$DIFFERENCE" > diff_output.txt

if [ -z "$DIFFERENCE" ]
then
	echo "Log: Success"
else
	echo "Log: Failed"
fi

# 8. examples/nacl.nacl

cat ../examples/nacl.nacl | ../NaCl.py nacl_content.cpp
DIFFERENCE=`diff nacl_content.cpp ../goldenfiles/nacl.cpp`

echo "$DIFFERENCE" > diff_output.txt

if [ -z "$DIFFERENCE" ]
then
	echo "Nacl: Success"
else
	echo "Nacl: Failed"
fi

# 9. examples/nacl_one_liner.nacl

cat ../examples/nacl_one_liner.nacl | ../NaCl.py nacl_content.cpp
DIFFERENCE=`diff nacl_content.cpp ../goldenfiles/nacl_one_liner.cpp`

echo "$DIFFERENCE" > diff_output.txt

if [ -z "$DIFFERENCE" ]
then
	echo "Nacl one liner: Success"
else
	echo "Nacl one liner: Failed"
fi

# 10. examples/nat_and_gateway.nacl

cat ../examples/nat_and_gateway.nacl | ../NaCl.py nacl_content.cpp
DIFFERENCE=`diff nacl_content.cpp ../goldenfiles/nat_and_gateway.cpp`

echo "$DIFFERENCE" > diff_output.txt

if [ -z "$DIFFERENCE" ]
then
	echo "Nat and gateway: Success"
else
	echo "Nat and gateway: Failed"
fi

# 11. examples/vlan.nacl

cat ../examples/vlan.nacl | ../NaCl.py nacl_content.cpp
DIFFERENCE=`diff nacl_content.cpp ../goldenfiles/vlan.cpp`

echo "$DIFFERENCE" > diff_output.txt

if [ -z "$DIFFERENCE" ]
then
	echo "Vlan: Success"
else
	echo "Vlan: Failed"
fi
