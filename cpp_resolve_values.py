import sys

from shared_constants import *

# ---- Helper functions ----

def get_pckt_name_cpp(subtype):
	return pckt_names[subtype.lower()]

def get_access_op_cpp(subtype):
	return DOT

def get_pckt_cast_cpp(subtype):
	subtype_lower = subtype.lower()
	if subtype_lower == IP:
		return "" # Already have (IP) pckt as input to Filter's operator() method

	pckt_name = pckt_names.get(subtype_lower)

	if pckt_name is not None:
		return AUTO + INCLUDEOS_REFERENCE_OP + " " + pckt_name + " = " + get_cast_cpp(subtype_lower, IP_PCKT)	
	else:
		sys.exit("Error: Invalid subtype (" + subtype + "), or pckt name or cpp pckt name not found")

def get_cast_cpp(cast_to_proto, pckt_name):
	proto = cast_to_proto.lower()
	if proto not in cpp_pckt_classes:
		sys.exit("Error: Invalid protocol: " + cast_to_proto)

	cpp_pckt_class = cpp_pckt_classes[proto]

	if proto != ICMP and pckt_name != ICMP_PCKT:
		return "static_cast<" + cpp_pckt_class + INCLUDEOS_REFERENCE_OP + ">(" + pckt_name + ");"
	else:
		return "*(" + cpp_pckt_class + "*) " + INCLUDEOS_REFERENCE_OP + pckt_name + ";"

def transpile_ip4_addr_cpp(ip_addr_ctx):
	parts = ip_addr_ctx.Number() # list
	part0 = parts[0].getText()
	part1 = parts[1].getText()
	part2 = parts[2].getText()
	part3 = parts[3].getText()

	if int(part0) > BYTE_LIMIT or int(part1) > BYTE_LIMIT or int(part2) > BYTE_LIMIT or int(part3) > BYTE_LIMIT:
		sys.exit("Error: IPv4 addr " + ip_addr_ctx.getText() + " contains bytes greater than " + str(BYTE_LIMIT))

	return INCLUDEOS_IP4_ADDR_CLASS + "{" + ip_addr_ctx.getText().replace(".", ",") + "}"

def transpile_ip4_cidr_cpp(ip_cidr_ctx):
	parts = ip_cidr_ctx.ipv4_addr().Number() # list
	part0 = parts[0].getText()
	part1 = parts[1].getText()
	part2 = parts[2].getText()
	part3 = parts[3].getText()

	if int(part0) > BYTE_LIMIT or int(part1) > BYTE_LIMIT or int(part2) > BYTE_LIMIT or int(part3) > BYTE_LIMIT:
		sys.exit("Error: IPv4 cidr " + ip_cidr_ctx.getText() + " contains bytes greater than " + str(BYTE_LIMIT))

	mask = ip_cidr_ctx.cidr_mask().integer().getText()

	if int(mask) > MASK_LIMIT:
		sys.exit("Error: IPv4 cidr mask in " + ip_cidr_ctx.getText() + " is greater than " + str(MASK_LIMIT))

	return INCLUDEOS_IP4_CIDR_CLASS + "{" + part0 + "," + part1 + "," + part2 + "," + part3 + "," + mask + "}"

# ---- < Helper functions ----

# Main function when processing 
def resolve_value_cpp(val_ctx, subtype=""):
	if val_ctx is None:
		return ""

	# value: primitive_type | rng | string | value_name | obj | list_t;

	val = val_ctx.getText()

	if val_ctx.value_name() is not None:
		return transpile_value_name_cpp(val_ctx, subtype)

	if val_ctx.primitive_type() is not None:
		if val_ctx.primitive_type().numeric_type() is not None:
			return transpile_numeric_value_cpp(val_ctx.primitive_type().numeric_type())

		if val_ctx.primitive_type().bool_val() is not None:
			return val.lower()

		if val_ctx.primitive_type().ipv4_cidr() is not None:
			return transpile_ip4_cidr_cpp(val_ctx.primitive_type().ipv4_cidr())

	if val_ctx.rng() is not None:
		numeric_vals 	= val_ctx.rng().numeric_type() # list
		from_val 		= numeric_vals[0]
		to_val 			= numeric_vals[1]

		# For now we have three numeric_types: ipv4_addr, integer, decimal
		if (from_val.ipv4_addr() is not None and to_val.ipv4_addr() is not None) or \
		(from_val.integer() is not None and to_val.integer() is not None) or \
		(from_val.decimal() is not None and to_val.decimal() is not None):
			from_transpiled = transpile_numeric_value_cpp(from_val)
			to_transpiled 	= transpile_numeric_value_cpp(to_val)
			return [ from_transpiled, to_transpiled ]
		else:
			sys.exit("Error: A range's values need to be of the same type (" + val + ")")

	if val_ctx.string() is not None:
		return val

	if val_ctx.obj() is not None:
		return resolve_object_cpp(val_ctx.obj())

	if val_ctx.list_t() is not None:
		return resolve_list_t_cpp(val_ctx.list_t())

	sys.exit("Error: Undefined value: " + val_ctx.getText())

def resolve_object_cpp(obj_ctx):
	resolved_values = [ IS_LIST ]
	for pair in obj_ctx.key_value_list().key_value_pair():
		resolved_values.append(resolve_value_cpp(pair.value()))
	return resolved_values

def resolve_list_t_cpp(list_ctx):
	resolved_values = [ IS_LIST ]
	for val in list_ctx.value_list().value():
		resolved_values.append(resolve_value_cpp(val))
	return resolved_values

def transpile_value_name_cpp(val_ctx, subtype):
	name_parts = val_ctx.value_name().getText().split(DOT)
	name = name_parts[0]

	# Checking if obj is the name of an element defined
	# in the NaCl file
	element = elements.get(name)
	if element is None:
		# No element has been defined in the NaCl file with this name
		if len(name_parts) == 1:
			# If no properties/members, just this one name:
			# Check if name is a predefined value and return its IncludeOS value
			# if it is:
			predefined_val = predefined_values_cpp.get(name.lower())
			if predefined_val is None:
				sys.exit("Error: Undefined: " + name)
			return predefined_val
		else:
			# Then properties/members are referenced, and this could be f.ex. tcp.dport
			
			if name.lower() in proto_objects:
				# Checking if obj == tcp, udp, ip, icmp or ct
				
				if subtype == "":
					sys.exit("Error: Trying to transpile protocol object (" + name + "), but the function's subtype has not been given")

				if name.lower() not in legal_obj_types[subtype.lower()]:
					sys.exit("Error: A function of type " + subtype + " cannot test on " + name + " properties")

				# Remove the name of the proto object - only need its members/properties
				name_parts.pop(0)
				properties = name_parts
				if len(properties) > 1:
					sys.exit("Error: Undefined protocol object properties: " + val_ctx.value_name().getText())

				pckt_name 	= get_pckt_name_cpp(subtype)
				access_op 	= get_access_op_cpp(subtype)
				prop 		= properties[0].lower()
				proto_obj 	= proto_objects[name.lower()]
				cast 		= proto_obj.resolve_cast_cpp(prop)
				method 		= proto_obj.resolve_method_cpp(prop)

				if name.lower() == CT:
					# return CT + access_op + method + "(" + pckt_name + ")"
					return INCLUDEOS_CT_ENTRY + ARROW + method

				if subtype.lower() == ICMP and name.lower() == IP:
					method = INCLUDEOS_ICMP_IP_ACCESS_METHOD + access_op + method

				transpiled_value = "" if cast == "" else cast + " "
				transpiled_value += pckt_name + access_op + method
				return transpiled_value

			sys.exit("Error: Undefined: " + name)

	# element is not None:

	if len(name_parts) == 1:
		# No members referenced - so referencing an element that exists/should exist
		return resolve_element_values_cpp(element)
	else:
		name_parts.pop(0) # Remove the name of the element - has been found
		return resolve_member_value_from_element_cpp(element, name_parts)

def resolve_element_values_cpp(element):
	# value in a function is the name of an element - resolve all values in this element

	# Base types:
	# UNTYPED_INIT
	# TYPED_INIT
	# FUNCTION

	if element.base_type == BASE_TYPE_FUNCTION:
		sys.exit("Error: The name of a function (" + element.name + ") cannot be used as a value name in a comparison")

	return resolve_value_cpp(element.ctx.value())

def resolve_member_value_from_obj_cpp(obj_ctx, member_list):
	member = member_list[0]

	for pair in obj_ctx.key_value_list().key_value_pair():
		if pair.key().getText() == member:			
			# End of recursion condition:
			if len(member_list) == 1:
				return resolve_value_cpp(pair.value())

			# Recursion
			if pair.value().obj() is not None:
				member_list.pop(0) # Remove found member
				# And search deeper
				return resolve_member_value_from_obj_cpp(pair.value().obj(), member_list)
			else:
				return None

def find_assignment_element(name):
	name_parts = name.split(DOT)
	
	if len(name_parts) < 1:
		return None

	# Check if have an assignment that is an exact match
	e = elements.get(name)
	if e is not None:
		return e
		# if e.ctx.value().obj() is not None:
		#	return resolve_member_value_from_obj_cpp(e.ctx.value().obj(), orig_name)
		# return resolve_value_cpp(e.ctx.value())
	else:
		# Remove last part (after DOT) to see if an element exists with this name
		name_parts = name_parts[:-1]
		name = ".".join(name_parts)
		return find_assignment_element(name)

def resolve_member_value_from_element_cpp(element, member_list):
	# Find the value indicated by member_list

	# member_list f.ex. ["e1", "e1-2", "e1-3"]
	# loop through first time and find e1 (level 1)
	# then recursion where the e1 (first level) has been popped

	if element.base_type == BASE_TYPE_FUNCTION:
		sys.exit("Error: A function (" + element.name + ") does not have any named attributes")

	if element.base_type == BASE_TYPE_UNTYPED_INIT:
		val = element.get_member_value(member_list)
		if val is None:
			sys.exit("Error: Could not identify " + element.name + "." + ".".join(member_list))
		
		if not isinstance(val, dict):
			return val # The value has been resolved inside the Untyped element's process method
	
		# if isinstance(val, dict):
		# 	sys.exit("Error (" + element.name + "): This feature is not supported yet: " + element.name + "." + ".".join(member_list))
		# Have another way of resolving the value for now: Continue with the function:

	if element.base_type == BASE_TYPE_UNTYPED_INIT or element.base_type == BASE_TYPE_TYPED_INIT:
		value = element.ctx.value()
		found_val = None
		
		if value.obj() is not None:
			# TODO?: Could be replaced by get_member_value in Element class

			found_val = resolve_member_value_from_obj_cpp(value.obj(), list(member_list))

			if found_val is not None:
				return found_val

		assignment_value_name = element.name + "." + ".".join(member_list)
		
		print "Assignment key:", assignment_value_name
		
		e = find_assignment_element(assignment_value_name)
		if e is None:
			sys.exit("Error: Could not identify " + element.name + "." + ".".join(member_list))
		else:
			if e.ctx.value().obj() is not None:
				# Remove the name of the e element to get only the name of the member left
				member = assignment_value_name.replace(e.name + ".", "")
				
				found_val = resolve_member_value_from_obj_cpp(e.ctx.value().obj(), [ member ])
				if found_val is not None:
					return found_val
				else:
					sys.exit("Error: Could not identify " + element.name + "." + ".".join(member_list))
			
			return resolve_value_cpp(e.ctx.value())

	sys.exit("Error: No support for handling element of base type " + element.base_type)

def transpile_numeric_value_cpp(numeric_value):
	if numeric_value.ipv4_addr() is not None:
		return transpile_ip4_addr_cpp(numeric_value.ipv4_addr())
	
	if numeric_value.integer() is not None or \
	numeric_value.decimal() is not None:
		return numeric_value.getText()

	sys.exit("Error: Undefined numeric value: " + numeric_value.getText())
