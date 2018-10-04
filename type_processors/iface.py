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
# To avoid: <...>/NaCl/type_processors/iface.py:1: RuntimeWarning: Parent module '<...>/NaCl/type_processors' not found while handling absolute import

from NaCl import exit_NaCl, NaCl_exception, Typed, BASE_TYPE_TYPED_INIT, BASE_TYPE_FUNCTION, DOT
from shared import *
# TYPE_IFACE, TYPE_NAT, TEMPLATE_KEY_IFACE_PUSHES, TEMPLATE_KEY_ENABLE_CT_IFACES, TEMPLATE_KEY_HAS_NATS,
# TRUE, FALSE

# -------------------- CONSTANTS Iface --------------------

# Moved to shared.py: TYPE_IFACE = "iface"

# Iface keys

IFACE_KEY_ADDRESS 		= "address"
IFACE_KEY_NETMASK 		= "netmask"
IFACE_KEY_GATEWAY		= "gateway"
IFACE_KEY_DNS 			= "dns"
IFACE_KEY_INDEX 		= "index"
# IFACE_KEY_VLAN 		= "vlan" 	# Moved to shared.py
IFACE_KEY_MASQUERADE 	= "masquerade"
IFACE_KEY_CONFIG 		= "config"
IFACE_KEY_SEND_QUEUE_LIMIT = "send_queue_limit"
IFACE_KEY_BUFFER_LIMIT = "buffer_limit"

IFACE_KEY_PREROUTING 	= "prerouting"
IFACE_KEY_INPUT 		= "input"
IFACE_KEY_OUTPUT 		= "output"
IFACE_KEY_POSTROUTING 	= "postrouting"

CHAIN_NAMES = [
	IFACE_KEY_PREROUTING,
	IFACE_KEY_INPUT,
	IFACE_KEY_OUTPUT,
	IFACE_KEY_POSTROUTING
]

PREDEFINED_IFACE_KEYS = [
	IFACE_KEY_ADDRESS,
	IFACE_KEY_NETMASK,
	IFACE_KEY_GATEWAY,
	IFACE_KEY_DNS,
	IFACE_KEY_INDEX,
	IFACE_KEY_VLAN,
	IFACE_KEY_MASQUERADE,
	IFACE_KEY_CONFIG,
	IFACE_KEY_SEND_QUEUE_LIMIT,
	IFACE_KEY_BUFFER_LIMIT
]
PREDEFINED_IFACE_KEYS.extend(CHAIN_NAMES)

DHCP_CONFIG 			= "dhcp"
DHCP_FALLBACK_CONFIG 	= "dhcp-with-fallback"
STATIC_CONFIG 			= "static"

PREDEFINED_CONFIG_TYPES = [
	DHCP_CONFIG,
	DHCP_FALLBACK_CONFIG,
	STATIC_CONFIG
]

# -------------------- TEMPLATE KEYS (pystache) --------------------

TEMPLATE_KEY_IFACES 					= "ifaces"
# Moved to shared.py: TEMPLATE_KEY_IFACE_PUSHES = "pushes_iface"
TEMPLATE_KEY_AUTO_NATTING_IFACES 		= "auto_natting_ifaces"
TEMPLATE_KEY_MASQUERADES 				= "masquerades"

# Moved to shared.py: TEMPLATE_KEY_ENABLE_CT_IFACES = "enable_ct_ifaces"

TEMPLATE_KEY_HAS_AUTO_NATTING_IFACES 	= "has_auto_natting_ifaces"
TEMPLATE_KEY_HAS_VLANS 					= "has_vlans"
TEMPLATE_KEY_HAS_MASQUERADES 			= "has_masquerades"
TEMPLATE_KEY_IS_VLAN 					= "is_vlan"
TEMPLATE_KEY_VLAN_INDEX_IS_MAC_STRING 	= "vlan_index_is_mac_string"

TEMPLATE_KEY_CONFIG_IS_DHCP 			= "config_is_dhcp"
TEMPLATE_KEY_CONFIG_IS_DHCP_FALLBACK 	= "config_is_dhcp_fallback"
TEMPLATE_KEY_CONFIG_IS_STATIC 			= "config_is_static"

TEMPLATE_KEY_INDEX 						= "index"
TEMPLATE_KEY_ADDRESS 					= "address"
TEMPLATE_KEY_NETMASK 					= "netmask"
TEMPLATE_KEY_GATEWAY 					= "gateway"
TEMPLATE_KEY_DNS 						= "dns"
TEMPLATE_KEY_VLAN 						= "vlan"
TEMPLATE_KEY_SEND_QUEUE_LIMIT 			= "send_queue_limit"
TEMPLATE_KEY_BUFFER_LIMIT 				= "buffer_limit"

TEMPLATE_KEY_IFACE_INDEX 				= "iface_index"

TEMPLATE_KEY_VLAN_IFACES 				= "vlan_ifaces"

# Helper function

def is_int(input):
	try:
		int(input)
	except ValueError:
		return False
	return True

# -------------------- Iface --------------------

class Iface(Typed):
	def __init__(self, nacl_state, idx, name, ctx, base_type, type_t):
		super(Iface, self).__init__(nacl_state, idx, name, ctx, base_type, type_t)

		self.handle_as_untyped = False

		self.config_is_dhcp 			= False
		self.config_is_dhcp_fallback 	= False
		self.config_is_static 			= False

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

	# Overriding
	def validate_key(self, key):
		key_lower = key.lower()
		if key_lower not in PREDEFINED_IFACE_KEYS:
			raise NaCl_exception("Invalid Iface member " + key)

	# Overriding
	def add_member(self, key, value):
		if key in CHAIN_NAMES:
			self.process_push(key, value)
		else:
			super(Iface, self).add_member(key, value) # self.members[key] = pair_value

	# Overriding
	def add_not_obj_value(self, value_ctx):
		if value_ctx.value_name() is not None:
			# configuration type (dhcp, dhcp-with-fallback, static)
			config = value_ctx.value_name().getText().lower()
			if config in PREDEFINED_CONFIG_TYPES:
				self.members[IFACE_KEY_CONFIG] = value_ctx
			else:
				raise NaCl_exception("Invalid Iface value " + value_ctx.value_name().getText())
		else:
			raise NaCl_exception("An Iface has to contain key value pairs, or be set to a configuration type (" + \
				", ".join(PREDEFINED_CONFIG_TYPES) + ")")

	def process_push(self, chain, value_ctx):
		if self.chains.get(chain) is not None:
			exit_NaCl(value_ctx, "Iface chain " + chain + " has already been set")

		functions = []
		if value_ctx.list_t() is not None:
			# More than one function pushed onto chain
			for list_value in value_ctx.list_t().value_list().value():
				if list_value.value_name() is None:
					exit_NaCl(list_value, "This is not supported: " + value_ctx.getText())
				functions.append(list_value.value_name())
		elif value_ctx.value_name() is not None:
			# Only one function pushed onto chain
			functions = [ value_ctx.value_name() ]
		else:
			exit_NaCl(value_ctx, "This is not supported: " + value_ctx.getText())

		self.chains[chain] = chain # Mark as set
		self.add_push(chain, functions)

	def validate_members(self):
		if self.members.get(IFACE_KEY_INDEX) is None:
			exit_NaCl(self.ctx.value(), "An index needs to be specified for all Ifaces")

		config = self.members.get(IFACE_KEY_CONFIG)
		if config is not None and (config.value_name() is None or config.value_name().getText().lower() not in PREDEFINED_CONFIG_TYPES):
			exit_NaCl(config, "Invalid config value " + config.getText())

		vlan = self.members.get(IFACE_KEY_VLAN)
		# If this is a vlan, require a network configuration:
		if vlan is not None:
			if (config is None or config.value_name().getText().lower() != DHCP_CONFIG) and \
				(self.members.get(IFACE_KEY_ADDRESS) is None or \
				self.members.get(IFACE_KEY_NETMASK) is None):
				exit_NaCl(self.ctx.value(), "The members " + IFACE_KEY_ADDRESS + " and " + IFACE_KEY_NETMASK + \
					" must be set for every Iface if the Iface configuration hasn't been set to " + DHCP_CONFIG)
			elif config is not None and config.value_name().getText().lower() == DHCP_CONFIG and \
				(self.members.get(IFACE_KEY_ADDRESS) is not None or \
				self.members.get(IFACE_KEY_NETMASK) is not None or \
				self.members.get(IFACE_KEY_GATEWAY) is not None or \
				self.members.get(IFACE_KEY_DNS) is not None):
				exit_NaCl(config.value_name(), "An Iface with config set to dhcp should not specify " + IFACE_KEY_ADDRESS + \
					", " + IFACE_KEY_NETMASK + ", " + IFACE_KEY_GATEWAY + " or " + IFACE_KEY_DNS)

			# It is not allowed (yet) to set buffer_limit or send_queue_limit on a vlan
			if self.members.get(IFACE_KEY_BUFFER_LIMIT) is not None or self.members.get(IFACE_KEY_SEND_QUEUE_LIMIT) is not None:
				exit_NaCl(self.ctx.value(), "The members send_queue_limit and buffer_limit can not be set on an Iface that is a vlan")

		# Else we allow an Iface (not vlan) to be configured without network
		# (f.ex. if the user wants to set buffer_limit or send_queue_limit on an Iface without having to configure it)

	def process_members(self):
		# Loop through self.members and transpile the values
		for key, member in self.members.iteritems():
			if key != IFACE_KEY_CONFIG and key != IFACE_KEY_MASQUERADE:
				self.members[key] = self.nacl_state.transpile_value(member)

				# Validate that an Iface with this Iface's index has not already been defined
				if key == IFACE_KEY_INDEX:
					for key, el in self.nacl_state.elements.iteritems():
						if isinstance(el, Iface) and key != self.name:
							el_idx = el.members.get(IFACE_KEY_INDEX)
							el_vlan = el.members.get(IFACE_KEY_VLAN)
							# If another Iface has been defined with the same index and neither this nor that Iface is a vlan
							# (has a vlan member), display an error
							if el_idx is not None and el_idx == self.members.get(IFACE_KEY_INDEX) and el_vlan is None and self.members.get(IFACE_KEY_VLAN) is None:
								exit_NaCl(member, "Another Iface has been defined with index " + el_idx)
			elif key == IFACE_KEY_CONFIG:
				self.members[IFACE_KEY_CONFIG] = member.value_name().getText().lower()
			else:
				masq_val = self.nacl_state.transpile_value(member)

				if not isinstance(masq_val, basestring) or (masq_val.lower() != TRUE and masq_val.lower() != FALSE):
					exit_NaCl(member, "Invalid masquerade value. Must be set to true or false")

				if masq_val == TRUE:
					self.nacl_state.append_to_pystache_data_list(TEMPLATE_KEY_MASQUERADES, {
						TEMPLATE_KEY_IFACE: self.name
					})

		# Update config members
		config = self.members.get(IFACE_KEY_CONFIG)
		if config == DHCP_CONFIG:
			self.config_is_dhcp = True
		elif config == DHCP_FALLBACK_CONFIG:
			self.config_is_dhcp_fallback = True
		else:
			self.config_is_static = True

	def add_push(self, chain, functions):
		# chain: string with name of chain
		# functions: list containing value_name ctxs, where each name corresponds to the name of a NaCl function

		add_auto_natting = False
		function_names = []
		num_functions = len(functions)
		for i, function in enumerate(functions):
			name = function.getText()
			element = self.nacl_state.elements.get(name)
			if element is None or element.base_type != BASE_TYPE_FUNCTION:
				exit_NaCl(function, "No function with the name " + name + " exists")

			# If a Nat function is pushed onto an Iface's chain,
			# push the snat_translate lambda in cpp_template.mustache
			# onto the same Iface's postrouting chain
			# and push the dnat_translate lambda in cpp_template.mustache
			# onto the same Iface's prerouting chain
			if element.type_t.lower() == TYPE_NAT:
				add_auto_natting = True

			function_names.append({TEMPLATE_KEY_FUNCTION_NAME: name, TEMPLATE_KEY_COMMA: (i < (num_functions - 1))})

		if add_auto_natting:
			self.nacl_state.append_to_pystache_data_list(TEMPLATE_KEY_AUTO_NATTING_IFACES, {
				TEMPLATE_KEY_IFACE: self.name
			})

		self.nacl_state.append_to_pystache_data_list(TEMPLATE_KEY_IFACE_PUSHES, {
			TEMPLATE_KEY_NAME:				self.name,
			TEMPLATE_KEY_CHAIN: 			chain,
			TEMPLATE_KEY_FUNCTION_NAMES: 	function_names
		})

	def add_iface(self):
		# Append iface object to pystache ifaces list

		# Is this Iface a vlan or not
		is_vlan = False
		vlan_index_is_mac_string = False
		if self.members.get(IFACE_KEY_VLAN) is not None:
			is_vlan = True

			# Set vlan_index_is_mac_string to True if the index is a string
			# and not a number (but only necessary for an Iface that is a vlan)
			index = self.members.get(IFACE_KEY_INDEX)
			if not is_int(index):
				vlan_index_is_mac_string = True

			# Also add this Iface to the pystache data list TEMPLATE_KEY_VLAN_IFACES to be able to find
			# out (in final_registration) whether to #include relevant headers or not in mustache
			self.nacl_state.append_to_pystache_data_list(TEMPLATE_KEY_VLAN_IFACES, {
				TEMPLATE_KEY_IFACE: self.name,
			})

		# Create object containing key value pairs with the data we have collected
		# Append this object to the ifaces list
		# Is to be sent to pystache renderer in handle_input function
		self.nacl_state.append_to_pystache_data_list(TEMPLATE_KEY_IFACES, {
			TEMPLATE_KEY_NAME: 		self.name,
			TEMPLATE_KEY_TITLE: 	self.name.title(),
			TEMPLATE_KEY_VLAN_INDEX_IS_MAC_STRING: vlan_index_is_mac_string,
			TEMPLATE_KEY_INDEX: 	self.members.get(IFACE_KEY_INDEX),
			TEMPLATE_KEY_IS_VLAN: 	is_vlan,
			TEMPLATE_KEY_VLAN: 		self.members.get(IFACE_KEY_VLAN),

			TEMPLATE_KEY_CONFIG_IS_STATIC: 			self.config_is_static,
			TEMPLATE_KEY_CONFIG_IS_DHCP: 			self.config_is_dhcp,
			TEMPLATE_KEY_CONFIG_IS_DHCP_FALLBACK: 	self.config_is_dhcp_fallback,

			TEMPLATE_KEY_ADDRESS: 	self.members.get(IFACE_KEY_ADDRESS),
			TEMPLATE_KEY_NETMASK:	self.members.get(IFACE_KEY_NETMASK),
			TEMPLATE_KEY_GATEWAY: 	self.members.get(IFACE_KEY_GATEWAY),
			TEMPLATE_KEY_DNS: 		self.members.get(IFACE_KEY_DNS),
			TEMPLATE_KEY_SEND_QUEUE_LIMIT: self.members.get(IFACE_KEY_SEND_QUEUE_LIMIT),
			TEMPLATE_KEY_BUFFER_LIMIT: self.members.get(IFACE_KEY_BUFFER_LIMIT)
		})

	def enable_ct(self):
		# Add this Iface's name to enable_ct_ifaces pystache list if it is not in the list already
		if not self.nacl_state.exists_in_pystache_list(TEMPLATE_KEY_ENABLE_CT_IFACES, TEMPLATE_KEY_IFACE, self.name):
			for chain in CHAIN_NAMES:
				if self.chains.get(chain) is not None:
					self.nacl_state.append_to_pystache_data_list(TEMPLATE_KEY_ENABLE_CT_IFACES, {
						TEMPLATE_KEY_IFACE: self.name
					})
					return # Only one entry in enable_ct_ifaces list for each Iface

	# Overriding
	def process_assignment(self, element_key):
		element = self.nacl_state.elements.get(element_key)

		name_parts = element_key.split(DOT)
		orig_member = name_parts[1]
		member = orig_member.lower()

		if len(name_parts) != 2:
			exit_NaCl(element.ctx, "Invalid " + self.get_class_name() + " member " + element.name)

		try:
			self.validate_key(orig_member)
		except NaCl_exception as e:
			exit_NaCl(element.ctx, e.value)

		if self.members.get(member) is not None:
			exit_NaCl(element.ctx, "Member " + member + " has already been set")

		found_element_value = element.ctx.value()
		try:
			self.add_member(member, found_element_value)
		except NaCl_exception as e:
			exit_NaCl(element.ctx, e.value)

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

		return self.res

	# Called from handle_input (NaCl.py) right before rendering, after the NaCl file has been processed
	# Register the last data here that can not be registered before this (set has-values f.ex.)
	@staticmethod
	def final_registration(nacl_state):
		if not nacl_state.pystache_list_is_empty(TEMPLATE_KEY_AUTO_NATTING_IFACES):
			nacl_state.register_pystache_data_object(TEMPLATE_KEY_HAS_AUTO_NATTING_IFACES, True)

		if not nacl_state.pystache_list_is_empty(TEMPLATE_KEY_VLAN_IFACES):
			nacl_state.register_pystache_data_object(TEMPLATE_KEY_HAS_VLANS, True)

		if not nacl_state.pystache_list_is_empty(TEMPLATE_KEY_MASQUERADES):
			nacl_state.register_pystache_data_object(TEMPLATE_KEY_HAS_MASQUERADES, True)
			nacl_state.register_pystache_data_object(TEMPLATE_KEY_HAS_NATS, True)

# < class Iface

# -------------------- INIT --------------------

# Dictionary of lists in NaCl_state
# pystache_data{}
# pystache_data[TEMPLATE_KEY] = []

def create_iface_pystache_lists(nacl_state):
	nacl_state.create_pystache_data_lists([ \
		TEMPLATE_KEY_IFACES, \
		TEMPLATE_KEY_AUTO_NATTING_IFACES, \
		TEMPLATE_KEY_IFACE_PUSHES, \
		TEMPLATE_KEY_VLAN_IFACES, \
		TEMPLATE_KEY_MASQUERADES, \
		TEMPLATE_KEY_ENABLE_CT_IFACES
		# TEMPLATE_KEY_HAS_MASQUERADES, \
		# TEMPLATE_KEY_HAS_AUTO_NATTING_IFACES, \
		# TEMPLATE_KEY_HAS_VLANS \
		# These three are added in the final_registration method
	])

def init(nacl_state):
	# print "Init iface: Iface"
	nacl_state.add_type_processor(TYPE_IFACE, Iface)
	create_iface_pystache_lists(nacl_state)
