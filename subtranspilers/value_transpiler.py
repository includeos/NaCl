# This file is a part of the IncludeOS unikernel - www.includeos.org
#
# Copyright 2017-2018 IncludeOS AS, Oslo, Norway
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
# To avoid: <...>/NaCl/subtranspilers/value_transpiler.py:1: RuntimeWarning: Parent module '<...>/NaCl/subtranspilers' not found while handling absolute import

from NaCl import exit_NaCl, exit_NaCl_internal_error, BASE_TYPE_UNTYPED_INIT, BASE_TYPE_TYPED_INIT, BASE_TYPE_FUNCTION
from shared import *

VALUE_TRANSPILER = "value_transpiler"

# TODO: Move to another file (__init__.py or make value_transpiler into a folder
# containing value_transpiler.py and cpp_value_transpiler.py?)
# -------------------- Value_transpiler --------------------

class Value_transpiler(object):
	def __init__(self, elements):
		# All elements (Iface, Filter, Port, etc.) that have been identified in the NaCl file
		# (by the visitor) are placed here because each language template (f.ex. cpp_template.py)
		# needs to access the elements when resolving a variable name f.ex.
		# Dictionary where key is the name of the Element and the value is the Element object or
		# subtype of this
		self.elements = elements

	def get_class_name(self):
		return self.__class__.__name__

	def transpile(self, val_ctx, subtype=""):
		# Should be implemented by class that extends this class
		exit_NaCl_internal_error("The class " + self.get_class_name() + " needs to override the method " + \
			"transpile")

# < Value_transpiler

# -------------------- Cpp_value_transpiler --------------------

class Cpp_value_transpiler(Value_transpiler):
	def __init__(self, elements):
		super(Cpp_value_transpiler, self).__init__(elements)
		# print "Cpp_value_transpiler"

	# Main function when processing
	def transpile(self, val_ctx, subtype=""):
		if val_ctx is None:
			return ""

		# value: primitive_type | rng | string | value_name | obj | list_t;

		val = val_ctx.getText()

		if val_ctx.value_name() is not None:
			return self.transpile_value_name(val_ctx, subtype)

		if val_ctx.primitive_type() is not None:
			if val_ctx.primitive_type().numeric_type() is not None:
				return self.transpile_numeric_value(val_ctx.primitive_type().numeric_type())

			if val_ctx.primitive_type().bool_val() is not None:
				return val.lower()

			if val_ctx.primitive_type().ipv4_cidr() is not None:
				return self.transpile_ip4_cidr(val_ctx.primitive_type().ipv4_cidr())

		if val_ctx.rng() is not None:
			numeric_vals 	= val_ctx.rng().numeric_type() # list
			from_val 		= numeric_vals[0]
			to_val 			= numeric_vals[1]

			# For now we have three numeric_types: ipv4_addr, integer, decimal
			if (from_val.ipv4_addr() is not None and to_val.ipv4_addr() is not None) or \
			(from_val.integer() is not None and to_val.integer() is not None) or \
			(from_val.decimal() is not None and to_val.decimal() is not None):
				from_transpiled = self.transpile_numeric_value(from_val)
				to_transpiled 	= self.transpile_numeric_value(to_val)
				return [ from_transpiled, to_transpiled ]
			else:
				exit_NaCl(val_ctx, "A range's values need to be of the same type (" + val + ")")

		if val_ctx.string() is not None:
			return val_ctx.parser.getTokenStream().getText(interval=(val_ctx.start.tokenIndex, val_ctx.stop.tokenIndex))

		if val_ctx.obj() is not None:
			return self.resolve_object(val_ctx.obj())

		if val_ctx.list_t() is not None:
			return self.resolve_list_t(val_ctx.list_t())

		exit_NaCl(val_ctx, "Undefined value " + val_ctx.getText())

	def resolve_object(self, obj_ctx):
		resolved_values = [ IS_LIST ]
		for pair in obj_ctx.key_value_list().key_value_pair():
			resolved_values.append(self.transpile(pair.value()))
		return resolved_values

	def resolve_list_t(self, list_ctx):
		resolved_values = [ IS_LIST ]
		for val in list_ctx.value_list().value():
			resolved_values.append(self.transpile(val))
		return resolved_values

	def transpile_value_name(self, val_ctx, subtype):
		name_parts = val_ctx.value_name().getText().split(DOT)
		name = name_parts[0]

		# Checking if obj is the name of an element defined
		# in the NaCl file
		element = self.elements.get(name) # self.nacl_state.elements.get(name)
		if element is None:
			# No element has been defined in the NaCl file with this name
			if len(name_parts) == 1:
				# If no properties/members, just this one name:
				# Check if name is a predefined value and return its IncludeOS value
				# if it is:
				predefined_val = predefined_values_cpp.get(name.lower())
				if predefined_val is None:
					exit_NaCl(val_ctx, "Undefined value " + name)
				return predefined_val
			else:
				# Then properties/members are referenced, and this could be f.ex. tcp.dport

				if name.lower() in proto_objects:
					# Checking if obj == tcp, udp, ip, icmp or ct

					if subtype == "":
						exit_NaCl(val_ctx, "Trying to transpile protocol object (" + \
							name + "), but the function's subtype has not been given")

					if name.lower() not in legal_obj_types[subtype.lower()]:
						exit_NaCl(val_ctx, "A function of subtype " + subtype + " cannot test on " + \
							name + " properties")

					# Remove the name of the proto object - only need its members/properties
					name_parts.pop(0)
					properties = name_parts
					if len(properties) > 1:
						exit_NaCl(val_ctx, "Undefined protocol object properties: " + val_ctx.value_name().getText())

					pckt_name 	= self.get_pckt_name(subtype)
					access_op 	= self.get_access_op(subtype)
					prop 		= properties[0].lower()
					proto_obj 	= proto_objects[name.lower()]
					cast 		= proto_obj.resolve_cast_cpp(prop)
					method 		= proto_obj.resolve_method_cpp(prop, val_ctx)

					if name.lower() == CT:
						# return CT + access_op + method + "(" + pckt_name + ")"
						return INCLUDEOS_CT_ENTRY + ARROW + method

					if subtype.lower() == ICMP and name.lower() == IP:
						method = INCLUDEOS_ICMP_IP_ACCESS_METHOD + access_op + method

					transpiled_value = "" if cast == "" else cast + " "
					transpiled_value += pckt_name + access_op + method
					return transpiled_value

				exit_NaCl(val_ctx, "Undefined value " + name)

		# element is not None:

		if len(name_parts) == 1:
			# No members referenced - so referencing an element that exists/should exist
			return self.resolve_element_values(element, val_ctx)
		else:
			name_parts.pop(0) # Remove the name of the element - has been found
			return self.resolve_member_value_from_element(element, name_parts, val_ctx)

	def resolve_element_values(self, element, ctx):
		# value in a function is the name of an element - resolve all values in this element

		# Base types:
		# UNTYPED_INIT
		# TYPED_INIT
		# FUNCTION

		if element.base_type == BASE_TYPE_FUNCTION:
			exit_NaCl(ctx, "The name of a function (" + element.name + \
				") cannot be used as a value name in a comparison")

		return self.transpile(element.ctx.value())

	def resolve_member_value_from_obj(self, obj_ctx, member_list):
		member = member_list[0]

		for pair in obj_ctx.key_value_list().key_value_pair():
			if pair.key().getText() == member:
				# End of recursion condition:
				if len(member_list) == 1:
					return self.transpile(pair.value())

				# Recursion
				if pair.value().obj() is not None:
					member_list.pop(0) # Remove found member
					# And search deeper
					return self.resolve_member_value_from_obj(pair.value().obj(), member_list)
				else:
					return None

	def find_assignment_element(self, name):
		name_parts = name.split(DOT)

		if len(name_parts) < 1:
			return None

		# Check if have an assignment that is an exact match
		e = self.elements.get(name) # self.nacl_state.elements.get(name)
		if e is not None:
			return e
			# if e.ctx.value().obj() is not None:
			#	return self.resolve_member_value_from_obj(e.ctx.value().obj(), orig_name)
			# return self.transpile(e.ctx.value())
		else:
			# Remove last part (after DOT) to see if an element exists with this name
			name_parts = name_parts[:-1]
			name = ".".join(name_parts)
			return self.find_assignment_element(name)

	def resolve_member_value_from_element(self, element, member_list, ctx):
		# Find the value indicated by member_list

		# member_list f.ex. ["e1", "e1-2", "e1-3"]
		# loop through first time and find e1 (level 1)
		# then recursion where the e1 (first level) has been popped

		if element.base_type == BASE_TYPE_FUNCTION:
			exit_NaCl(ctx, "A function (" + element.name + ") does not have any named attributes")

		if element.base_type == BASE_TYPE_UNTYPED_INIT:
			val = element.get_member_value(member_list, ctx)
			if val is None:
				exit_NaCl(ctx, "Could not identify " + element.name + "." + ".".join(member_list))

			if not isinstance(val, dict):
				return val # The value has been resolved inside the Untyped element's process method

			# if isinstance(val, dict):
			# 	exit_NaCl(ctx, "Error (" + element.name + "): This feature is not supported yet: " + element.name + "." + ".".join(member_list))
			# Have another way of resolving the value for now: Continue with the function:

		if element.base_type == BASE_TYPE_UNTYPED_INIT or element.base_type == BASE_TYPE_TYPED_INIT:
			value = element.ctx.value()
			found_val = None

			if value.obj() is not None:
				# TODO?: Could be replaced by get_member_value in Element class

				found_val = self.resolve_member_value_from_obj(value.obj(), list(member_list))

				if found_val is not None:
					return found_val

			assignment_value_name = element.name + "." + ".".join(member_list)

			e = self.find_assignment_element(assignment_value_name)
			if e is None:
				exit_NaCl(ctx, "Could not identify " + element.name + "." + ".".join(member_list))
			else:
				if e.ctx.value().obj() is not None:
					# Remove the name of the e element to get only the name of the member left
					member = assignment_value_name.replace(e.name + ".", "")

					found_val = self.resolve_member_value_from_obj(e.ctx.value().obj(), [ member ])
					if found_val is not None:
						return found_val
					else:
						exit_NaCl(ctx, "Could not identify " + element.name + "." + ".".join(member_list))

				return self.transpile(e.ctx.value())

		exit_NaCl(ctx, "No support for handling element of base type " + element.base_type)

	def transpile_numeric_value(self, numeric_value):
		if numeric_value.ipv4_addr() is not None:
			return self.transpile_ip4_addr(numeric_value.ipv4_addr())

		if numeric_value.integer() is not None or \
		numeric_value.decimal() is not None:
			return numeric_value.getText()

		exit_NaCl(numeric_value, "Undefined numeric value " + numeric_value.getText())

	# ---- Helper functions ----

	def get_pckt_name(self, subtype):
		return pckt_names[subtype.lower()]

	def get_access_op(self, subtype):
		if subtype.lower() != IP:
			return DOT
		else:
			return ARROW

	def get_pckt_cast(self, subtype, ctx):
		subtype_lower = subtype.lower()
		if subtype_lower == IP:
			return "" # Already have (IP) pckt as input to Filter's operator() method

		pckt_name = pckt_names.get(subtype_lower)

		if pckt_name is not None:
			if pckt_name != ICMP_PCKT:
				return AUTO + INCLUDEOS_REFERENCE_OP + " " + pckt_name + " = " + self.get_cast(subtype_lower, IP_PCKT, ctx)
			else:
				return AUTO + " " + pckt_name + " = " + self.get_cast(subtype_lower, IP_PCKT, ctx)
		else:
			exit_NaCl(ctx, "Invalid subtype " + subtype + ", or pckt name or cpp pckt name not found")

	def get_cast(self, cast_to_proto, pckt_name, ctx):
		proto = cast_to_proto.lower()
		if proto not in cpp_pckt_classes:
			exit_NaCl(ctx, "Invalid protocol " + cast_to_proto)

		cpp_pckt_class = cpp_pckt_classes[proto]

		if proto != ICMP and pckt_name != ICMP_PCKT:
			return "static_cast<" + cpp_pckt_class + INCLUDEOS_REFERENCE_OP + ">(" + INCLUDEOS_DEREFERENCE_OP + pckt_name + ");"
		else:
			return INCLUDEOS_ICMP_PCKT_CLASS + "(std::move(" + IP_PCKT + "));"

	def get_cout_convert_to_type(self, val_ctx):
		if val_ctx.value_name() is None:
			exit_NaCl(val_ctx, "This value can not be printed")

		name_parts = val_ctx.value_name().getText().split(DOT)
		name = name_parts[0]

		if len(name_parts) == 1:
			exit_NaCl(val_ctx, "This value can not be printed")

		if name.lower() not in proto_objects:
			exit_NaCl(val_ctx, name + " is not a valid protocol")

		name_parts.pop(0)
		properties = name_parts
		if len(properties) > 1:
			exit_NaCl(val_ctx, "Undefined protocol object properties: " + val_ctx.value_name().getText())

		return proto_objects[name.lower()].get_cout_convert_to_type_cpp(properties[0].lower(), val_ctx)

	def transpile_ip4_addr(self, ip_addr_ctx):
		parts = ip_addr_ctx.Number() # list
		part0 = parts[0].getText()
		part1 = parts[1].getText()
		part2 = parts[2].getText()
		part3 = parts[3].getText()

		if int(part0) > BYTE_LIMIT or int(part1) > BYTE_LIMIT or int(part2) > BYTE_LIMIT or int(part3) > BYTE_LIMIT:
			exit_NaCl(ip_addr_ctx, "IPv4 addr " + ip_addr_ctx.getText() + " contains bytes greater than " + str(BYTE_LIMIT))

		return INCLUDEOS_IP4_ADDR_CLASS + "{" + ip_addr_ctx.getText().replace(".", ",") + "}"

	def transpile_ip4_cidr(self, ip_cidr_ctx):
		parts = ip_cidr_ctx.ipv4_addr().Number() # list
		part0 = parts[0].getText()
		part1 = parts[1].getText()
		part2 = parts[2].getText()
		part3 = parts[3].getText()

		if int(part0) > BYTE_LIMIT or int(part1) > BYTE_LIMIT or int(part2) > BYTE_LIMIT or int(part3) > BYTE_LIMIT:
			exit_NaCl(ip_cidr_ctx, "IPv4 cidr " + ip_cidr_ctx.getText() + " contains bytes greater than " + str(BYTE_LIMIT))

		mask = ip_cidr_ctx.cidr_mask().integer().getText()

		if int(mask) > MASK_LIMIT:
			exit_NaCl(ip_cidr_ctx, "IPv4 cidr mask in " + ip_cidr_ctx.getText() + " is greater than " + str(MASK_LIMIT))

		return INCLUDEOS_IP4_CIDR_CLASS + "{" + part0 + "," + part1 + "," + part2 + "," + part3 + "," + mask + "}"

	# ---- < Helper functions ----

# < Cpp_value_transpiler

def init(nacl_state):
    # print "Init value_transpiler: Cpp_value_transpiler"
    nacl_state.register_subtranspiler(VALUE_TRANSPILER, Cpp_value_transpiler(nacl_state.elements))
