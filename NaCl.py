#! /usr/bin/env python

# This file is a part of the IncludeOS unikernel - www.includeos.org
#
# Copyright 2017 IncludeOS AS, Oslo, Norway
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

from antlr4 import *
from NaClLexer import *
from NaClParser import *
from NaClVisitor import *
import sys
import os

import pystache
from cpp_template import *

# antlr4 -Dlanguage=Python2 NaCl.g4 -visitor

LANGUAGE = CPP # CPP is defined in shared_constants.py, imported in cpp_template.py

# Pystache keys
TEMPLATE_KEY_IFACES 			= "ifaces"
TEMPLATE_KEY_IFACES_WITH_VLANS	= "ifaces_with_vlans"
TEMPLATE_KEY_FILTERS 			= "filters"
TEMPLATE_KEY_NATS 				= "nats"
TEMPLATE_KEY_REWRITES 			= "rewrites"
TEMPLATE_KEY_PUSHES 			= "pushes"
TEMPLATE_KEY_GATEWAYS 			= "gateways"
TEMPLATE_KEY_CONNTRACKS 		= "conntracks"
TEMPLATE_KEY_LOAD_BALANCERS 	= "load_balancers"
TEMPLATE_KEY_IP_FORWARD_IFACES 	= "ip_forward_ifaces"
TEMPLATE_KEY_ENABLE_CT_IFACES 	= "enable_ct_ifaces"
TEMPLATE_KEY_MASQUERADES 		= "masquerades"
TEMPLATE_KEY_AUTO_NATTING_IFACES = "auto_natting_ifaces"

TEMPLATE_KEY_HAS_GATEWAYS 		= "has_gateways"
TEMPLATE_KEY_HAS_NATS 			= "has_nats"
TEMPLATE_KEY_HAS_MASQUERADES 	= "has_masquerades"
TEMPLATE_KEY_HAS_VLANS 			= "has_vlans"
TEMPLATE_KEY_HAS_AUTO_NATTING_IFACES = "has_auto_natting_ifaces"
TEMPLATE_KEY_HAS_FUNCTIONS 		= "has_functions"
TEMPLATE_KEY_HAS_LOAD_BALANCERS = "has_load_balancers"

TEMPLATE_KEY_ENABLE_CT 			= "enable_ct"

# Data to be sent to pystache renderer
# Each list are to contain objects consisting of key value pairs
ifaces 				= []
ifaces_with_vlans 	= []
filters 			= []
rewrites 			= []
nats 				= []
pushes 				= []
gateways 			= []
conntracks 			= []
load_balancers 		= []
ip_forward_ifaces 	= []
enable_ct_ifaces 	= []
masquerades 		= []
auto_natting_ifaces = []

gateway_exists 		= False
conntrack_exists 	= False

TEMPLATE_KEY_FUNCTION_NAME 	= "function_name"
TEMPLATE_KEY_COMMA 			= "comma"
TEMPLATE_KEY_IFACE 			= "iface"
TEMPLATE_KEY_CHAIN 			= "chain"
TEMPLATE_KEY_FUNCTION_NAMES = "function_names"
TEMPLATE_KEY_NAME 			= "name"
TEMPLATE_KEY_TITLE 			= "title"
TEMPLATE_KEY_CONFIG_IS_DHCP 			= "config_is_dhcp"
TEMPLATE_KEY_CONFIG_IS_DHCP_FALLBACK 	= "config_is_dhcp_fallback"
TEMPLATE_KEY_CONFIG_IS_STATIC 			= "config_is_static"
TEMPLATE_KEY_INDEX 			= "index"
TEMPLATE_KEY_ADDRESS 		= "address"
TEMPLATE_KEY_NETMASK 		= "netmask"
TEMPLATE_KEY_GATEWAY 		= "gateway"
TEMPLATE_KEY_DNS 			= "dns"
TEMPLATE_KEY_ROUTES 		= "routes"
TEMPLATE_KEY_CONTENT		= "content"
TEMPLATE_KEY_IFACE_INDEX 	= "iface_index"
TEMPLATE_KEY_VLANS 			= "vlans"
TEMPLATE_KEY_IS_GATEWAY_PUSH = "is_gateway_push"

TEMPLATE_KEY_LB_LAYER 				= "layer"
TEMPLATE_KEY_LB_ALGORITHM 			= "algorithm"
TEMPLATE_KEY_LB_WAIT_QUEUE_LIMIT 	= "wait_queue_limit"
TEMPLATE_KEY_LB_SESSION_LIMIT 		= "session_limit"
TEMPLATE_KEY_LB_PORT 				= "port"
TEMPLATE_KEY_LB_CLIENTS_IFACE 		= "clients_iface_name"
TEMPLATE_KEY_LB_SERVERS_IFACE 		= "servers_iface_name"
TEMPLATE_KEY_LB_POOL 				= "pool"
TEMPLATE_KEY_LB_NODE_ADDRESS 		= TEMPLATE_KEY_ADDRESS
TEMPLATE_KEY_LB_NODE_PORT 			= TEMPLATE_KEY_LB_PORT

TEMPLATE_KEY_CONNTRACK_TIMEOUTS 	= "timeouts"
TEMPLATE_KEY_CONNTRACK_TYPE 		= "type"

def transpile_function(language, type_t, subtype, ctx):
	if language == CPP:
		return transpile_function_cpp(type_t, subtype, ctx)

def resolve_value(language, ctx):
	if language == CPP:
		return resolve_value_cpp(ctx)

def get_router_name(language):
	if language == CPP:
		return INCLUDEOS_ROUTER_OBJ_NAME

# -------------------- Element --------------------

class Element(object):
	def __init__(self, idx, name, ctx, base_type):
		self.idx 		= idx
		self.name 		= name
		self.ctx 		= ctx
		self.base_type 	= base_type
		self.res 		= None

		# Use res
		# self.values 	= None # Resolved all the element's values so can be used
		            	       # when transpiling comparisons inside functions

		# Fill members dictionary if this is a top element with a value of type obj
		self.members = {}

	def process(self):
		sys.exit("line " + get_line_and_column(self.ctx) + " Internal error: Subclass of class Element has not implemented the process method")

	def get_class_name(self):
		return self.__class__.__name__

	def process_ctx(self):
		# Handle the Element's value ctx object: Fill self.members dictionary
		# Note: Gateway has its own process_ctx method

		value = self.ctx.value() if hasattr(self.ctx, 'value') else self.ctx
		class_name = self.get_class_name()
		is_iface = isinstance(self, Iface)
		is_vlan = isinstance(self, Vlan)

		# Using Untyped methods (placed in Element) since depth is more than 1 level deep
		if isinstance(self, Load_balancer) or isinstance(self, Conntrack):
			if value.obj() is None:
				sys.exit("line " + get_line_and_column(value) + " A " + class_name + " must be an object")
			self.process_obj(self.members, value.obj())
			return

		if value.obj() is not None:
			for pair in value.obj().key_value_list().key_value_pair():
				orig_key 	= pair.key().getText()
				key 		= orig_key.lower()
				pair_value 	= pair.value()

				if (is_iface and key not in predefined_iface_keys) or \
					(is_vlan and key not in predefined_vlan_keys):
					sys.exit("line " + get_line_and_column(pair.key()) + " Invalid " + class_name + \
						" member " + orig_key)

				if self.members.get(key) is not None:
					sys.exit("line " + get_line_and_column(pair.key()) + " " + class_name + " member " + key + " has already been set")

				if is_iface and key in chains:
					self.process_push(key, pair.value())
				else:
					self.members[key] = pair_value
		elif is_iface and value.value_name() is not None:
			# configuration type (dhcp, dhcp-with-fallback, static)
			config = value.value_name().getText().lower()
			if config in predefined_config_types:
				self.members[IFACE_KEY_CONFIG] = value
			else:
				sys.exit("line " + get_line_and_column(value) + " Invalid Iface value " + value.value_name().getText())
		else:
			if is_iface:
				sys.exit("line " + get_line_and_column(value) + " An Iface has to contain key value pairs, or be set to a configuration type (" + \
					", ".join(predefined_config_types) + ")")
			else:
				sys.exit("line " + get_line_and_column(value) + " A " + class_name + " has to contain key value pairs")

	def process_assignments(self):
		# Loop through elements that are assignments
		# Find assignments (f.ex. x.y: <value> or x.y.z: <value>) that refers to this Element

		class_name = self.get_class_name()
		is_lb_untyped_or_conntrack = isinstance(self, Untyped) or isinstance(self, Load_balancer) or \
			isinstance(self, Conntrack)
		is_gateway = isinstance(self, Gateway)

		# Handle assignments in the order of number of name parts to facilitate that you can have two assignments
		# where one is creating a member with an object as a value, while the other adds another element (key and value)
		# to that members object

		# Get the keys of all the assignment elements that manipulates this Element's members
		# If the name of the assignment element (= dictionary key) starts with the name of this Element and a DOT,
		# we know we have to do with an assignment element that manipulates this Element
		assignments_to_process = [key for key in elements if key.startswith(self.name + DOT)]

		if len(assignments_to_process) > 1:
			# Sorting the list based on length of element.name of each assignment element (shortest first)
			assignments_to_process = sorted(assignments_to_process, key=lambda k: len(k.split(DOT)))

		for key in assignments_to_process:
			element = elements.get(key)

			if is_lb_untyped_or_conntrack:
				self.process_assignment(element)
			elif is_gateway:
				self.process_gateway_assignment(element)
			else:
				name_parts = key.split(DOT)
				orig_member = name_parts[1]
				member = orig_member.lower()

				if len(name_parts) != 2:
					sys.exit("line " + get_line_and_column(element.ctx) + " Invalid " + class_name + " member " + element.name)

				if (isinstance(self, Iface) and member not in predefined_iface_keys) or \
					(isinstance(self, Vlan) and member not in predefined_vlan_keys) or \
					(isinstance(self, Conntrack) and member not in predefined_conntrack_keys):
					sys.exit("line " + get_line_and_column(element.ctx) + " Invalid " + class_name + " member " + orig_member)

				if self.members.get(member) is not None:
					sys.exit("line " + get_line_and_column(element.ctx) + " Member " + member + " has already been set")

				found_element_value = element.ctx.value()
				if isinstance(self, Iface) and member in chains:
					self.process_push(member, found_element_value)
				else:
					if self.members.get(member) is None:
						self.members[member] = found_element_value
					else:
						sys.exit("line " + get_line_and_column(element.ctx) + " " + class_name + " member " + member + " has already been set")

	# ---------- Methods related to dictionary self.members for Untyped and Load_balancer ----------

	def process_assignment(self, element):
		# Could be either Untyped, Load_balancer or Conntrack

		# Remove first part (the name of this element)
		assignment_name_parts = element.name.split(DOT)
		assignment_name_parts.pop(0)

		# Check if this key has already been set in this element
		# In that case: Error: Value already set
		if self.get_dictionary_val(self.members, list(assignment_name_parts), element.ctx) is not None:
			sys.exit("line " + get_line_and_column(element.ctx) + " Member " + element.name + " has already been set")
		else:
			# Add to members dictionary
			num_name_parts = len(assignment_name_parts)
			parent_key = "" if len(assignment_name_parts) < 2 else assignment_name_parts[num_name_parts - 2]

			self.add_dictionary_val(self.members, assignment_name_parts, element.ctx.value(), num_name_parts, parent_key)

	# Called when resolving values
	def get_member_value(self, key_list, error_ctx):
		self.process() # Make sure this element has been processed (self.res is not None)
		return self.get_dictionary_val(self.members, key_list, error_ctx)

	def get_dictionary_val(self, dictionary, key_list, error_ctx):
		level_key = key_list[0]

		# End of recursion condition
		if len(key_list) == 1:
			return dictionary.get(level_key)

		if level_key not in dictionary:
			return None

		# Recursion
		for key in dictionary:
			if key == level_key:
				new_dict = dictionary.get(key)
				if new_dict is None or not isinstance(new_dict, dict):
					line_and_column = "1:0" if error_ctx is None else get_line_and_column(error_ctx)
					sys.exit("line " + line_and_column + " " + level_key + "." + key_list[1] + " does not exist")

				key_list.pop(0) # Remove first key (level_key) - has been found
				return self.get_dictionary_val(new_dict, key_list, error_ctx)

	def add_dictionary_val(self, dictionary, key_list, value, level=1, parent_key=""):
		is_lb = isinstance(self, Load_balancer)
		is_conntrack = isinstance(self, Conntrack)
		level_key = key_list[0] if not is_lb and not is_conntrack else key_list[0].lower()

		# End of recursion condition
		if len(key_list) == 1:
			if value.obj() is not None:
				# Then the value is a new dictionary
				dictionary[level_key] = {} # Create new dictionary
				return self.process_obj(dictionary[level_key], value.obj(), (level + 1), level_key)
			else:
				if is_lb:
					self.validate_lb_key(level_key, parent_key, level, value) # sys.exit on error
					self.resolve_lb_value(dictionary, level_key, value)
				elif is_conntrack:
					self.validate_conntrack_key(level_key, parent_key, level, value) # sys.exit on error
					self.resolve_conntrack_value(dictionary, level_key, value)
				else:
					dictionary[level_key] = resolve_value(LANGUAGE, value)
				return

		if level_key not in dictionary:
			sys.exit("line " + get_line_and_column(value) + " Trying to add to a member (" + level_key + ") that doesn't exist")

		for key in dictionary:
			if key == level_key:
				key_list.pop(0) # Remove first key (level_key) - has been found
				return self.add_dictionary_val(dictionary[key], key_list, value, level, level_key)

	def process_obj(self, dictionary, ctx, level=1, parent_key=""):
		# Could be either Untyped, Load_balancer or Conntrack
		# Level only relevant for Load_balancer and Conntrack

		is_lb = isinstance(self, Load_balancer)
		is_conntrack = isinstance(self, Conntrack)

		for pair in ctx.key_value_list().key_value_pair():
			key = pair.key().getText() if not is_lb and not is_conntrack else pair.key().getText().lower()

			if dictionary.get(key) is not None:
				sys.exit("line " + get_line_and_column(pair.key()) + " Member " + key + " has already been set")

			# Validate key
			if is_lb:
				self.validate_lb_key(key, parent_key, level, pair.key()) # sys.exit on error
			elif is_conntrack:
				self.validate_conntrack_key(key, parent_key, level, pair.key()) # sys.exit on error

			# End of recursion:
			if pair.value().obj() is None:
				if is_lb:
					self.resolve_lb_value(dictionary, key, pair.value())
				elif is_conntrack:
					self.resolve_conntrack_value(dictionary, key, pair.value())
				else:
					dictionary[key] = resolve_value(LANGUAGE, pair.value())
			else:
				# Recursion:
				# Then we have an obj inside an obj
				dictionary[key] = {} # creating new dictionary
				# loop through the obj and fill the new dictionary
				self.process_obj(dictionary[key], pair.value().obj(), (level + 1), key)

# < Element

# -------------------- Untyped --------------------

class Untyped(Element):
	def __init__(self, idx, name, ctx, base_type):
		super(Untyped, self).__init__(idx, name, ctx, base_type)

	# Main processing method
	def process(self):
		if self.res is None:
			name_parts = self.name.split(DOT)

			if len(name_parts) > 1:
				# This is an assignment to an already existing element
				element_name = name_parts[0]
				if elements.get(element_name) is None:
					sys.exit("line " + get_line_and_column(self.ctx) + " No element with the name " + element_name + " exists")
			else:
				if self.ctx.value().obj() is not None:
					# Then this element is an obj and other assignments can add to this element
					# We need to validate that no other assignments are overwriting one of the element's
					# values:

					self.process_obj(self.members, self.ctx.value().obj())
					self.process_assignments()

			self.res = self.members

		return self.res

# < Untyped

# -------------------- Typed --------------------

class Typed(Element):
	def __init__(self, idx, name, ctx, base_type, type_t):
		super(Typed, self).__init__(idx, name, ctx, base_type)
		self.type_t = type_t

# < Typed

# -------------------- Conntrack --------------------

class Conntrack(Typed):
	def __init__(self, idx, name, ctx, base_type, type_t):
		super(Conntrack, self).__init__(idx, name, ctx, base_type, type_t)

	def add_conntrack(self):
		timeout = self.members.get(CONNTRACK_KEY_TIMEOUT)
		timeouts = []

		if timeout is not None:
			class_name = self.get_class_name()

			if not isinstance(timeout, dict):
				sys.exit("line " + get_line_and_column(self.ctx) + " Invalid " + CONNTRACK_KEY_TIMEOUT + \
					" value of " + class_name + " (needs to be an object)")

			for conntrack_type in timeout:
				t = timeout.get(conntrack_type)

				if not isinstance(t, dict):
					sys.exit("line " + get_line_and_column(self.ctx) + " Invalid " + conntrack_type + \
						" value of " + class_name + " (needs to be an object)")

				tcp_timeout = t.get(TCP)
				udp_timeout = t.get(UDP)
				icmp_timeout = t.get(ICMP)

				timeouts.append({
					TEMPLATE_KEY_CONNTRACK_TYPE: conntrack_type,
					TCP: tcp_timeout,
					UDP: udp_timeout,
					ICMP: icmp_timeout
				})

		conntracks.append({
			TEMPLATE_KEY_NAME: 					self.name,
			CONNTRACK_KEY_LIMIT: 				self.members.get(CONNTRACK_KEY_LIMIT),
			CONNTRACK_KEY_RESERVE: 				self.members.get(CONNTRACK_KEY_RESERVE),
			TEMPLATE_KEY_CONNTRACK_TIMEOUTS: 	timeouts
		})

	# Called in Element
	def validate_conntrack_key(self, key, parent_key, level, ctx):
		class_name = self.get_class_name()

		if level == 1:
			if key not in predefined_conntrack_keys:
				sys.exit("line " + get_line_and_column(ctx) + " Invalid " + class_name + " member " + key)
			return

		if parent_key == "":
			sys.exit("line " + get_line_and_column(ctx) + " Internal error: Parent key of " + key + " has not been given")

		if level == 2:
			if parent_key == CONNTRACK_KEY_TIMEOUT and key not in predefined_conntrack_timeout_keys:
				sys.exit("line " + get_line_and_column(ctx) + " Invalid " + class_name + " member " + key + " in " + self.name + "." + parent_key)
		elif level == 3:
			if parent_key not in predefined_conntrack_timeout_keys:
				sys.exit("line " + get_line_and_column(ctx) + " Internal error: Invalid parent key " + parent_key + " of " + key)
			if key not in predefined_conntrack_timeout_inner_keys:
				sys.exit("line " + get_line_and_column(ctx) + " Invalid " + class_name + " member " + key)
		else:
			sys.exit("line " + get_line_and_column(ctx) + " Invalid " + class_name + " member " + key)

	# Called in Element
	def resolve_conntrack_value(self, dictionary, key, value):
		# Add found value
		dictionary[key] = resolve_value(LANGUAGE, value)

	# Main processing method
	def process(self):
		if self.res is None:
			# Then process

			self.process_ctx()
			self.process_assignments()
			self.add_conntrack()

			self.res = self.members
			# Or:
			# self.res = resolve_value(LANGUAGE, ...)

		return self.res

# < Conntrack

# -------------------- Iface --------------------

class Iface(Typed):
	def __init__(self, idx, name, ctx, base_type, type_t):
		super(Iface, self).__init__(idx, name, ctx, base_type, type_t)

		self.config_is_dhcp = False
		self.config_is_dhcp_fallback = False
		self.config_is_static = False

		self.chains = {}	# To handle setting of a chain multiple times in the same Iface
		                	# Should not be handled as the ctx objects in self.members

		# Iface keys/members:
		# address
		# netmask
		# gateway
		# dns
		# index
		# vlan
		# config
		# masquerade
		# prerouting
		# input
		# forward
		# output
		# postrouting

	def process_push(self, chain, value_ctx):
		if self.chains.get(chain) is not None:
			sys.exit("line " + get_line_and_column(value_ctx) + " Iface chain " + chain + " has already been set")

		functions = []
		if value_ctx.list_t() is not None:
			# More than one function pushed onto chain
			for list_value in value_ctx.list_t().value_list().value():
				if list_value.value_name() is None:
					sys.exit("line " + get_line_and_column(list_value) + " This is not supported: " + value_ctx.getText())
				functions.append(list_value.value_name())
		elif value_ctx.value_name() is not None:
			# Only one function pushed onto chain
			functions = [ value_ctx.value_name() ]
		else:
			sys.exit("line " + get_line_and_column(value_ctx) + " This is not supported: " + value_ctx.getText())

		self.chains[chain] = chain # Mark as set
		self.add_push(chain, functions)

	def validate_members(self):
		if self.members.get(IFACE_KEY_INDEX) is None:
			sys.exit("line " + get_line_and_column(self.ctx.value()) + " An index needs to be specified for all Ifaces")

		config = self.members.get(IFACE_KEY_CONFIG)
		if config is not None and (config.value_name() is None or config.value_name().getText().lower() not in predefined_config_types):
			sys.exit("line " + get_line_and_column(config) + " Invalid config value " + config.getText())

		if (config is None or config.value_name().getText().lower() != DHCP_CONFIG) and \
			(self.members.get(IFACE_KEY_ADDRESS) is None or \
				self.members.get(IFACE_KEY_NETMASK) is None):
			sys.exit("line " + get_line_and_column(self.ctx.value()) + " The members " + IFACE_KEY_ADDRESS + " and " + IFACE_KEY_NETMASK + \
				" must be set for every Iface if the Iface configuration hasn't been set to " + DHCP_CONFIG)
		elif config is not None and config.value_name().getText().lower() == DHCP_CONFIG and \
			(self.members.get(IFACE_KEY_ADDRESS) is not None or \
				self.members.get(IFACE_KEY_NETMASK) is not None or \
				self.members.get(IFACE_KEY_GATEWAY) is not None or \
				self.members.get(IFACE_KEY_DNS) is not None):
			sys.exit("line " + get_line_and_column(config.value_name()) + " An Iface with config set to dhcp should not specify " + IFACE_KEY_ADDRESS + \
				", " + IFACE_KEY_NETMASK + ", " + IFACE_KEY_GATEWAY + " or " + IFACE_KEY_DNS)

	def is_vlan(self, element):
		if element is None or not hasattr(element, 'type_t') or element.type_t.lower() != TYPE_VLAN:
			return False
		return True

	def process_members(self):
		# Vlans
		vlans = []
		if self.members.get(IFACE_KEY_VLAN) is not None:
			vlan_ctx = self.members.get(IFACE_KEY_VLAN)

			if vlan_ctx.obj() is not None:
				# Add each Vlan in obj to the vlans list
				# Each element in the obj needs to be a valid Vlan
				for pair in vlan_ctx.obj().key_value_list().key_value_pair():
					# Key: Name of Vlan
					# Value: Actual Vlan object/value (containing address, netmask, gateway, index)
					vlan_element = Vlan(0, pair.key().getText(), pair.value(), BASE_TYPE_TYPED_INIT, TYPE_VLAN)
					vlans.append(vlan_element)
			elif vlan_ctx.list_t() is not None:
				# Add each Vlan in list_t to the vlans list
				# Each element in the list_t needs to be a valid Vlan
				for i, v in enumerate(vlan_ctx.list_t().value_list().value()):
					vlan_element = None

					if v.value_name() is not None:
						vlan_name = v.value_name().getText()
						vlan_element = elements.get(vlan_name)
						if not self.is_vlan(vlan_element):
							sys.exit("line " + get_line_and_column(v.value_name()) + " Undefined Vlan " + vlan_name)
					elif v.obj() is not None:
						vlan_element = Vlan(0, "", v, BASE_TYPE_TYPED_INIT, TYPE_VLAN)
					else:
						sys.exit("line " + get_line_and_column(v) + " A Vlan list must either contain Vlan objects (key value pairs) or names of Vlans")

					vlans.append(vlan_element)
			elif vlan_ctx.value_name() is not None:
				vlan_name = vlan_ctx.value_name().getText()
				vlan_element = elements.get(vlan_name)
				if not self.is_vlan(vlan_element):
					sys.exit("line " + get_line_and_column(vlan_ctx.value_name()) + " Undefined Vlan " + vlan_name)
				vlans.append(vlan_element)
			else:
				sys.exit("line " + get_line_and_column(vlan_ctx) + " An Iface's vlan needs to be a list of Vlans")

		# Loop through self.members and resolve the values
		for key, member in self.members.iteritems():
			if key != IFACE_KEY_CONFIG and key != IFACE_KEY_MASQUERADE:
				self.members[key] = resolve_value(LANGUAGE, member)

				# Validate that an Iface with this Iface's index has not already been defined
				if key == IFACE_KEY_INDEX:
					for key, el in elements.iteritems():
						if isinstance(el, Iface) and key != self.name:
							el_idx = el.members.get(IFACE_KEY_INDEX)
							if el_idx is not None and el_idx == self.members.get(IFACE_KEY_INDEX):
								sys.exit("line " + get_line_and_column(member) + " Another Iface has been defined with index " + el_idx)
			elif key == IFACE_KEY_CONFIG:
				self.members[IFACE_KEY_CONFIG] = member.value_name().getText().lower()
			else:
				masq_val = resolve_value(LANGUAGE, member)

				if not isinstance(masq_val, basestring) or (masq_val.lower() != TRUE and masq_val.lower() != FALSE):
					sys.exit("line " + get_line_and_column(member) + " Invalid masquerade value. Must be set to true or false")

				if masq_val == TRUE:
					masquerades.append({TEMPLATE_KEY_IFACE: self.name})

		# Update config members
		config = self.members.get(IFACE_KEY_CONFIG)
		if config == DHCP_CONFIG:
			self.config_is_dhcp = True
		elif config == DHCP_FALLBACK_CONFIG:
			self.config_is_dhcp_fallback = True
		else:
			self.config_is_static = True

		if len(vlans) > 0:
			# Process and add vlans found
			self.add_iface_vlans(vlans)

	def add_push(self, chain, functions):
		# chain: string with name of chain
		# functions: list containing value_name ctxs, where each name corresponds to the name of a NaCl function

		add_auto_natting = False
		function_names = []
		num_functions = len(functions)
		for i, function in enumerate(functions):
			name = function.getText()
			element = elements.get(name)
			if element is None or element.base_type != BASE_TYPE_FUNCTION:
				sys.exit("line " + get_line_and_column(function) + " No function with the name " + name + " exists")

			# If a Nat function is pushed onto an Iface's chain,
			# push the snat_translate lambda in cpp_template.mustache
			# onto the same Iface's postrouting chain
			# and push the dnat_translate lambda in cpp_template.mustache
			# onto the same Iface's prerouting chain
			if element.type_t.lower() == TYPE_NAT:
				add_auto_natting = True

			function_names.append({TEMPLATE_KEY_FUNCTION_NAME: name, TEMPLATE_KEY_COMMA: (i < (num_functions - 1))})

		if add_auto_natting:
			auto_natting_ifaces.append({ TEMPLATE_KEY_IFACE: self.name })

		pushes.append({
			TEMPLATE_KEY_NAME:				self.name,
			TEMPLATE_KEY_CHAIN: 			chain,
			TEMPLATE_KEY_FUNCTION_NAMES: 	function_names
		})

	def add_iface_vlans(self, vlans):
		# Called once per Iface

		pystache_vlans = []
		for vlan in vlans:
			vlan.process() # Make sure the Vlan has been processed

			gateway = vlan.members.get(VLAN_KEY_GATEWAY)
			if gateway is None:
				gateway = self.members.get(IFACE_KEY_GATEWAY)

			pystache_vlans.append({
				TEMPLATE_KEY_INDEX: 	vlan.members.get(VLAN_KEY_INDEX),
				TEMPLATE_KEY_ADDRESS: 	vlan.members.get(VLAN_KEY_ADDRESS),
				TEMPLATE_KEY_NETMASK: 	vlan.members.get(VLAN_KEY_NETMASK),
				TEMPLATE_KEY_GATEWAY: 	gateway
			})

		ifaces_with_vlans.append({
			TEMPLATE_KEY_IFACE: 		self.name,
			TEMPLATE_KEY_IFACE_INDEX: 	self.members.get(IFACE_KEY_INDEX),
			TEMPLATE_KEY_VLANS: 		pystache_vlans
		})

	def add_iface(self):
		# Append iface object to pystache ifaces list

		# Create object containing key value pairs with the data we have collected
		# Append this object to the ifaces list
		# Is to be sent to pystache renderer in handle_input function
		ifaces.append({
			TEMPLATE_KEY_NAME: 		self.name,
			TEMPLATE_KEY_TITLE: 	self.name.title(),
			TEMPLATE_KEY_INDEX: 	self.members.get(IFACE_KEY_INDEX),

			TEMPLATE_KEY_CONFIG_IS_STATIC: 			self.config_is_static,
			TEMPLATE_KEY_CONFIG_IS_DHCP: 			self.config_is_dhcp,
			TEMPLATE_KEY_CONFIG_IS_DHCP_FALLBACK: 	self.config_is_dhcp_fallback,

			TEMPLATE_KEY_ADDRESS: 	self.members.get(IFACE_KEY_ADDRESS),
			TEMPLATE_KEY_NETMASK:	self.members.get(IFACE_KEY_NETMASK),
			TEMPLATE_KEY_GATEWAY: 	self.members.get(IFACE_KEY_GATEWAY),
			TEMPLATE_KEY_DNS: 		self.members.get(IFACE_KEY_DNS)
		})

	def enable_ct(self):
		# Add this Iface's name to enable_ct_ifaces pystache list if it is not in the list already
		if not any(enable_ct_iface[TEMPLATE_KEY_IFACE] == self.name for enable_ct_iface in enable_ct_ifaces):
			for chain in chains:
				if self.chains.get(chain) is not None:
					enable_ct_ifaces.append({TEMPLATE_KEY_IFACE: self.name})
					return # Only one entry in enable_ct_ifaces list for each Iface

	# Main processing method
	def process(self):
		if self.res is None:
			# Then process

			self.process_ctx()
			self.process_assignments()
			self.validate_members()
			self.process_members()
			self.add_iface()
			self.enable_ct()

			self.res = self.members
			# Or:
			# self.res = resolve_value(LANGUAGE, ...)

		return self.res

# < Iface

# -------------------- Vlan --------------------

class Vlan(Typed):
	def __init__(self, idx, name, ctx, base_type, type_t):
		super(Vlan, self).__init__(idx, name, ctx, base_type, type_t)

		# Vlan keys/members:
		# address
		# netmask
		# gateway
		# index

	def validate_members(self):
		if self.members.get(VLAN_KEY_INDEX) is None or self.members.get(VLAN_KEY_ADDRESS) is None or \
			self.members.get(VLAN_KEY_NETMASK) is None:
			sys.exit("line " + get_line_and_column(self.ctx) + " The members index, address and netmask must be set for every Vlan")

	def process_members(self):
		# Transpile values
		for key, member in self.members.iteritems():
			self.members[key] = resolve_value(LANGUAGE, member)

	# Main processing method
	def process(self):
		if self.res is None:
			# Then process

			self.process_ctx()
			self.process_assignments()
			self.validate_members()
			self.process_members()

			self.res = self.members
			# Or:
			# self.res = resolve_value(LANGUAGE, ...)

		return self.res

# < Vlan

# -------------------- Gateway --------------------

class Gateway(Typed):
	def __init__(self, idx, name, ctx, base_type, type_t):
		super(Gateway, self).__init__(idx, name, ctx, base_type, type_t)

		# self.members (in Element) to contain this Gateway's members as defined in NaCl file
		# Key: Name of route
		# Value: pystache route object

		self.not_route_members = {}

	def get_pystache_route_obj(self, name, route_ctx):
		route_obj = { "ctx": route_ctx }
		pairs = route_ctx.key_value_list().key_value_pair()
		num_pairs = len(pairs)

		for pair in pairs:
			orig_key = pair.key().getText()
			key = orig_key.lower()

			if route_obj.get(key) is not None:
				sys.exit("line " + get_line_and_column(pair.key()) + " Member " + key + \
					" has already been set for route " + name)

			if key not in predefined_gateway_route_keys:
				sys.exit("line " + get_line_and_column(pair.key()) + " " + orig_key + " is not a valid Gateway route member. " + \
					"Valid members are: " + ", ".join(predefined_gateway_route_keys))

			if key != GATEWAY_KEY_IFACE:
				route_obj[key] = resolve_value(LANGUAGE, pair.value())
			else:
				# Then the Iface element's name is to be added to the route_obj,
				# not the resolved Iface
				iface_name = pair.value().getText()

				if pair.value().value_name() is None:
					sys.exit("line " + get_line_and_column(pair.value()) + " Gateway route member iface contains an invalid value (" + iface_name + ")")

				element = elements.get(iface_name)
				if element is None or (hasattr(element, 'type_t') and element.type_t.lower() != TYPE_IFACE):
					sys.exit("line " + get_line_and_column(pair.value()) + " No Iface with the name " + iface_name + " exists")

				route_obj[key] = iface_name

		return route_obj

	def process_ctx(self):
		# Handle the Element's value ctx object: Fill self.members dictionary

		value = self.ctx.value()

		if value.obj() is not None:
			for route_pair in value.obj().key_value_list().key_value_pair():
				orig_name = route_pair.key().getText()
				name = orig_name.lower()

				if route_pair.value().obj() is None and name not in predefined_gateway_keys:
					sys.exit("line " + get_line_and_column(route_pair) + " Invalid Gateway member " + orig_name)

				if name == GATEWAY_KEY_SEND_TIME_EXCEEDED or name == GATEWAY_KEY_FORWARD:
					if self.not_route_members.get(name) is not None:
						sys.exit("line " + get_line_and_column(route_pair) + " " + name + " has already been set")
					self.not_route_members[name] = route_pair.value()
					continue

				if self.members.get(name) is not None:
					sys.exit("line " + get_line_and_column(route_pair) + " Route " + name + " has already been set")

				if route_pair.value().obj() is None:
					sys.exit("line " + get_line_and_column(route_pair.value()) + " A Gateway's routes must be objects (" + \
						"containing key value pairs)")

				# Add pystache route obj to members dictionary
				self.members[name] = self.get_pystache_route_obj(name, route_pair.value().obj())
		elif value.list_t() is not None:
			for i, val in enumerate(value.list_t().value_list().value()):
				if val.obj() is None:
					sys.exit("line " + get_line_and_column(val) + " A Gateway that constitutes a list must be a list of " + \
						"objects (containing key value pairs)")

				# Add pystache route obj to members dictionary
				# When unnamed routes, use index as key
				self.members[i] = self.get_pystache_route_obj(str(i), val.obj())
		else:
			sys.exit("line " + get_line_and_column(value) + " A Gateway must contain key value pairs (in which " + \
				"each pair's value is an object), or it must contain a list of objects")

	# Called in Element's process_assignments method
	def process_gateway_assignment(self, element):
		name_parts = element.name.split(DOT)
		orig_member = name_parts[1]
		member = orig_member.lower()
		num_name_parts = len(name_parts)

		if num_name_parts > 3:
			sys.exit("line " + get_line_and_column(element.ctx) + " Invalid Gateway member " + element.name)
		elif self.members.get(0) is not None:
			sys.exit("line " + get_line_and_column(element.ctx) + " Trying to access a named member in a Gateway without named members (" + element.name + ")")
			# Could support later: gateway.0.netmask: 255.255.255.0

		if num_name_parts == 2:
			# members:
			if member != GATEWAY_KEY_SEND_TIME_EXCEEDED and member != GATEWAY_KEY_FORWARD:
				# Then the user is adding an additional route to this Gateway
				# F.ex. gateway.r6: <value>
				if self.members.get(member) is None:
					# Then add the route if valid
					if element.ctx.value().obj() is None:
						sys.exit("line " + get_line_and_column(element.ctx.value()) + " A Gateway member's value needs to contain key value pairs")
					self.members[member] = self.get_pystache_route_obj(element.name, element.ctx.value().obj())
				else:
					sys.exit("line " + get_line_and_column(element.ctx) + " Gateway member " + member + " has already been set")
			# not_route_members:
			else:
				if self.not_route_members.get(member) is None:
					self.not_route_members[member] = element.ctx.value()
				else:
					sys.exit("line " + get_line_and_column(element.ctx.value()) + " Gateway member " + member + " has already been set")
		else:
			# Then num_name_parts are 3 and we're talking about adding a member to a route
			route = self.members.get(member)
			if route is None:
				sys.exit("line " + get_line_and_column(element.ctx) + " No member named " + member + " in Gateway " + self.name)

			route_member = name_parts[2].lower()

			if route.get(route_member) is not None:
				sys.exit("line " + get_line_and_column(element.ctx) + " Member " + route_member + " in route " + member + \
					" has already been set")

			if route_member not in predefined_gateway_route_keys:
				sys.exit("line " + get_line_and_column(element.ctx) + " " + route_member + " is not a valid Gateway route member. " + \
					"Valid members are: " + ", ".join(predefined_gateway_route_keys))

			if route_member != GATEWAY_KEY_IFACE:
				route[route_member] = resolve_value(LANGUAGE, element.ctx.value())
			else:
				# Then the Iface element's name is to be added to the route obj,
				# not the resolved Iface
				iface_name = element.ctx.value().getText()

				if element.ctx.value().value_name() is None:
					sys.exit("line " + get_line_and_column(element.ctx.value()) + " Invalid iface value " + \
						iface_name + " (the value must be the name of an Iface)")

				iface_element = elements.get(iface_name)
				if iface_element is None or (hasattr(iface_element, 'type_t') and iface_element.type_t.lower() != TYPE_IFACE):
					sys.exit("line " + get_line_and_column(element.ctx.value()) + " No Iface with the name " + iface_name + " exists")

				route[route_member] = iface_name

	def process_push(self, chain, value_ctx):
		functions = []
		if value_ctx.list_t() is not None:
			# More than one function pushed onto chain
			for list_value in value_ctx.list_t().value_list().value():
				if list_value.value_name() is None:
					sys.exit("line " + get_line_and_column(list_value) + " This is not supported: " + value_ctx.getText())
				functions.append(list_value.value_name())
		elif value_ctx.value_name() is not None:
			# Only one function pushed onto chain
			functions = [ value_ctx.value_name() ]
		else:
			sys.exit("line " + get_line_and_column(value_ctx) + " This is not supported: " + value_ctx.getText())

		self.add_push(chain, functions)

	def add_push(self, chain, functions):
		# chain: string with name of chain
		# functions: list containing value_name ctxs, where each name corresponds to the name of a NaCl function

		function_names = []
		num_functions = len(functions)
		for i, function in enumerate(functions):
			name = function.getText()
			element = elements.get(name)
			if element is None or element.base_type != BASE_TYPE_FUNCTION:
				sys.exit("line " + get_line_and_column(function) + " No function with the name " + name + " exists")

			if element.type_t.lower() == TYPE_NAT:
				sys.exit("line " + get_line_and_column(function) + " A Nat function cannot be pushed onto a Gateway's forward chain")

			function_names.append({TEMPLATE_KEY_FUNCTION_NAME: name, TEMPLATE_KEY_COMMA: (i < (num_functions - 1))})

		pushes.append({
			TEMPLATE_KEY_IS_GATEWAY_PUSH: 	True,
			TEMPLATE_KEY_NAME:				get_router_name(LANGUAGE),
			TEMPLATE_KEY_CHAIN: 			chain,
			TEMPLATE_KEY_FUNCTION_NAMES: 	function_names
		})

	def validate_and_process_not_route_members(self):
		for key, value_ctx in self.not_route_members.iteritems():
			if key == GATEWAY_KEY_SEND_TIME_EXCEEDED:
				resolved_value = resolve_value(LANGUAGE, value_ctx)
				self.not_route_members[key] = resolved_value

				if resolved_value != TRUE and resolved_value != FALSE:
					sys.exit("line " + get_line_and_column(value_ctx) + " Invalid value of " + key + \
						" (" + resolved_value + "). Must be set to " + TRUE + " or " + FALSE)
			elif key == GATEWAY_KEY_FORWARD:
				self.process_push(key, value_ctx)

	def process_members(self):
		routes = []
		index = 0
		num_routes = len(self.members)
		for i, route in self.members.iteritems():
			if GATEWAY_KEY_NETMASK not in route or \
				GATEWAY_KEY_IFACE not in route or \
				(GATEWAY_KEY_NET not in route and GATEWAY_KEY_HOST not in route):
				sys.exit("line " + get_line_and_column(route.get("ctx")) + " A Gateway route must specify " + \
					GATEWAY_KEY_IFACE + ", " + GATEWAY_KEY_NETMASK + " and either " + GATEWAY_KEY_NET + " or " + GATEWAY_KEY_HOST)

			# Add iface_name to ip_forward_ifaces pystache list if it is not in the
			# list already
			iface_name = route.get(GATEWAY_KEY_IFACE)
			if iface_name is not None and not any(ip_forward_iface[TEMPLATE_KEY_IFACE] == iface_name for ip_forward_iface in ip_forward_ifaces):
				ip_forward_ifaces.append({TEMPLATE_KEY_IFACE: iface_name})

			# Add iface_name to enable_ct_ifaces pystache list if it is not in the
			# list already
			if iface_name is not None and not any(enable_ct_iface[TEMPLATE_KEY_IFACE] == iface_name for enable_ct_iface in enable_ct_ifaces):
				enable_ct_ifaces.append({TEMPLATE_KEY_IFACE: iface_name})

			route[TEMPLATE_KEY_COMMA] = (index < (num_routes - 1))
			index += 1

			routes.append(route)
			# routes.append({
			#	'host': ,
			#	'net': ,
			#	'netmask': ,
			#	'nexthop': ,
			#	'iface': ,
			#	'cost':
			# })

		self.add_gateway(routes)

	def add_gateway(self, routes):
		send_time_exceeded = ""
		resolved_value = self.not_route_members.get(GATEWAY_KEY_SEND_TIME_EXCEEDED)
		if resolved_value is not None:
			if resolved_value == TRUE:
				send_time_exceeded = TRUE
			else:
				send_time_exceeded = FALSE

		# Create object containing key value pairs with the data we have collected
		# Append this object to the gateways list
		# Is to be sent to pystache renderer in handle_input function
		gateways.append({
			TEMPLATE_KEY_NAME: self.name,
			TEMPLATE_KEY_ROUTES: routes,
			GATEWAY_KEY_SEND_TIME_EXCEEDED: send_time_exceeded
		})

	# Main processing method
	def process(self):
		if self.res is None:
			# Then process:

			self.process_ctx()
			self.process_assignments()
			self.validate_and_process_not_route_members()
			self.process_members()

			self.res = self.members # Indicating that this element (Gateway) has been processed
			# Or:
			# self.res = resolve_value(LANGUAGE, ...)

		return self.res

# < Gateway

# -------------------- Load_balancer --------------------

class Load_balancer(Typed):
	def __init__(self, idx, name, ctx, base_type, type_t):
		super(Load_balancer, self).__init__(idx, name, ctx, base_type, type_t)

	def add_load_balancer(self):
		# Note: This method also validates that all the mandatory fields have been set
		# Note: The value has already been validated in process_ctx and process_assignments
		# Note: Only allowed to create one Load_balancer per layer

		layer = self.members.get(LB_KEY_LAYER)
		if layer is None:
			sys.exit("line " + get_line_and_column(self.ctx) + " Load_balancer member " + LB_KEY_LAYER + " has not been set")
		if any(lb[TEMPLATE_KEY_LB_LAYER] == layer for lb in load_balancers):
			sys.exit("line " + get_line_and_column(self.ctx) + " A " + layer.upper() + " Load_balancer has already been defined")

		clients = self.members.get(LB_KEY_CLIENTS)
		if clients is None:
			sys.exit("line " + get_line_and_column(self.ctx) + " Load_balancer member " + LB_KEY_CLIENTS + " has not been set")
		if not isinstance(clients, dict):
			sys.exit("line " + get_line_and_column(self.ctx) + " Invalid value of Load_balancer member " + LB_KEY_CLIENTS + \
				". It needs to be an object containing " + ", ".join(predefined_lb_clients_keys))

		servers = self.members.get(LB_KEY_SERVERS)
		if servers is None:
			sys.exit("line " + get_line_and_column(self.ctx) + " Load_balancer member " + LB_KEY_SERVERS + " has not been set")
		if not isinstance(servers, dict):
			sys.exit("line " + get_line_and_column(self.ctx) + " Invalid value of Load_balancer member " + LB_KEY_SERVERS + \
				". It needs to be an object containing " + ", ".join(predefined_lb_servers_keys))

		# Clients

		clients_iface_name = clients.get(LB_KEY_IFACE)
		if clients_iface_name is None:
			sys.exit("line " + get_line_and_column(self.ctx) + " Load_balancer member " + LB_KEY_CLIENTS + "." + LB_KEY_IFACE + " has not been set")

		port = clients.get(LB_KEY_PORT)
		if port is None:
			sys.exit("line " + get_line_and_column(self.ctx) + " Load_balancer member " + LB_KEY_CLIENTS + "." + LB_KEY_PORT + " has not been set")

		waitq_limit = clients.get(LB_CLIENTS_KEY_WAIT_QUEUE_LIMIT)
		if waitq_limit is None:
			waitq_limit = 1000

		session_limit = clients.get(LB_CLIENTS_KEY_SESSION_LIMIT)
		if session_limit is None:
			session_limit = 1000

		# Servers

		servers_iface_name = servers.get(LB_KEY_IFACE)
		if servers_iface_name is None:
			sys.exit("line " + get_line_and_column(self.ctx) + " Load_balancer member " + LB_KEY_SERVERS + "." + LB_KEY_IFACE + " has not been set")

		algo = servers.get(LB_SERVERS_KEY_ALGORITHM)
		if algo is None:
			sys.exit("line " + get_line_and_column(self.ctx) + " Load_balancer member " + LB_KEY_SERVERS + "." + LB_SERVERS_KEY_ALGORITHM + " has not been set")

		# pool is a list of nodes/servers, containing address and port
		pool = servers.get(LB_SERVERS_KEY_POOL)
		if pool is None:
			sys.exit("line " + get_line_and_column(self.ctx) + " Load_balancer member " + LB_KEY_SERVERS + "." + LB_SERVERS_KEY_POOL + " has not been set")
		if not isinstance(pool, list):
			sys.exit("line " + get_line_and_column(self.ctx) + " Invalid value of Load_balancer member " + LB_KEY_SERVERS + "." + LB_SERVERS_KEY_POOL + \
				". It needs to be a list of objects containing " + ", ".join(predefined_lb_node_keys))

		pystache_pool = []
		for s in pool:
			pystache_pool.append({
				TEMPLATE_KEY_INDEX: 			s.get(TEMPLATE_KEY_INDEX),
				TEMPLATE_KEY_LB_NODE_ADDRESS: 	s.get(LB_NODE_KEY_ADDRESS),
				TEMPLATE_KEY_LB_NODE_PORT: 		s.get(LB_KEY_PORT)
			})

		load_balancers.append({
			TEMPLATE_KEY_NAME: 					self.name,
			TEMPLATE_KEY_LB_LAYER: 				layer,
			TEMPLATE_KEY_LB_ALGORITHM: 			algo,
			TEMPLATE_KEY_LB_WAIT_QUEUE_LIMIT: 	waitq_limit,
			TEMPLATE_KEY_LB_SESSION_LIMIT: 		session_limit,
			TEMPLATE_KEY_LB_PORT: 				port,
			TEMPLATE_KEY_LB_CLIENTS_IFACE: 		clients_iface_name,
			TEMPLATE_KEY_LB_SERVERS_IFACE: 		servers_iface_name,
			TEMPLATE_KEY_LB_POOL: 				pystache_pool
		})

	# Called in Element
	def validate_lb_key(self, key, parent_key, level, ctx):
		class_name = self.get_class_name()

		if level == 1:
			if key not in predefined_lb_keys:
				sys.exit("line " + get_line_and_column(ctx) + " Invalid " + class_name + " member " + key)
		elif level == 2:
			if parent_key == "":
				sys.exit("line " + get_line_and_column(ctx) + " Internal error: Parent key of " + key + " has not been given")
			if parent_key == LB_KEY_CLIENTS and key not in predefined_lb_clients_keys:
				sys.exit("line " + get_line_and_column(ctx) + " Invalid " + class_name + " member " + key + " in " + self.name + "." + parent_key)
			if parent_key == LB_KEY_SERVERS and key not in predefined_lb_servers_keys:
				sys.exit("line " + get_line_and_column(ctx) + " Invalid " + class_name + " member " + key + " in " + self.name + "." + parent_key)
		else:
			sys.exit("line " + get_line_and_column(ctx) + " Invalid " + class_name + " member " + key)

	# Called in Element
	def resolve_lb_value(self, dictionary, key, value):
		found_element_value = value.getText()

		if key == LB_KEY_LAYER or key == LB_SERVERS_KEY_ALGORITHM:
			found_element_value = found_element_value.lower()

		if key == LB_KEY_LAYER:
			if value.value_name() is None or found_element_value not in valid_lb_layers:
				sys.exit("line " + get_line_and_column(value) + " Invalid " + LB_KEY_LAYER + " value (" + value.getText() + ")")
		elif key == LB_KEY_IFACE:
			# Then the Iface element's name is to be added, not the resolved Iface
			if value.value_name() is None:
				sys.exit("line " + get_line_and_column(value) + " " + class_name + " member " + LB_KEY_IFACE + " contains an invalid value (" + \
					found_element_value + ")")
			element = elements.get(found_element_value)
			if element is None or (hasattr(element, 'type_t') and element.type_t.lower() != TYPE_IFACE):
				sys.exit("line " + get_line_and_column(value) + " No Iface with the name " + found_element_value + " exists")
		elif key == LB_SERVERS_KEY_ALGORITHM:
			if value.value_name() is None or found_element_value not in valid_lb_servers_algos:
				sys.exit("line " + get_line_and_column(value) + " Invalid algorithm " + value.getText())
		elif key == LB_SERVERS_KEY_POOL:
			if value.list_t() is None and value.value_name() is None:
				sys.exit("line " + get_line_and_column(value) + " Invalid " + LB_SERVERS_KEY_POOL + \
					" value. It needs to be a list of objects or the name of a list of objects containing " + \
					", ".join(predefined_lb_node_keys))

			if value.value_name() is not None:
				element_name = value.value_name().getText()
				e = elements.get(element_name)
				if e is None:
					sys.exit("line " + get_line_and_column(value) + " No element with the name " + element_name + " exists")
				if e.ctx.value().list_t() is None:
					sys.exit("line " + get_line_and_column(value) + " Element " + element_name + " does not consist of a list")
				value = e.ctx.value()

			pool = []
			for i, node in enumerate(value.list_t().value_list().value()):
				if node.obj() is None and node.value_name() is None:
					sys.exit("line " + get_line_and_column(node) + " Invalid " + LB_SERVERS_KEY_POOL + " value. It needs to be a list of objects containing " + \
						", ".join(predefined_lb_node_keys))

				if node.value_name() is not None:
					element_name = node.value_name().getText()
					e = elements.get(element_name)
					if e is None:
						sys.exit("line " + get_line_and_column(node) + " No element with the name " + element_name + " exists")
					if e.ctx.value().obj() is None:
						sys.exit("line " + get_line_and_column(node) + " Element " + element_name + " is not an object")
					node = e.ctx.value()

				n = {}
				n[TEMPLATE_KEY_INDEX] = i
				for pair in node.obj().key_value_list().key_value_pair():
					node_key = pair.key().getText().lower()
					if node_key not in predefined_lb_node_keys:
						sys.exit("line " + get_line_and_column(pair.key()) + " Invalid member in node " + str(i) + " in " + \
							LB_KEY_SERVERS + "." + LB_SERVERS_KEY_POOL)
					n[node_key] = resolve_value(LANGUAGE, pair.value())

				if n.get(LB_NODE_KEY_ADDRESS) is None or n.get(LB_KEY_PORT) is None:
					sys.exit("line " + get_line_and_column(node) + " An object in a " + LB_SERVERS_KEY_POOL + \
						" needs to specify " + ", ".join(predefined_lb_node_keys))

				pool.append(n)

			found_element_value = pool
		else:
			found_element_value = resolve_value(LANGUAGE, value)

		# Add found value
		dictionary[key] = found_element_value

	def process(self):
		if self.res is None:
			# Then process

			self.process_ctx()
			self.process_assignments()
			self.add_load_balancer()

			self.res = self.members
			# Or:
			# self.res = resolve_value(LANGUAGE, ...)

		return self.res

# < Load_balancer

# -------------------- Function --------------------

class Function(Element):
	def __init__(self, idx, name, ctx, base_type, type_t, subtype):
		super(Function, self).__init__(idx, name, ctx, base_type)
		self.type_t 	= type_t
		self.subtype 	= subtype

	def add_function(self):
		# Only if a function is mentioned in an assignment that is a push or
		# an Iface's chain, should it be added to filters/nats/rewrites pystache list

		pystache_function_obj = {
			TEMPLATE_KEY_NAME: 		self.name,
			TEMPLATE_KEY_TITLE: 	self.name.title(),
			TEMPLATE_KEY_CONTENT: 	self.res 	# Contains transpiled content
		}

		for p in pushes:
			for f in p[TEMPLATE_KEY_FUNCTION_NAMES]:
		 		if self.name == f[TEMPLATE_KEY_FUNCTION_NAME]:
		 			# Then we know that this function is called in the C++ code
		 			# And the function should be added to the correct pystache list
		 			type_t_lower = self.type_t.lower()

					# Display an error message if the function is a Filter and does not end in a default verdict
					if type_t_lower == TYPE_FILTER:
						if self.subtype.lower() != IP:
							sys.exit("line " + get_line_and_column(self.ctx) + " Only a function of subtype IP can be pushed onto an Iface's chain. " + \
								"However, you can create and call Filters of any subtype inside an IP Filter")

						elements = list(self.ctx.body().body_element())
						last_element = elements[len(elements) - 1]
						if last_element.action() is None or last_element.action().getText() not in valid_default_filter_verdicts:
							sys.exit("line " + get_line_and_column(self.ctx) + " Missing default verdict at the end of this Filter")

		 			if type_t_lower == TYPE_FILTER:
		 				filters.append(pystache_function_obj)
		 			elif type_t_lower == TYPE_NAT:
		 				nats.append(pystache_function_obj)
		 			elif type_t_lower == TYPE_REWRITE:
		 				rewrites.append(pystache_function_obj)
		 			else:
		 				sys.exit("line " + get_line_and_column(ctx.type_t()) + " Functions of type " + \
		 					self.type_t + " are not handled")
		 			return self.res

	# Main processing method
	def process(self):
		if self.res is None:
			self.res = transpile_function(LANGUAGE, self.type_t, self.subtype, self.ctx)
			self.add_function()
		return self.res

# < Function

# -------------------- 2. Process elements and write content to file --------------------

def handle_input():
	if LANGUAGE not in valid_languages:
		sys.exit("line 1:0 Internal error in handle_input: Cannot transpile to language " + LANGUAGE)

	# Process / transpile / fill the pystache lists
	function_elements = []

	for key, e in elements.iteritems():
		if e.base_type != BASE_TYPE_FUNCTION:
			e.process()
		else:
			function_elements.append(e)

	# Have processed all elements except function elements when arrive here
	for e in function_elements:
		e.process()

	data = {
		TEMPLATE_KEY_IFACES: 				ifaces,
		TEMPLATE_KEY_IFACES_WITH_VLANS: 	ifaces_with_vlans,
		TEMPLATE_KEY_CONNTRACKS: 			conntracks,
		TEMPLATE_KEY_LOAD_BALANCERS: 		load_balancers,
		TEMPLATE_KEY_FILTERS: 				filters,
		TEMPLATE_KEY_NATS: 					nats,
		TEMPLATE_KEY_REWRITES: 				rewrites,
		TEMPLATE_KEY_PUSHES: 				pushes,
		TEMPLATE_KEY_GATEWAYS: 				gateways, # or only one gateway?
		TEMPLATE_KEY_IP_FORWARD_IFACES:		ip_forward_ifaces,
		TEMPLATE_KEY_ENABLE_CT_IFACES:		enable_ct_ifaces,
		TEMPLATE_KEY_MASQUERADES: 			masquerades,
		TEMPLATE_KEY_AUTO_NATTING_IFACES: 	auto_natting_ifaces,
		TEMPLATE_KEY_HAS_GATEWAYS: 			(len(gateways) > 0),
		TEMPLATE_KEY_HAS_NATS: 				(len(nats) > 0 or len(masquerades) > 0),
		TEMPLATE_KEY_HAS_MASQUERADES:		(len(masquerades) > 0),
		TEMPLATE_KEY_HAS_VLANS: 			(len(ifaces_with_vlans) > 0),
		TEMPLATE_KEY_HAS_AUTO_NATTING_IFACES: (len(auto_natting_ifaces) > 0),
		TEMPLATE_KEY_HAS_FUNCTIONS: 		(len(nats) > 0 or len(filters) > 0),
		TEMPLATE_KEY_ENABLE_CT: 			(len(nats) > 0 or len(filters) > 0 or len(gateways) > 0),
		TEMPLATE_KEY_HAS_LOAD_BALANCERS: 	(len(load_balancers) > 0)
	}

	if LANGUAGE == CPP:
		content = pystache.Renderer().render(Cpp_template(), data)

		# Create the C++ file and write the content to the file
		file = None
		if len(sys.argv) > 1:
			file = open(os.path.expanduser(sys.argv[1]), "w")

		if file is not None:
			file.write(content)
	else:
		sys.exit("line 1:0 Internal error in handle_input: Transpilation to language " + LANGUAGE + " has not been implemented")

	print "Transpilation complete"

# -------------------- 1. Visiting --------------------

def save_element(base_type, ctx):
	if base_type != BASE_TYPE_TYPED_INIT and base_type != BASE_TYPE_UNTYPED_INIT and base_type != BASE_TYPE_FUNCTION:
		sys.exit("line " + get_line_and_column(ctx) + " NaCl elements of base type " + base_type + " are not handled")

	name_ctx = ctx.name() if base_type != BASE_TYPE_UNTYPED_INIT else ctx.value_name()
	if name_ctx is None:
		sys.exit("line " + get_line_and_column(ctx) + " Missing name of element")
	if name_ctx.getText() in elements:
		sys.exit("line " + get_line_and_column(name_ctx) + " Element " + name_ctx.getText() + " has already been defined")

	name = name_ctx.getText()
	idx = len(elements)

	# BASE_TYPE_UNTYPED_INIT

	if base_type == BASE_TYPE_UNTYPED_INIT:
		elements[name] = Untyped(idx, name, ctx, base_type)
		return

	type_t_ctx = ctx.type_t()
	type_t = type_t_ctx.getText()

	if type_t.lower() not in valid_nacl_types:
		sys.exit("line " + get_line_and_column(type_t_ctx) + " Undefined type " + type_t)

	# BASE_TYPE_FUNCTION

	if base_type == BASE_TYPE_FUNCTION:
		elements[name] = Function(idx, name, ctx, base_type, type_t, ctx.subtype().getText())
		return

	# BASE_TYPE_TYPED_INIT

	type_t_lower = type_t.lower()
	if type_t_lower == TYPE_IFACE:
		elements[name] = Iface(idx, name, ctx, base_type, type_t)
	elif type_t_lower == TYPE_VLAN:
		elements[name] = Vlan(idx, name, ctx, base_type, type_t)
	elif type_t_lower == TYPE_GATEWAY:
		global gateway_exists
		if gateway_exists:
			sys.exit("line " + get_line_and_column(type_t_ctx) + " A Gateway has already been defined")
		elements[name] = Gateway(idx, name, ctx, base_type, type_t)
		gateway_exists = True
	elif type_t_lower == TYPE_LOAD_BALANCER:
		elements[name] = Load_balancer(idx, name, ctx, base_type, type_t)
	elif type_t_lower == TYPE_CONNTRACK:
		global conntrack_exists
		if conntrack_exists:
			sys.exit("line " + get_line_and_column(type_t_ctx) + " A Conntrack has already been defined")
		if name.lower() == CT:
			sys.exit("line " + get_line_and_column(name_ctx) + " Invalid name (" + name + ") of Conntrack object")
		elements[name] = Conntrack(idx, name, ctx, base_type, type_t)
		conntrack_exists = True
	else:
		sys.exit("line " + get_line_and_column(type_t_ctx) + " NaCl elements of type " + type_t + " are not handled")

class NaClRecordingVisitor(NaClVisitor):

	def visitTyped_initializer(self, ctx):
		# Typed: Could indicate that C++ code is going to be created from this - depends on the
		# type_t specified (Iface, Gateway special)
		save_element(BASE_TYPE_TYPED_INIT, ctx)

	def visitInitializer(self, ctx):
		# Untyped: Means generally that no C++ code is going to be created from this - exists only in NaCl
		# Except: Assignments
		save_element(BASE_TYPE_UNTYPED_INIT, ctx)

	def visitFunction(self, ctx):
		save_element(BASE_TYPE_FUNCTION, ctx)

lexer = NaClLexer(StdinStream())
stream = CommonTokenStream(lexer)
parser = NaClParser(stream)
tree = parser.prog()
visitor = NaClRecordingVisitor()
visitor.visit(tree)

handle_input()
