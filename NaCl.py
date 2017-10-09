#! /usr/local/bin/python

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
TEMPLATE_KEY_VLANS 				= "vlans"
TEMPLATE_KEY_FILTERS 			= "filters"
TEMPLATE_KEY_NATS 				= "nats"
TEMPLATE_KEY_REWRITES 			= "rewrites"
TEMPLATE_KEY_PUSHES 			= "pushes"
TEMPLATE_KEY_GATEWAYS 			= "gateways"
TEMPLATE_KEY_IP_FORWARD_IFACES 	= "ip_forward_ifaces"
TEMPLATE_KEY_CT_IFACES 			= "ct_ifaces"
TEMPLATE_KEY_MASQUERADES 		= "masquerades"

TEMPLATE_KEY_HAS_GATEWAYS 		= "has_gateways"
TEMPLATE_KEY_HAS_NATS 			= "has_nats"
TEMPLATE_KEY_HAS_MASQUERADES 	= "has_masquerades"

# Data to be sent to pystache renderer
# Each list are to contain objects consisting of key value pairs
ifaces 				= []
vlans 				= []
filters 			= []
rewrites 			= []
nats 				= []
pushes 				= []
gateways 			= []
ip_forward_ifaces 	= []
ct_ifaces 			= []
masquerades 		= []

gateway_exists 		= False

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
TEMPLATE_KEY_VLAN 			= "vlan"
TEMPLATE_KEY_ADDRESS 		= "address"
TEMPLATE_KEY_NETMASK 		= "netmask"
TEMPLATE_KEY_GATEWAY 		= "gateway"
TEMPLATE_KEY_DNS 			= "dns"
TEMPLATE_KEY_ROUTES 		= "routes"
TEMPLATE_KEY_CONTENT		= "content"

def transpile_function(language, type_t, subtype, ctx):
	if language == CPP:
		return transpile_function_cpp(type_t, subtype, ctx)

def resolve_value(language, ctx):
	if language == CPP:
		return resolve_value_cpp(ctx)

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
		sys.exit("Error (" + self.name + "): Subclass of class Element has not implemented the process method")

	# ---------- Methods related to dictionary self.members ----------

	# Called when resolving values
	def get_member_value(self, key_list):
		self.process() # Make sure this element has been processed (self.res is not None)
		return self.get_dictionary_val(self.members, key_list)

	def get_dictionary_val(self, dictionary, key_list):
		level_key = key_list[0]

		# End of recursion condition
		if len(key_list) == 1:
			return dictionary.get(level_key)

		if level_key not in dictionary:
			return None

		# Recursion
		for key in dictionary:
			if key == level_key:
				key_list.pop(0) # Remove first key (level_key) - has been found
				return self.get_dictionary_val(dictionary[key], key_list)

	def add_dictionary_val(self, dictionary, key_list, value):
		level_key = key_list[0]

		# End of recursion condition
		if len(key_list) == 1:
			if value.obj() is not None:
				# Then the value is a new dictionary
				dictionary[level_key] = {} # Create new dictionary
				return self.process_obj(dictionary[level_key], value.obj())
			else:
				dictionary[level_key] = resolve_value(LANGUAGE, value)
				return

		if level_key not in dictionary:
			sys.exit("Error (" + self.name + "): Trying to add to a member (" + level_key + ") that doesn't exist")

		for key in dictionary:
			if key == level_key:
				key_list.pop(0) # Remove first key (level_key) - has been found
				return self.add_dictionary_val(dictionary[key], key_list, value)

	def process_obj(self, dictionary, ctx):
		for pair in ctx.key_value_list().key_value_pair():
			key = pair.key().getText()

			if dictionary.get(key) is not None:
				sys.exit("Error(" + self.name + "): Member " + key + " has already been set")

			# End of recursion:
			if pair.value().obj() is None:
				dictionary[key] = resolve_value(LANGUAGE, pair.value())
			else:
				# Recursion:
				# Then we have an obj inside an obj
				dictionary[key] = {} # creating new dictionary
				# loop through the obj and fill the new dictionary
				self.process_obj(dictionary[key], pair.value().obj())

# < Element

# -------------------- Untyped --------------------

class Untyped(Element):
	def __init__(self, idx, name, ctx, base_type):
		super(Untyped, self).__init__(idx, name, ctx, base_type)

	def process(self):
		if self.res is None:
			name_parts = self.name.split(DOT)

			if len(name_parts) > 1:
				# This is an assignment to an already existing element
				element_name 	= name_parts[0]
				member 			= name_parts[1]
				
				element = elements.get(element_name)
				if element is None:
					sys.exit("Error (" + self.name + "): No element with the name " + element_name + " exists")
			else:
				if self.ctx.value().obj() is not None:
					# Then this element is an obj and other assignments can add to this element
					# We need to validate that no other assignments are overwriting one of the element's
					# values:
					
					self.process_obj(self.members, self.ctx.value().obj())

					# Loop through assignments
					# Find assignments (f.ex. my_map.e1: <value>) that refers to this Untyped element
					for i, key in enumerate(elements):
						if key.startswith(self.name + DOT):
							# Then we know we have to do with a value_name
							element = elements.get(key)
							assignment_name_parts = key.split(DOT)
							# Remove first part (the name of this element)
							assignment_name_parts.pop(0)

							# Check if this key has already been set in this Untyped element
							# In that case: Error: Value already set
							if self.get_dictionary_val(self.members, list(assignment_name_parts)) is not None:
								sys.exit("Error (" + self.name + "): Member " + element.name + " has already been set")
							else:
								# Add to members dictionary
								self.add_dictionary_val(self.members, assignment_name_parts, element.ctx.value())

					print self.name, ": Members after checking assignments related to this element:", str(self.members)

			self.res = self.members

		return self.res

# < Untyped

# -------------------- Typed --------------------

class Typed(Element):
	def __init__(self, idx, name, ctx, base_type, type_t):
		super(Typed, self).__init__(idx, name, ctx, base_type)
		self.type_t = type_t

# < Typed

# -------------------- Iface --------------------

class Iface(Typed):
	def __init__(self, idx, name, ctx, base_type, type_t):
		super(Iface, self).__init__(idx, name, ctx, base_type, type_t)

		self.masquerade = False
		self.config_is_dhcp = False
		self.config_is_dhcp_fallback = False
		self.config_is_static = False

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

	def process(self):
		if self.res is None:
			# Then process
			
			pushes_to_add = {}
			value = self.ctx.value()

			if value.obj() is not None:
				for pair in value.obj().key_value_list().key_value_pair():
					orig_key 	= pair.key().getText()
					key 		= orig_key.lower()
					pair_value 	= pair.value()

					if self.members.get(key) is not None:
						sys.exit("Error (" + self.name + "): Member " + key + " has already been set")

					if key not in predefined_iface_keys:
						sys.exit("Error (" + self.name + "): Invalid member (" + orig_key + ") inside Iface object")

					if key in chains:
						functions = []
						
						if pair_value.list_t() is not None:
							# More than one function pushed onto chain
							for list_value in pair_value.list_t().value_list().value():
								if list_value.value_name() is None:
									sys.exit("Error (" + self.name + "): This is not supported: " + pair.getText())
								functions.append(list_value.value_name().getText())
						elif pair_value.value_name() is not None:
							# Only one function pushed onto chain
							functions = [pair_value.value_name().getText()]
						else:
							sys.exit("Error (" + self.name + "): This is not supported: " + pair.getText())

						pushes_to_add[key] = functions
					else:
						if key != IFACE_KEY_MASQUERADE:
							self.members[key] = pair_value
						else:
							if resolve_value(LANGUAGE, pair_value) == TRUE:
								self.masquerade = True
			elif value.value_name() is not None:
				# configuration type (dhcp, dhcp-with-fallback, static)
				config = value.value_name().getText().lower()
				if config in predefined_config_types:
					self.members[IFACE_KEY_CONFIG] = value
				else:
					sys.exit("Error (" + self.name + "): Invalid Iface value " + value.value_name().getText())
			else:
				sys.exit("Error (" + self.name + "): An Iface has to contain key value pairs, or be set to a configuration type (" + \
					", ".join(predefined_config_types) + ")")

			# Loop through assignments
			# Find assignments (f.ex. eth0.index: <value>) that refers to this Iface
			for i, key in enumerate(elements):
				if key.startswith(self.name + DOT):
					# Then we know we have to do with a value_name
					element = elements.get(key)
					name_parts = element.ctx.value_name().getText().split(DOT)					
					orig_iface_member = name_parts[1]
					iface_member = orig_iface_member.lower()

					if len(name_parts) != 2:
						sys.exit("Error (" + element.name + "): Invalid Iface property " + key)

					if iface_member not in predefined_iface_keys:
						sys.exit("Error (" + element.name + "): Invalid member (" + orig_iface_member + ") of Iface object")
					
					found_element_value = element.ctx.value()

					# ? eth0.vlan: [ my_vlan, my_other_vlan ]

					if iface_member in chains:
						# Not allowed to edit already set property
						# if pushes_to_add.get(iface_member) is None or i > self.idx:
						# 	functions = []

						# 	if found_element_value.list_t() is not None:
						# 		# More than one function pushed onto chain
						# 		for list_value in found_element_value.list_t().value_list().value():
						# 			if list_value.value_name() is None:
						# 				sys.exit("Error (" + element.name + "): This is not supported: " + element.ctx.getText())
						# 			functions.append(list_value.value_name().getText())
						# 	elif found_element_value.value_name() is not None:
						# 		# Only one function pushed onto chain
						# 		functions = [found_element_value.value_name().getText()]
						# 	else:
						# 		sys.exit("Error (" + element.name + "): This is not supported: " + element.ctx.getText())

						# 	pushes_to_add[iface_member] = functions
						# Therefore:
						if pushes_to_add.get(iface_member) is None:
							functions = []

							if found_element_value.list_t() is not None:
								# More than one function pushed onto chain
								for list_value in found_element_value.list_t().value_list().value():
									if list_value.value_name() is None:
										sys.exit("Error (" + element.name + "): This is not supported: " + element.ctx.getText())
									functions.append(list_value.value_name().getText())
							elif found_element_value.value_name() is not None:
								# Only one function pushed onto chain
								functions = [found_element_value.value_name().getText()]
							else:
								sys.exit("Error (" + element.name + "): This is not supported: " + element.ctx.getText())

							pushes_to_add[iface_member] = functions
						else:
							sys.exit("Error (" + element.name + "): Iface chain " + iface_member + " has already been set")
					else:
						if iface_member != IFACE_KEY_MASQUERADE:
							# Not allowed to edit already set property
							# if self.members.get(iface_member) is None or i > self.idx:
							# 	self.members[iface_member] = found_element_value
							# Therefore:
							if self.members.get(iface_member) is None:
								self.members[iface_member] = found_element_value
							else:
								sys.exit("Error (" + element.name + "): Iface member " + iface_member + " has already been set")
						else:
							masq_val = resolve_value(LANGUAGE, found_element_value)
							# TODO:
							# Make impossible to edit masquerade property/member as well? (sys.exit)
							if not self.masquerade or i > self.idx:
								if masq_val == TRUE:
									self.masquerade = True

			if self.members.get(IFACE_KEY_INDEX) is None:
				sys.exit("Error (" + self.name + "): An index needs to be specified for all Ifaces")

			config = self.members.get(IFACE_KEY_CONFIG)
			if config is not None and (config.value_name() is None or config.value_name().getText().lower() not in predefined_config_types):
				sys.exit("Error (" + self.name + "): Invalid config value " + config.getText())

			if (config is None or config.value_name().getText().lower() != DHCP_CONFIG) and \
				(self.members.get(IFACE_KEY_ADDRESS) is None or \
					self.members.get(IFACE_KEY_NETMASK) is None or \
					self.members.get(IFACE_KEY_GATEWAY) is None):
				sys.exit("Error (" + self.name + "): The members address, netmask and gateway must be set for every Iface if the Iface " + \
					"configuration hasn't been set to " + DHCP_CONFIG)

			# Add pushes (pushes of functions onto the Iface's chains):
			for push_key, functions in pushes_to_add.iteritems():
				self.add_push(push_key, functions)

			if self.masquerade:
				masquerades.append({TEMPLATE_KEY_IFACE: self.name})

			if self.members.get(IFACE_KEY_VLAN) is not None:
				print "VLAN specified for Iface", self.name
				print self.members.get(IFACE_KEY_VLAN)
				
				# TODO
				# vlans.append()

				# Resolve value
				# Could be: a list_t or an obj
				# And each element in the list_t or obj could be the name of an Iface (if obj, the key is the vlan's id or index),
				# or an obj again containing Iface key value pairs
				
				# Also TODO:
				# If this is not a top level Iface, but an Iface that is part of another Iface's vlan,
				# it should not be appended to ifaces list ?
				# Set a member that says that this is a vlan interface

			# Note: If a member's value is None, the new value will be "" here:
			for key, member in self.members.iteritems():
				if key != IFACE_KEY_CONFIG:
					if key != IFACE_KEY_INDEX:
						self.members[key] = resolve_value(LANGUAGE, self.members.get(key))							
					else:
						index = self.members.get(IFACE_KEY_INDEX)
						self.members[IFACE_KEY_INDEX] = resolve_value(LANGUAGE, index)
				else:
					self.members[IFACE_KEY_CONFIG] = "" if self.members.get(IFACE_KEY_CONFIG) is None else self.members.get(IFACE_KEY_CONFIG).value_name().getText().lower()

			config = self.members.get(IFACE_KEY_CONFIG)
			if config == DHCP_CONFIG:
				self.config_is_dhcp = True
			elif config == DHCP_FALLBACK_CONFIG:
				self.config_is_dhcp_fallback = True
			else:
				self.config_is_static = True

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

				# TODO: Add to vlans list
				# TEMPLATE_KEY_VLAN: 		self.members.get(IFACE_KEY_VLAN),	# not resolved (for now)
				
				TEMPLATE_KEY_ADDRESS: 	self.members.get(IFACE_KEY_ADDRESS),
				TEMPLATE_KEY_NETMASK:	self.members.get(IFACE_KEY_NETMASK),
				TEMPLATE_KEY_GATEWAY: 	self.members.get(IFACE_KEY_GATEWAY),
				TEMPLATE_KEY_DNS: 		self.members.get(IFACE_KEY_DNS)
			})

			print "Processed iface with name " + self.name

			self.res = self.members
			# Or:
			# self.res = resolve_value(LANGUAGE, ...)

		return self.res

	# chain: string with name of chain
	# functions: list containing strings, where each string corresponds to the name of a NaCl function
	def add_push(self, chain, functions):
		function_names = []
		num_functions = len(functions)
		for i, function in enumerate(functions):
			element = elements.get(function)
			if element is None or element.base_type != BASE_TYPE_FUNCTION:
				sys.exit("Error: No function (Filter, Nat) with the name " + function + " exists")
			function_names.append({TEMPLATE_KEY_FUNCTION_NAME: function, TEMPLATE_KEY_COMMA: (i < (num_functions - 1))})

		pushes.append({
			TEMPLATE_KEY_IFACE:				self.name,
			TEMPLATE_KEY_CHAIN: 			chain,
			TEMPLATE_KEY_FUNCTION_NAMES: 	function_names
		})

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

	def process(self):
		if self.res is None:
			# Then process
		
			# TODO

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

	def get_pystache_route_obj(self, name, route_ctx):
		route_obj = {}
		pairs = route_ctx.key_value_list().key_value_pair()
		num_pairs = len(pairs)

		for pair in pairs:
			orig_key = pair.key().getText()
			key = orig_key.lower()

			if route_obj.get(key) is not None:
				sys.exit("Error (" + self.name + "): Member " + key + " has already been set for route " + name)

			if key not in predefined_gateway_keys:
				sys.exit("Error (" + self.name + "): " + orig_key + " is not a valid Gateway route member. " + \
					"Valid members are: " + ", ".join(predefined_gateway_keys))

			if key != GATEWAY_KEY_IFACE:
				route_obj[key] = resolve_value(LANGUAGE, pair.value())
			else:
				# Then the Iface element's name is to be added to the route_obj,
				# not the resolved Iface
				iface_name = pair.value().getText()

				if pair.value().value_name() is None:
					sys.exit("Error (" + self.name + "): Gateway route contains an iface property with an invalid value: " + iface_name)

				element = elements.get(iface_name)
				if element is None or (hasattr(element, 'type_t') and element.type_t.lower() != TYPE_IFACE):
					sys.exit("Error (" + self.name + "): No Iface with the name " + iface_name + " exists")

				route_obj[key] = iface_name

		return route_obj

	def process(self):
		if self.res is None:
			# Then process:
			
			value = self.ctx.value()

			if value.obj() is not None:
				for route_pair in value.obj().key_value_list().key_value_pair():
					name = route_pair.key().getText()
					if self.members.get(name) is not None:
						sys.exit("Error (" + self.name + "): Member " + name + " has already been set")

					if route_pair.value().obj() is None:
						sys.exit("Error (" + self.name + "): A Gateway's routes must constitute an object (" + \
							"containing key value pairs)")
					key = route_pair.key().getText()

					if route_pair.value().obj() is None:
						sys.exit("Error (" + self.name + "): A Gateway's route must contain key value pairs. " + \
							"Invalid route value: " + route_pair.value().getText())
					
					# Add pystache route obj to members dictionary
					self.members[key] = self.get_pystache_route_obj(key, route_pair.value().obj())
			elif value.list_t() is not None:
				for i, val in enumerate(value.list_t().value_list().value()):
					if val.obj() is None:
						sys.exit("Error (" + self.name + "): A Gateway that constitutes a list must be a list of " + \
							"objects (containing key value pairs). Invalid value: " + val.getText())
					
					# Add pystache route obj to members dictionary
					# When unnamed routes, use index as key
					self.members[i] = self.get_pystache_route_obj(str(i), val.obj())
			else:
				sys.exit("Error (" + self.name + "): A Gateway must contain key value pairs (in which " + \
					"each pair's value is an object), or it must contain a list of objects")

			# Loop through assignments
			# Find assignments (f.ex. gateway.r2.nexthop: <value>) that refers to this Gateway
			for i, key in enumerate(elements):
				if key.startswith(self.name + DOT):
					# Then we know we have to do with a value_name
					element = elements.get(key)
					name_parts = element.ctx.value_name().getText().split(DOT)					
					gw_member = name_parts[1]
					num_name_parts = len(name_parts)

					if num_name_parts > 3:
						sys.exit("Error (" + self.name + "): Invalid Gateway member " + key)

					if self.members.get(0) is not None:
						sys.exit("Error (" + self.name + "): Trying to access a named member in a Gateway without named members (" + key + ")")
					# Could support later: gateway.0.netmask: 255.255.255.0

					if num_name_parts == 2:
						# Then the user is adding an additional route to this Gateway
						# F.ex. gateway.r6: <value>
						# Not allowed to edit already set property:
						# if self.members.get(gw_member) is None or i > self.idx:
						# 	# Then add the route if valid
						# 	if element.ctx.value().obj() is None:
						# 		sys.exit("Error (" + element.name + "): A Gateway member's value needs to be contain key value pairs")
						# 	self.members[gw_member] = self.get_pystache_route_obj(element.ctx.value().obj())
						# Therefore:
						if self.members.get(gw_member) is None:
							# Then add the route if valid
							if element.ctx.value().obj() is None:
								sys.exit("Error (" + element.name + "): A Gateway member's value needs to be contain key value pairs")
							self.members[gw_member] = self.get_pystache_route_obj(element.ctx.value().obj())
						else:
							sys.exit("Error (" + self.name + "): Gateway member " + gw_member + " has already been set")
					else:
						# Then num_name_parts are 3 and we're talking about changing (no longer allowed) a route's member
						# or adding one
						route = self.members.get(gw_member)
						if route is None:
							sys.exit("Error (" + self.name + "): No member named " + gw_member + " in Gateway " + self.name + \
								" This assignment is invalid: " + element.ctx.getText())

						route_member = name_parts[2].lower()
						
						if route.get(route_member) is not None:
							sys.exit("Error (" + self.name + "): Member " + route_member + " in route " + gw_member + " has already been set")

						if route_member not in predefined_gateway_keys:
							sys.exit("Error (" + element.ctx.key().getText() + "): " + route_member + " is not a valid Gateway route member. " + \
								"Valid members are: " + ", ".join(predefined_gateway_keys))

						if route_member != GATEWAY_KEY_IFACE:
							route[route_member] = resolve_value(LANGUAGE, element.ctx.value())
						else:
							# Then the Iface element's name is to be added to the route obj,
							# not the resolved Iface
							iface_name = element.ctx.value().getText()

							if element.ctx.value().value_name() is None:
								sys.exit("Error (" + element.ctx.key().getText() + "): iface property's value (" + \
									iface_name + ") is invalid")

							iface_element = elements.get(iface_name)
							if iface_element is None or (hasattr(iface_element, 'type_t') and iface_element.type_t.lower() != TYPE_IFACE):
								sys.exit("Error (" + element.ctx.key().getText() + "): No Iface with the name " + iface_name + " exists")

							route[route_member] = iface_name

			routes = []
			index = 0
			num_routes = len(self.members)
			for i, route in self.members.iteritems():
				if GATEWAY_KEY_NETMASK not in route or \
					GATEWAY_KEY_IFACE not in route or \
					(GATEWAY_KEY_NET not in route and GATEWAY_KEY_HOST not in route):
					sys.exit("Error (" + self.name + "'s route " + str(i) + "): In a Gateway route, these properties are mandatory: " + \
						", " + GATEWAY_KEY_IFACE + ", " + GATEWAY_KEY_NETMASK + " and either " + GATEWAY_KEY_NET + \
						" or " + GATEWAY_KEY_HOST)

				# Add iface_name to ip_forward_ifaces pystache list if it is not in the
				# list already
				iface_name = route.get(GATEWAY_KEY_IFACE)
				if iface_name is not None and not any(ip_forward_iface[TEMPLATE_KEY_IFACE] == iface_name for ip_forward_iface in ip_forward_ifaces):
					ip_forward_ifaces.append({TEMPLATE_KEY_IFACE: iface_name})

					print "IFACE IP FORWARD LIST:", str(ip_forward_ifaces)

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
			
			# Create object containing key value pairs with the data we have collected
			# Append this object to the gateways list
			# Is to be sent to pystache renderer in handle_input function
			gateways.append({
				TEMPLATE_KEY_NAME: self.name,
				TEMPLATE_KEY_ROUTES: routes
			})

			print "Gateway pystache obj processed. Routes:", str(routes)

			self.res = self.members # Indicating that this element (Gateway) has been processed
			# Or:
			# self.res = resolve_value(LANGUAGE, ...)

		return self.res

# < Gateway

# -------------------- Function --------------------

class Function(Element):
	def __init__(self, idx, name, ctx, base_type, type_t, subtype):		
		super(Function, self).__init__(idx, name, ctx, base_type)
		self.type_t 	= type_t
		self.subtype 	= subtype

	def process(self):
		if self.res is None:
			transpiled_content = transpile_function(LANGUAGE, self.type_t, self.subtype, self.ctx)

			pystache_function_obj = {
				TEMPLATE_KEY_NAME: 		self.name,
				TEMPLATE_KEY_TITLE: 	self.name.title(),
				TEMPLATE_KEY_CONTENT: 	transpiled_content
			}

			# Only if a function is mentioned in an assignment that is a push or
			# an Iface's chain, should it be added to filters/nats/rewrites pystache list

			self.res = transpiled_content

			print "Processed function with name " + self.name

			for p in pushes:
				for f in p[TEMPLATE_KEY_FUNCTION_NAMES]:
			 		if self.name == f[TEMPLATE_KEY_FUNCTION_NAME]:
			 			# Then we know that this function is called in the C++ code
			 			# And the function should be added to the correct pystache list
			 			type_t_lower = self.type_t.lower()
			 			
			 			if type_t_lower == TYPE_FILTER:
			 				filters.append(pystache_function_obj)
			 			elif type_t_lower == TYPE_NAT:
			 				nats.append(pystache_function_obj)
			 			elif type_t_lower == TYPE_REWRITE:
			 				rewrites.append(pystache_function_obj)
			 			else:
			 				sys.exit("Error (" + self.name + "): Function of type " + self.type_t + " is not valid")
			 			return self.res

		return self.res

# < Function

# -------------------- 2. Process elements and write content to file --------------------

def handle_input():
	if LANGUAGE not in valid_languages:
		sys.exit("Error (handle_input): Cannot transpile to language " + LANGUAGE)

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
		TEMPLATE_KEY_IFACES: 			ifaces,
		TEMPLATE_KEY_VLANS: 			vlans,
		TEMPLATE_KEY_FILTERS: 			filters,
		TEMPLATE_KEY_NATS: 				nats,
		TEMPLATE_KEY_REWRITES: 			rewrites,
		TEMPLATE_KEY_PUSHES: 			pushes,
		TEMPLATE_KEY_GATEWAYS: 			gateways, # or only one gateway?
		TEMPLATE_KEY_IP_FORWARD_IFACES:	ip_forward_ifaces,
		TEMPLATE_KEY_CT_IFACES:			ct_ifaces,
		TEMPLATE_KEY_MASQUERADES: 		masquerades,
		TEMPLATE_KEY_HAS_GATEWAYS: 		(len(gateways) > 0),
		TEMPLATE_KEY_HAS_NATS: 			(len(nats) > 0),
		TEMPLATE_KEY_HAS_MASQUERADES:	(len(masquerades) > 0)
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
		sys.exit("Error (handle_input): Transpilation to language " + LANGUAGE + " has not been implemented")

# -------------------- 1. Visiting --------------------

def save_element(base_type, ctx):
	idx = len(elements)

	if base_type == BASE_TYPE_UNTYPED_INIT:
		name = ctx.value_name().getText()
		if name in elements:
			sys.exit("Error (save_element): Element " + name + " has already been defined")

		# Untyped
		elements[name] = Untyped(idx, name, ctx, base_type)
	elif base_type == BASE_TYPE_TYPED_INIT:
		type_t = ctx.type_t().getText()
		type_t_lower = type_t.lower()
		name = ctx.name().getText()
		
		if type_t_lower not in valid_nacl_types:
			sys.exit("Error (" + name + "): Undefined type " + type_t)
		if name in elements:
			sys.exit("Error (save_element): Element " + name + " has already been defined")

		if type_t_lower == TYPE_IFACE:
			# Iface
			elements[name] = Iface(idx, name, ctx, base_type, type_t)
		elif type_t_lower == TYPE_VLAN:
			elements[name] = Vlan(idx, name, ctx, base_type, type_t)
		elif type_t_lower == TYPE_GATEWAY:
			global gateway_exists
			
			# Gateway
			# Only allowed to create one Gateway (for now at least)
			if gateway_exists:
				sys.exit("Error (" + name + "): You cannot create more than one Gateway")

			elements[name] = Gateway(idx, name, ctx, base_type, type_t)
			gateway_exists = True
		else:
			sys.exit("Error (" + name + "): NaCl elements of type " + type_t + " are not handled")
	elif base_type == BASE_TYPE_FUNCTION:
		type_t = ctx.type_t().getText()
		subtype = ctx.subtype().getText()
		
		if type_t.lower() not in valid_nacl_types:
			sys.exit("Error (save_element): Undefined type " + type_t)

		# A top function must have a name
		if ctx.name() is None:
			sys.exit("Error (save_element): A top function (" + type_t + "::" + subtype + ") must have a name")

		name = ctx.name().getText()
		if name in elements:
			sys.exit("Error (save_element): Element " + name + " has already been defined")

		# Function
		elements[name] = Function(idx, name, ctx, base_type, type_t, subtype)
	else:
		sys.exit("Error (save_element): Undefined base type " + base_type)

class NaClRecordingVisitor(NaClVisitor):

	def visitTyped_initializer(self, ctx):
		print "Visiting typed initializer", ctx.name().getText(), "of type", ctx.type_t().getText()

		# Typed: Could indicate that C++ code is going to be created from this - depends on the
		# type_t specified (Iface, Gateway special)

		save_element(BASE_TYPE_TYPED_INIT, ctx)

	def visitInitializer(self, ctx):
		print "Visiting untyped initializer with value_name", ctx.value_name().getText()

		# Untyped: Means generally that no C++ code is going to be created from this - exists only in NaCl
		# Except: Assignments

		save_element(BASE_TYPE_UNTYPED_INIT, ctx)

	def visitFunction(self, ctx):
		text = "Visiting function of type " + ctx.type_t().getText() + " and subtype " + ctx.subtype().getText()
		
		if ctx.name() is not None:
			text += " with name " + ctx.name().getText()
		else:
			text += " without a name"
		
		print text

		save_element(BASE_TYPE_FUNCTION, ctx)

lexer = NaClLexer(StdinStream())
stream = CommonTokenStream(lexer)
parser = NaClParser(stream)
tree = parser.prog()
visitor = NaClRecordingVisitor()
visitor.visit(tree)

handle_input()