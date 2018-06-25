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
IFACE_KEY_VLAN 			= "vlan"
IFACE_KEY_MASQUERADE 	= "masquerade"
IFACE_KEY_CONFIG 		= "config"

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
	IFACE_KEY_CONFIG
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

# -------------------- CONSTANTS Vlan --------------------

TYPE_VLAN 	= "vlan"

# Vlan keys

VLAN_KEY_ADDRESS 	= IFACE_KEY_ADDRESS
VLAN_KEY_NETMASK 	= IFACE_KEY_NETMASK
VLAN_KEY_GATEWAY 	= IFACE_KEY_GATEWAY
VLAN_KEY_DNS 		= IFACE_KEY_DNS
VLAN_KEY_INDEX 		= IFACE_KEY_INDEX

PREDEFINED_VLAN_KEYS = [
	VLAN_KEY_ADDRESS,
	VLAN_KEY_NETMASK,
	VLAN_KEY_GATEWAY,
	VLAN_KEY_INDEX
]

# -------------------- TEMPLATE KEYS (pystache) --------------------

# Template keys Vlan

TEMPLATE_KEY_VLANS 			= "vlans"

# Template keys Iface

TEMPLATE_KEY_IFACES 					= "ifaces"
TEMPLATE_KEY_IFACES_WITH_VLANS			= "ifaces_with_vlans"
# Moved to shared.py: TEMPLATE_KEY_IFACE_PUSHES = "pushes_iface"
TEMPLATE_KEY_AUTO_NATTING_IFACES 		= "auto_natting_ifaces"
TEMPLATE_KEY_MASQUERADES 				= "masquerades"

# Moved to shared.py: TEMPLATE_KEY_ENABLE_CT_IFACES = "enable_ct_ifaces"

TEMPLATE_KEY_HAS_AUTO_NATTING_IFACES 	= "has_auto_natting_ifaces"
TEMPLATE_KEY_HAS_VLANS 					= "has_vlans"
TEMPLATE_KEY_HAS_MASQUERADES 			= "has_masquerades"

TEMPLATE_KEY_CONFIG_IS_DHCP 			= "config_is_dhcp"
TEMPLATE_KEY_CONFIG_IS_DHCP_FALLBACK 	= "config_is_dhcp_fallback"
TEMPLATE_KEY_CONFIG_IS_STATIC 			= "config_is_static"

TEMPLATE_KEY_INDEX 						= "index"
TEMPLATE_KEY_ADDRESS 					= "address"
TEMPLATE_KEY_NETMASK 					= "netmask"
TEMPLATE_KEY_GATEWAY 					= "gateway"
TEMPLATE_KEY_DNS 						= "dns"

TEMPLATE_KEY_IFACE_INDEX 				= "iface_index"

# -------------------- CLASSES --------------------

# ---- class Common (base class to the below classes Vlan and Iface) ----

class Common(Typed):
	def __init__(self, nacl_state, idx, name, ctx, base_type, type_t):
		super(Common, self).__init__(nacl_state, idx, name, ctx, base_type, type_t)

	def process_assignment(self, element_key):
		# print "process assignment Common"

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

# < class Common

# ---- class Vlan ----

class Vlan(Common):
	def __init__(self, nacl_state, idx, name, ctx, base_type, type_t):
		super(Vlan, self).__init__(nacl_state, idx, name, ctx, base_type, type_t)

		self.handle_as_untyped = False

		# Vlan keys/members:
		# address
		# netmask
		# gateway
		# index

	# Overriding
	def validate_key(self, key):
		key_lower = key.lower()
		if key_lower not in PREDEFINED_VLAN_KEYS:
			raise NaCl_exception("Invalid Vlan member " + key)

	def validate_members(self):
		vlan_index = self.members.get(VLAN_KEY_INDEX)
		vlan_address = self.members.get(VLAN_KEY_ADDRESS)
		vlan_netmask = self.members.get(VLAN_KEY_NETMASK)

		if vlan_index is None or vlan_address is None or vlan_netmask is None:
			exit_NaCl(self.ctx, "The members index, address and netmask must be set for every Vlan")

		if vlan_index.obj() is not None or vlan_index.list_t() is not None:
			exit_NaCl(vlan_index, "The Vlan member " + VLAN_KEY_INDEX + " can not be an object")
		if vlan_address.obj() is not None or vlan_address.list_t() is not None:
			exit_NaCl(vlan_address, "The Vlan member " + VLAN_KEY_ADDRESS + " can not be an object")
		if vlan_netmask.obj() is not None or vlan_netmask.list_t() is not None:
			exit_NaCl(vlan_netmask, "The Vlan member " + VLAN_KEY_NETMASK + " can not be an object")

	def process_members(self):
		# Transpile values
		for key, member in self.members.iteritems():
			self.members[key] = self.nacl_state.transpile_value(member)

	# Main processing method
	def process(self):
		if self.res is None:
			# Then process

			self.process_ctx()
			self.process_assignments()
			self.validate_members()
			self.process_members()

			self.res = self.members

		return self.res

# < class Vlan

# ---- class Iface ----

class Iface(Common):
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
	# TODO: Naming...
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

	def is_vlan(self, element):
		if element is None or not hasattr(element, 'type_t') or element.type_t.lower() != TYPE_VLAN:
			return False
		return True

	def process_members(self):
		# Vlans
		vlans = []
		if self.members.get(IFACE_KEY_VLAN) is not None:
			vlan_ctx = self.members.get(IFACE_KEY_VLAN)

			if vlan_ctx.obj() is not None and any(pair.key().getText().lower() in PREDEFINED_VLAN_KEYS for pair in vlan_ctx.obj().key_value_list().key_value_pair()):
				# Then handle this as a vlan object in itself, not an obj of vlans
				vlan_element = Vlan(self.nacl_state, 0, "", vlan_ctx, BASE_TYPE_TYPED_INIT, TYPE_VLAN)
				vlans.append(vlan_element)
			elif vlan_ctx.obj() is not None:
				# If this is a dictionary/map/obj of vlans
				# Add each Vlan in obj to the vlans list
				# Each element in the obj needs to be a valid Vlan
				for pair in vlan_ctx.obj().key_value_list().key_value_pair():
					# Key: Name of Vlan
					# Value: Actual Vlan object/value (containing address, netmask, gateway, index)
					vlan_element = Vlan(self.nacl_state, 0, pair.key().getText(), pair.value(), BASE_TYPE_TYPED_INIT, TYPE_VLAN)
					vlans.append(vlan_element)
			elif vlan_ctx.list_t() is not None:
				# Add each Vlan in list_t to the vlans list
				# Each element in the list_t needs to be a valid Vlan
				for _, v in enumerate(vlan_ctx.list_t().value_list().value()):
					vlan_element = None

					if v.value_name() is not None:
						vlan_name = v.value_name().getText()
						vlan_element = self.nacl_state.elements.get(vlan_name)
						if not self.is_vlan(vlan_element):
							exit_NaCl(v.value_name(), "Undefined Vlan " + vlan_name)
					elif v.obj() is not None:
						vlan_element = Vlan(self.nacl_state, 0, "", v, BASE_TYPE_TYPED_INIT, TYPE_VLAN)
					else:
						exit_NaCl(v, "A Vlan list must either contain Vlan objects (key value pairs) or names of Vlans")

					vlans.append(vlan_element)
			elif vlan_ctx.value_name() is not None:
				vlan_name = vlan_ctx.value_name().getText()
				vlan_element = self.nacl_state.elements.get(vlan_name)
				if not self.is_vlan(vlan_element):
					exit_NaCl(vlan_ctx.value_name(), "Undefined Vlan " + vlan_name)
				vlans.append(vlan_element)
			else:
				exit_NaCl(vlan_ctx, "An Iface's vlan needs to be a list of Vlans")

		# Loop through self.members and transpile the values
		for key, member in self.members.iteritems():
			if key != IFACE_KEY_CONFIG and key != IFACE_KEY_MASQUERADE:
				self.members[key] = self.nacl_state.transpile_value(member)

				# Validate that an Iface with this Iface's index has not already been defined
				if key == IFACE_KEY_INDEX:
					for key, el in self.nacl_state.elements.iteritems():
						if isinstance(el, Iface) and key != self.name:
							el_idx = el.members.get(IFACE_KEY_INDEX)
							if el_idx is not None and el_idx == self.members.get(IFACE_KEY_INDEX):
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

		self.nacl_state.append_to_pystache_data_list(TEMPLATE_KEY_IFACES_WITH_VLANS, {
			TEMPLATE_KEY_IFACE: 		self.name,
			TEMPLATE_KEY_IFACE_INDEX: 	self.members.get(IFACE_KEY_INDEX),
			TEMPLATE_KEY_VLANS: 		pystache_vlans
		})

	def add_iface(self):
		# Append iface object to pystache ifaces list

		# Create object containing key value pairs with the data we have collected
		# Append this object to the ifaces list
		# Is to be sent to pystache renderer in handle_input function
		self.nacl_state.append_to_pystache_data_list(TEMPLATE_KEY_IFACES, {
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
		if not self.nacl_state.exists_in_pystache_list(TEMPLATE_KEY_ENABLE_CT_IFACES, TEMPLATE_KEY_IFACE, self.name):
			for chain in CHAIN_NAMES:
				if self.chains.get(chain) is not None:
					self.nacl_state.append_to_pystache_data_list(TEMPLATE_KEY_ENABLE_CT_IFACES, {
						TEMPLATE_KEY_IFACE: self.name
					})
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

		return self.res

	# Called from handle_input (NaCl.py) right before rendering, after the NaCl file has been processed
	# Register the last data here that can not be registered before this (set has-values f.ex.)
	@staticmethod
	def final_registration(nacl_state):
		if not nacl_state.pystache_list_is_empty(TEMPLATE_KEY_AUTO_NATTING_IFACES):
			nacl_state.register_pystache_data_object(TEMPLATE_KEY_HAS_AUTO_NATTING_IFACES, True)

		if not nacl_state.pystache_list_is_empty(TEMPLATE_KEY_IFACES_WITH_VLANS):
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
		TEMPLATE_KEY_IFACES_WITH_VLANS, \
		TEMPLATE_KEY_MASQUERADES, \
		TEMPLATE_KEY_ENABLE_CT_IFACES
		# TEMPLATE_KEY_HAS_MASQUERADES, \
		# TEMPLATE_KEY_HAS_AUTO_NATTING_IFACES, \
		# TEMPLATE_KEY_HAS_VLANS \
		# These three are added in the final_registration method
	])

# def create_vlan_pystache_lists(nacl_state):
#	nacl_state.create_pystache_data_lists(...)

def init(nacl_state):
	# print "Init iface: Iface and Vlan"

	nacl_state.add_type_processor(TYPE_IFACE, Iface)
	nacl_state.add_type_processor(TYPE_VLAN, Vlan)

	create_iface_pystache_lists(nacl_state)
	# create_vlan_pystache_lists(nacl_state) # No lists to create
