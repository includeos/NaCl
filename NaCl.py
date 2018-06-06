#! /usr/bin/env python

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

from antlr4 import *
from NaClLexer import *
from NaClParser import *
from NaClVisitor import *
import sys
import os

import pystache

''' Moved to function.py
# cpp_transpile_function.py also imports cpp_resolve_values.py, which
# in turn imports shared_constants.py
from cpp_transpile_function import *
'''
# ->
from shared_constants import * # CPP
from cpp_resolve_values import Cpp_value_resolver # resolve_value_cpp

# antlr4 -Dlanguage=Python2 NaCl.g4 -visitor

# Old:
# LANGUAGE = CPP # CPP is defined in shared_constants.py, imported in cpp_template.py

# Pystache keys
# New:
# TEMPLATE_KEY_IFACES 				= "ifaces"
# TEMPLATE_KEY_IFACES_WITH_VLANS	= "ifaces_with_vlans"
# New: Moved to function.py:
# TEMPLATE_KEY_FILTERS 				= "filters"
# TEMPLATE_KEY_NATS 				= "nats"
# TEMPLATE_KEY_REWRITES 			= "rewrites"

# New:
# TEMPLATE_KEY_PUSHES 			= "pushes"
# New: Moved to gateway.py:
# TEMPLATE_KEY_GATEWAY_PUSHES 	= "pushes_gateway"

# New: Moved to gateway.py:
# TEMPLATE_KEY_GATEWAYS 		= "gateways"
# New: Moved to conntrack.py:
# TEMPLATE_KEY_CONNTRACKS 		= "conntracks"
# New: Moved to load_balancer.py:
# TEMPLATE_KEY_LOAD_BALANCERS 	= "load_balancers"
# New: Moved to syslog.py:
# TEMPLATE_KEY_SYSLOGS 			= "syslogs"
# New: Moved to gateway.py:
# TEMPLATE_KEY_IP_FORWARD_IFACES 	= "ip_forward_ifaces"
# New:
# TEMPLATE_KEY_ENABLE_CT_IFACES 	= "enable_ct_ifaces"
# TEMPLATE_KEY_MASQUERADES 			= "masquerades"
# TEMPLATE_KEY_AUTO_NATTING_IFACES 	= "auto_natting_ifaces"

# New: Moved to gateway.py:
# TEMPLATE_KEY_HAS_GATEWAYS 	= "has_gateways"
# New: Moved to function.py:
# TEMPLATE_KEY_HAS_NATS 		= "has_nats"
# New:
# TEMPLATE_KEY_HAS_MASQUERADES 	= "has_masquerades"
# TEMPLATE_KEY_HAS_VLANS 		= "has_vlans"
# New:
# TEMPLATE_KEY_HAS_AUTO_NATTING_IFACES = "has_auto_natting_ifaces"
# New: Moved to function.py:
# TEMPLATE_KEY_HAS_FUNCTIONS 	= "has_functions"
# New: Moved to load_balancer.py:
# TEMPLATE_KEY_HAS_LOAD_BALANCERS = "has_load_balancers"
# New: Moved to syslog.py:
# TEMPLATE_KEY_HAS_SYSLOGS 		= "has_syslogs"

# Note: Moved to conntrack.py:
# TEMPLATE_KEY_ENABLE_CT 		= "enable_ct"

# New: Moving this into class NaCl_state:
# Data to be sent to pystache renderer
# Each list are to contain objects consisting of key value pairs
# New: Moved into Iface class:
# ifaces 				= []
# ifaces_with_vlans 	= []
# New: Moved into function.py:
# filters 			= []
# rewrites 			= []
# nats 				= []
# New: Moved into Iface class:
# pushes 			= []
# New: Moved to gateway.py:
# gateways 			= []
# New: Moved to conntrack.py:
# conntracks 		= []
# New: Moved to load_balancer.py:
# load_balancers 	= []
# New: Moved to syslog.py:
# syslogs 			= []
# New: Moved to gateway.py:
# ip_forward_ifaces = []
# New: Moved into Iface class:
# enable_ct_ifaces 	= []
# masquerades 		= []
# auto_natting_ifaces = []
# New: Moved into NaCl_state (add_type_processor method takes is_singleton bool value as parameter):
# gateway_exists 	= False
# conntrack_exists 	= False
# syslog_exists 	= False

# Moved into shared_between_type_processors.py:
'''
TEMPLATE_KEY_FUNCTION_NAME 	= "function_name"
TEMPLATE_KEY_COMMA 			= "comma"
TEMPLATE_KEY_IFACE 			= "iface"
TEMPLATE_KEY_CHAIN 			= "chain"
TEMPLATE_KEY_FUNCTION_NAMES = "function_names"
TEMPLATE_KEY_NAME 			= "name"
TEMPLATE_KEY_TITLE 			= "title"
'''
# New: Moved into Iface class:
# TEMPLATE_KEY_CONFIG_IS_DHCP 			= "config_is_dhcp"
# TEMPLATE_KEY_CONFIG_IS_DHCP_FALLBACK 	= "config_is_dhcp_fallback"
# TEMPLATE_KEY_CONFIG_IS_STATIC 		= "config_is_static"
# TEMPLATE_KEY_INDEX 		= "index"
# Moved into iface.py and syslog.py:
# TEMPLATE_KEY_ADDRESS 		= "address"
# Moved into iface.py:
# TEMPLATE_KEY_NETMASK 		= "netmask"
# TEMPLATE_KEY_GATEWAY 		= "gateway"
# TEMPLATE_KEY_DNS 			= "dns"
# New: Moved to gateway.py:
# TEMPLATE_KEY_ROUTES 		= "routes"
# New: Moved to function.py:
# TEMPLATE_KEY_CONTENT		= "content"
# Moved to iface.py:
# TEMPLATE_KEY_IFACE_INDEX 	= "iface_index"
# New:
# TEMPLATE_KEY_VLANS 		= "vlans"
# TEMPLATE_KEY_IS_GATEWAY_PUSH = "is_gateway_push"

# New: Moved into load_balancer.py:
'''
TEMPLATE_KEY_INDEX 					= "index"
TEMPLATE_KEY_PORT 					= "port"
TEMPLATE_KEY_LB_LAYER 				= "layer"
TEMPLATE_KEY_LB_ALGORITHM 			= "algorithm"
TEMPLATE_KEY_LB_WAIT_QUEUE_LIMIT 	= "wait_queue_limit"
TEMPLATE_KEY_LB_SESSION_LIMIT 		= "session_limit"
TEMPLATE_KEY_LB_CLIENTS_IFACE 		= "clients_iface_name"
TEMPLATE_KEY_LB_SERVERS_IFACE 		= "servers_iface_name"
TEMPLATE_KEY_LB_POOL 				= "pool"
TEMPLATE_KEY_LB_NODE_ADDRESS 		= "address"
TEMPLATE_KEY_LB_NODE_PORT 			= "port"
'''

'''
TEMPLATE_KEY_CONNTRACK_TIMEOUTS 	= "timeouts"
TEMPLATE_KEY_CONNTRACK_TYPE 		= "type"
'''

# class Resolver ? (Inherited by Cpp_value_resolver and Cpp_function_resolver f.ex.?)

def exit_NaCl(ctx, message):
	sys.exit("line " + get_line_and_column(ctx) + " " + message)

def exit_NaCl_internal_error(message):
	sys.exit("line 1:0 " + message)

def exit_NaCl_custom_line_and_column(line_and_column, message):
	sys.exit("line " + line_and_column + " " + message)

class NaCl_exception(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)

class NaCl_state(object):
	def __init__(self, language):
		# All elements (Iface, Filter, Port, etc.) that have been identified in the NaCl file
		# (by the visitor) are placed here because each language template (f.ex. cpp_template.py)
		# needs to access the elements when resolving a variable name f.ex.
		# Dictionary where key is the name of the Element and the value is the Element object or
		# subtype of this
		self.elements = {}

		self.invalid_names = [
			TCP,
			UDP,
			ICMP,
			CT,
			IP
		]
		self.nacl_type_processors = {} # e.g. nacl_types/valid_nacl_types
		self.singletons = [] 	# list of NaCl types (nacl_type_processors) that
								# there's only allowed to create ONE element of
		self.pystache_data = {} # e.g. data in handle_input

		# Languages that NaCl can be transpiled to
		self.valid_languages = [
			CPP
		]
		self.set_language(language)
		# self.language = CPP # default
		# The language is only CPP for now:
		# self.value_resolver = Cpp_value_resolver(self.elements)
		self.resolvers = {
			VALUE_RESOLVER: Cpp_value_resolver(self.elements) # Cpp_value_resolver(self)
		}

		# TODO: Find out:
		# Will every Element object have a COPY of the nacl_state object when doing
		# self.nacl_state = nacl_state
		# in the __init__ method?
		# Or will self.nacl_state be a reference referring to the ONE NaCl_state object created
		# in __main__?

	def register_custom_resolver(self, key, value):
		# F.ex. Cpp_function_resolver
		self.resolvers[key] = value

	def set_language(self, language):
		if language not in self.valid_languages:
			exit_NaCl_internal_error("Internal error in handle_input: Cannot transpile to language " + language)
		self.language = language

	def resolve_value(self, value_ctx, subtype=""):
		# if self.language == CPP:
		return self.resolvers[VALUE_RESOLVER].resolve(value_ctx, subtype) # resolve_value_cpp(value_ctx)

	def register_pystache_data_object(self, key, value):
		self.pystache_data[key] = value

	def create_pystache_data_lists(self, keys):
		for key in keys:
			self.pystache_data[key] = []

	def append_to_pystache_data_list(self, list_key, value):
		if list_key not in self.pystache_data:
			exit_NaCl_internal_error("Internal error when appending to pystache_data: No member named " + list_key)
		if not isinstance(value, dict):
			exit_NaCl_internal_error("Internal error when appending to pystache_data['" + list_key + "']: Value given is not a dictionary")
		self.pystache_data[list_key].append(value)

	def pystache_list_is_empty(self, key):
		if key not in self.pystache_data:
			exit_NaCl_internal_error("Internal error when checking if pystache list is empty: No member named " + key)
		if len(self.pystache_data[key]) > 0:
			return False
		return True

	def exists_in_pystache_list(self, list_key, key, value):
		if list_key not in self.pystache_data:
			exit_NaCl_internal_error("Internal error: No member named " + list_key + " in pystache_data")
		if any(list_obj.get(key) is not None and list_obj.get(key) == value for list_obj in self.pystache_data[list_key]):
			# if any(enable_ct_iface[TEMPLATE_KEY_IFACE] == self.name for enable_ct_iface in enable_ct_ifaces):
			return True
		return False

	# Solved by static final_registration method in the type_processors?
	# TODO: Need more dynamic solution (these are from Iface class:)
	# Last method to be called in handle_input before pystache rendering:
	'''
	def set_has_values(self):
		TEMPLATE_KEY_HAS_AUTO_NATTING_IFACES 	= "has_auto_natting_ifaces"
		TEMPLATE_KEY_HAS_VLANS 					= "has_vlans"
		TEMPLATE_KEY_HAS_MASQUERADES 			= "has_masquerades"

		auto_natting_ifaces = self.pystache_data.get(TEMPLATE_KEY_AUTO_NATTING_IFACES)
		ifaces_with_vlans = self.pystache_data.get(TEMPLATE_KEY_VLANS)
		masquerades = self.pystache_data.get(TEMPLATE_KEY_MASQUERADES)

		if auto_natting_ifaces is not None and (len(auto_natting_ifaces) > 0):
			self.register_pystache_data_object(TEMPLATE_KEY_HAS_AUTO_NATTING_IFACES, True) # (len(self.auto_natting_ifaces) > 0)
		if ifaces_with_vlans is not None and (len(ifaces_with_vlans) > 0):
			self.register_pystache_data_object(TEMPLATE_KEY_HAS_VLANS, True)
		if masquerades is not None and (len(masquerades) > 0):
			self.register_pystache_data_object(TEMPLATE_KEY_HAS_MASQUERADES, True)

		# Old:
		# self.register_pystache_data_object(TEMPLATE_KEY_HAS_MASQUERADES, (len(self.masquerades) > 0))
		# self.register_pystache_data_object(TEMPLATE_KEY_HAS_AUTO_NATTING_IFACES, (len(self.auto_natting_ifaces) > 0))
		# self.register_pystache_data_object(TEMPLATE_KEY_HAS_VLANS, (len(self.ifaces_with_vlans) > 0))
	'''

	''' Option 1:
	def register_all_type_processors(self):
		print "Register all type processors"
		# The init function in type_processors/__init__.py will loop through all the modules (.py files)
		# in the folder and will in turn call each module's init function:
		from type_processors import init as init_type_processors
		init_type_processors(self)
	'''

	def add_type_processor(self, type_name, class_constructor, is_singleton=False):
		# The name of a NaCl type should always be stored in lower case to make it easy to compare:
		type_name_lower = type_name.lower()
		self.nacl_type_processors[type_name_lower] = class_constructor
		if is_singleton:
			self.singletons.append(type_name_lower)

	# Validate the name that the user has given an element
	# Called in save_element function
	def validate_name(self, name_ctx):
		name_parts = name_ctx.getText().split(DOT)
		name = name_parts[0]

		if "-" in name:
			exit_NaCl(name_ctx, "Invalid character (-) in name " + name)

		if name.lower() in self.invalid_names:
			exit_NaCl(name_ctx, "Invalid name " + name)

	def element_of_type_exists(self, type_name):
		if any(hasattr(e, 'type_t') and e.type_t.lower() == type_name for _, e in self.elements.iteritems()):
			return True
		return False

	# Add visited element to the elements dictionary
	def save_element(self, base_type, ctx):
		# print "save_element - content of nacl_type_processors: ", str(self.nacl_type_processors)

		if base_type != BASE_TYPE_TYPED_INIT and base_type != BASE_TYPE_UNTYPED_INIT and base_type != BASE_TYPE_FUNCTION:
			exit_NaCl(ctx, "NaCl elements of base type " + base_type + " are not handled")

		name_ctx = ctx.name() if base_type != BASE_TYPE_UNTYPED_INIT else ctx.value_name()
		if name_ctx is None:
			exit_NaCl(ctx, "Missing name of element")
		if name_ctx.getText() in self.elements:
			exit_NaCl(name_ctx, "Element " + name_ctx.getText() + " has already been defined")

		self.validate_name(name_ctx)

		name = name_ctx.getText()
		idx = len(self.elements)

		# BASE_TYPE_UNTYPED_INIT

		if base_type == BASE_TYPE_UNTYPED_INIT:
			self.elements[name] = Untyped(self, idx, name, ctx, base_type)
			return

		type_t_ctx = ctx.type_t()
		type_t = type_t_ctx.getText()
		type_t_lower = type_t.lower()

		# Old: if type_t.lower() not in valid_nacl_types:
		# New:
		if type_t_lower not in self.nacl_type_processors:
			exit_NaCl(type_t_ctx, "Undefined type " + type_t)

		# If only ONE element of this type is allowed and an element of the type already exists,
		# exit with error
		if type_t_lower in self.singletons and self.element_of_type_exists(type_t_lower):
			exit_NaCl(type_t_ctx, "A " + type_t + " has already been defined")

		# BASE_TYPE_FUNCTION
		if base_type == BASE_TYPE_FUNCTION:
			# Old:
			# elements[name] = Function(self, idx, name, ctx, base_type, type_t, ctx.subtype().getText())
			# New:
			self.elements[name] = self.nacl_type_processors[type_t_lower](self, idx, name, ctx, base_type, type_t, ctx.subtype().getText())
			return

		# BASE_TYPE_TYPED_INIT
		self.elements[name] = self.nacl_type_processors[type_t_lower](self, idx, name, ctx, base_type, type_t)
		# TODO: Each class in its own file
		# Load_balancer / all classes in pyton you can call type processors
		# Type_processors (folder) contains one file per class
		# In load_balancer.py f.ex.: from Ncl import Types
		# -> NaCl.register("Load_balancer", Load_balancer) in the dictioary nacl_types/valid_nacl_types ()
		# (So don't need to change)

	# Old:
	'''
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
			elements[name] = Conntrack(idx, name, ctx, base_type, type_t)
			conntrack_exists = True
		elif type_t_lower == TYPE_SYSLOG:
			global syslog_exists
			if syslog_exists:
				sys.exit("line " + get_line_and_column(type_t_ctx) + " A Syslog has already been defined")
			elements[name] = Syslog(idx, name, ctx, base_type, type_t)
			syslog_exists = True
		else:
			sys.exit("line " + get_line_and_column(type_t_ctx) + " NaCl elements of type " + type_t + " are not handled")
	'''

''' Moved to function.py
def transpile_function(language, type_t, subtype, ctx):
	if language == CPP:
		return transpile_function_cpp(type_t, subtype, ctx)
'''

''' Moved into NaCl_state:
def resolve_value(language, ctx):
	if language == CPP:
		return resolve_value_cpp(ctx)
'''

''' Functionality moved into gateway.py (inside the add_push method):
def get_router_name(language):
	if language == CPP:
		return INCLUDEOS_ROUTER_OBJ_NAME
'''

# -------------------- Element --------------------

class Element(object):
	def __init__(self, nacl_state, idx, name, ctx, base_type):
		# New:
		self.nacl_state = nacl_state

		self.idx 		= idx
		self.name 		= name
		self.ctx 		= ctx
		self.base_type 	= base_type
		self.res 		= None

		self.handle_as_untyped = True # Default (preferred)

		# Use res
		# self.values 	= None # Resolved all the element's values so can be used
		            	       # when transpiling comparisons inside functions

		# Fill members dictionary if this is a top element with a value of type obj
		self.members = {}

	@staticmethod
	def final_registration(nacl_state):
		pass

	# All subclasses MUST implement the process method - this is the main processing method for all NaCl elements, the
	# starting point for every transpilation of every NaCl element
	def process(self):
		exit_NaCl(self.ctx, "Internal error: Subclass of class Element has not implemented the process method")

	def get_class_name(self):
		return self.__class__.__name__

	# This is only implemented in the Vlan and Iface classes
	# Every other class does nothing here
	# If not valid - throw exception
	def validate_key(self, key):
		pass

	# Can be overrided by subclasses
	# Iface is special here and should override the method
	def add_member(self, key, value):
		if self.members.get(key) is None:
			self.members[key] = value
		else:
			raise NaCl_exception(self.get_class_name() + " member " + key + " has already been set")
		# Prev: self.members[key] = value

	# def add_value_name(self, value_ctx):
	#	raise NaCl_exception()
	def add_not_obj_value(self, value_ctx):
		raise NaCl_exception(self.get_class_name() + " has to contain key value pairs")

	# Or maybe really process_object (or other name...)
	# Adding to self.members
	def process_ctx(self):
		# Handle the Element's value ctx object: Fill self.members dictionary
		# Note: Gateway has its own process_ctx method

		value = self.ctx.value() if hasattr(self.ctx, 'value') else self.ctx
		class_name = self.get_class_name()
		''' Old:
		is_iface = isinstance(self, Iface)
		is_vlan = isinstance(self, Vlan)
		'''

		# Using Untyped methods (placed in Element) since depth is more than 1 level deep
		# Old:
		'''
		if isinstance(self, Load_balancer) or isinstance(self, Conntrack) or isinstance(self, Syslog):
			if value.obj() is None:
				exit_NaCl(value, class_name + " must be an object")
			self.process_obj(self.members, value.obj())
			return
		'''
		# New:
		if self.handle_as_untyped:
			if value.obj() is None:
				exit_NaCl(value, class_name + " must be an object")
			self.process_obj(self.members, value.obj())
			return

		# Everything else but Load_balancer, Conntrack and Syslog (meaning Gateway, Vlan and Iface):
		if value.obj() is not None:
			for pair in value.obj().key_value_list().key_value_pair():
				orig_key 	= pair.key().getText()
				key 		= orig_key.lower()
				pair_value 	= pair.value()

				# TODO: Call validate_keys in subclass (throw exception with error message - call sys.exit here in catch)
				# Some classes don't need to do anything
				# Or validate_pair
				# New:
				try:
					# The old solution only tested this for vlan and iface:
					# So the other classes (are there other classes?) can have an empty validate_key implementation f.ex. (do nothing)
					# That means, this class Element can have a dummy method called this that does nothing
					self.validate_key(orig_key) # check if exists in predefined_iface_keys f.ex.
				except NaCl_exception as e:
					exit_NaCl(pair.key(), e.value)
				# Old:
				'''
				if (is_iface and key not in predefined_iface_keys) or \
					(is_vlan and key not in predefined_vlan_keys):
					sys.exit("line " + get_line_and_column(pair.key()) + " Invalid " + class_name + \
						" member " + orig_key)
				'''

				# TODO: Can be removed later? Checked in self.add_member-method
				if self.members.get(key) is not None:
					exit_NaCl(pair.key(), class_name + " member " + key + " has already been set")

				# Old:
				'''
				if is_iface and key in chains:
					self.process_push(key, pair.value())
				else:
					self.members[key] = pair_value
				'''
				# New:
				# TODO: Implement this method in all classes that needs to do other operations
				# than just adding the key value pair to the self.members dictionary
				try:
					self.add_member(key, pair_value)
				except NaCl_exception as e:
					exit_NaCl(pair.key(), e.value)
				# Default add_member behavior: self.members[key] = pair_value
				# Special if is_iface and key in chains: self.process_push(key, pair_value)

			# Really one tab to the left:
			# Old:
			'''
			elif is_iface and value.value_name() is not None:
				# configuration type (dhcp, dhcp-with-fallback, static)
				config = value.value_name().getText().lower()
				if config in predefined_config_types:
					self.members[IFACE_KEY_CONFIG] = value
				else:
					sys.exit("line " + get_line_and_column(value) + " Invalid Iface value " + value.value_name().getText())
			# New:
			# else:
			'''
		else:
			try:
				self.add_not_obj_value(value)
				# Iface's method if not value.value_name() is None:
				'''
				if is_iface:
					sys.exit("line " + get_line_and_column(value) + " An Iface has to contain key value pairs, or be set to a configuration type (" + \
						", ".join(predefined_config_types) + ")")
				'''
			except NaCl_exception as e:
				exit_NaCl(value, e.value)
				# sys.exit("line " + get_line_and_column(value) + " A " + class_name + " has to contain key value pairs")

		'''
		elif value.value_name() is not None:
			# Do something if is Iface, but if is other class look at the else-functionality below:
			# sys.exit(... has to contain key value pairs)
			try:
				self.add_value_name(value)
				# So if the class does not allow value_names (constant values, f.ex. dhcp), throw exception?
			except Exception:
				sys.exit("line " + get_line_and_column(value) + " A " + class_name + " has to contain key value pairs")
		else:
			if is_iface:
				sys.exit("line " + get_line_and_column(value) + " An Iface has to contain key value pairs, or be set to a configuration type (" + \
					", ".join(predefined_config_types) + ")")
			else:
				sys.exit("line " + get_line_and_column(value) + " A " + class_name + " has to contain key value pairs")
		'''

	def process_assignments(self):
		# Loop through elements that are assignments
		# Find assignments (f.ex. x.y: <value> or x.y.z: <value>) that refers to this Element

		class_name = self.get_class_name()
		# Old:
		'''
		is_lb_untyped_conntrack_or_syslog = isinstance(self, Untyped) or isinstance(self, Load_balancer) or \
			isinstance(self, Conntrack) or isinstance(self, Syslog)
		is_gateway = isinstance(self, Gateway)
		'''
		# New: use self.handle_as_untyped instead

		# Handle assignments in the order of number of name parts to facilitate that you can have two assignments
		# where one is creating a member with an object as a value, while the other adds another element (key and value)
		# to that members object

		# Get the keys of all the assignment elements that manipulates this Element's members
		# If the name of the assignment element (= dictionary key) starts with the name of this Element and a DOT,
		# we know we have to do with an assignment element that manipulates this Element
		assignments_to_process = [key for key in self.nacl_state.elements if key.startswith(self.name + DOT)]

		if len(assignments_to_process) > 1:
			# Sorting the list based on length of element.name of each assignment element (shortest first)
			assignments_to_process = sorted(assignments_to_process, key=lambda k: len(k.split(DOT)))

		for key in assignments_to_process:
			# New:
			self.process_assignment(key)

			'''
			# Old:
			element = elements.get(key)

			# Old:
			# if is_lb_untyped_conntrack_or_syslog:
			# New:
			if self.handle_as_untyped:
				self.process_assignment(element)
			elif is_gateway:
				# Old:
				# self.process_gateway_assignment(element)
				# New:
				self.process_assignment(element)
			else:
			'''
			'''
				# Override process_assignment in Iface and Vlan with (moved to class Common in iface module:
				name_parts = key.split(DOT)
				orig_member = name_parts[1]
				member = orig_member.lower()

				if len(name_parts) != 2:
					exit_NaCl(element.ctx, "Invalid " + class_name + " member " + element.name)

				# TODO: Call validate_key (same as in process_ctx)
				# New:
				try:
					self.validate_key(orig_member)
				except NaCl_exception as e:
					exit_NaCl(element.ctx, e.value)
				# Old:
				# TODO: Vlan and Conntrack validate_key
			'''
			'''
				if (isinstance(self, Iface) and member not in predefined_iface_keys) or \
					(isinstance(self, Vlan) and member not in predefined_vlan_keys) or \
					(isinstance(self, Conntrack) and member not in predefined_conntrack_keys):
					# Note: If Conntrack: Would have never come here because of if above
					sys.exit("line " + get_line_and_column(element.ctx) + " Invalid " + class_name + " member " + orig_member)
			'''
			'''
				if self.members.get(member) is not None:
					exit_NaCl(element.ctx, "Member " + member + " has already been set")

				# New:
				found_element_value = element.ctx.value()
				try:
					self.add_member(member, found_element_value)
				except NaCl_exception as e:
					exit_NaCl(element.ctx, e.value)
				# Old:
			'''
			'''
				found_element_value = element.ctx.value()
				if isinstance(self, Iface) and member in chains:
					self.process_push(member, found_element_value)
				else:
					if self.members.get(member) is None:
						self.members[member] = found_element_value
					else:
						sys.exit("line " + get_line_and_column(element.ctx) + " " + class_name + " member " + member + " has already been set")
			'''

	# ---------- Methods related to dictionary self.members for Untyped, Load_balancer, Conntrack and Syslog ----------

	def process_assignment(self, element_key):
		# Could be either Untyped, Load_balancer, Conntrack or Syslog

		element = self.nacl_state.elements.get(element_key)

		# Remove first part (the name of this element)
		assignment_name_parts = element.name.split(DOT)
		assignment_name_parts.pop(0)

		# Check if this key has already been set in this element
		# In that case: Error: Value already set
		if self.get_dictionary_val(self.members, list(assignment_name_parts), element.ctx) is not None:
			exit_NaCl(element.ctx, "Member " + element.name + " has already been set")
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
					exit_NaCl_custom_line_and_column(line_and_column, level_key + "." + key_list[1] + " does not exist")

				# key_list.pop(0) # Remove first key (level_key) - has been found
				# return self.get_dictionary_val(new_dict, key_list, error_ctx)
				# We don't want to modify the input parameter
				return self.get_dictionary_val(new_dict, key_list[1:], error_ctx)

	def validate_dictionary_key(self, key, parent_key, level, value_ctx):
		exit_NaCl(value_ctx, "Internal error: The class " + self.get_class_name() + " needs to override the method " + \
			"validate_dictionary_key")

	def resolve_dictionary_value(self, dictionary, key, value_ctx):
		exit_NaCl(value_ctx, "Internal error: The class " + self.get_class_name() + " needs to override the method " + \
			"resolve_dictionary_value")

	def add_dictionary_val(self, dictionary, key_list, value, level=1, parent_key=""):
		# Old:
		'''
		is_lb = isinstance(self, Load_balancer)
		is_conntrack = isinstance(self, Conntrack)
		is_syslog = isinstance(self, Syslog)

		level_key = key_list[0] if not is_lb and not is_conntrack and not is_syslog else key_list[0].lower()
		'''
		# New:
		level_key = key_list[0] if self.handle_as_untyped else key_list[0].lower()
		# TODO: The other way around?
		# level_key = key_list[0] if not self.handle_as_untyped else key_list[0].lower()

		# End of recursion condition
		if len(key_list) == 1:
			if value.obj() is not None:
				# Then the value is a new dictionary
				dictionary[level_key] = {} # Create new dictionary
				return self.process_obj(dictionary[level_key], value.obj(), (level + 1), level_key)
			else:
				# Old:
				'''
				if is_lb:
					self.validate_lb_key(level_key, parent_key, level, value) # sys.exit on error
					self.resolve_lb_value(dictionary, level_key, value)
				elif is_conntrack:
					self.validate_conntrack_key(level_key, parent_key, level, value) # sys.exit on error
					self.resolve_conntrack_value(dictionary, level_key, value)
				elif is_syslog:
					self.validate_syslog_key(level_key, parent_key, level, value) # sys.exit on error
					self.resolve_syslog_value(dictionary, level_key, value)
				else:
					dictionary[level_key] = resolve_value(LANGUAGE, value)
				'''
				# New:
				if self.handle_as_untyped:
					# self.validate_and_resolve_dictionary_val(dictionary, level_key, parent_key, level, value)
					self.validate_dictionary_key(level_key, parent_key, level, value)
					self.resolve_dictionary_value(dictionary, level_key, value)
				else:
					dictionary[level_key] = self.nacl_state.resolve_value(value)
				return

		if level_key not in dictionary:
			exit_NaCl(value, "Trying to add to a member (" + level_key + ") that doesn't exist")

		for key in dictionary:
			if key == level_key:
				# key_list.pop(0) # Remove first key (level_key) - has been found
				# return self.add_dictionary_val(dictionary[key], key_list, value, level, level_key)
				# We don't want to modify the input parameter
				return self.add_dictionary_val(dictionary[key], key_list[1:], value, level, level_key)

	def process_obj(self, dictionary, ctx, level=1, parent_key=""):
		# Could be either Untyped, Load_balancer, Conntrack or Syslog
		# Level only relevant for Load_balancer, Conntrack and Syslog

		# Old:
		'''
		is_lb = isinstance(self, Load_balancer)
		is_conntrack = isinstance(self, Conntrack)
		is_syslog = isinstance(self, Syslog)
		'''

		for pair in ctx.key_value_list().key_value_pair():
			# Old:
			# key = pair.key().getText() if not is_lb and not is_conntrack and not is_syslog else pair.key().getText().lower()
			# New:
			key = pair.key().getText() if self.handle_as_untyped else pair.key().getText().lower()

			if dictionary.get(key) is not None:
				exit_NaCl(pair.key(), "Member " + key + " has already been set")

			# Validate key

			# Old:
			'''
			if is_lb:
				self.validate_lb_key(key, parent_key, level, pair.key()) # sys.exit on error
			elif is_conntrack:
				self.validate_conntrack_key(key, parent_key, level, pair.key()) # sys.exit on error
			elif is_syslog:
				self.validate_syslog_key(key, parent_key, level, pair.key()) # sys.exit on error
			'''
			# New:
			if self.handle_as_untyped:
				self.validate_dictionary_key(key, parent_key, level, pair.key())

			# End of recursion:
			if pair.value().obj() is None:
				# Old:
				'''
				if is_lb:
					self.resolve_lb_value(dictionary, key, pair.value())
				elif is_conntrack:
					self.resolve_conntrack_value(dictionary, key, pair.value())
				elif is_syslog:
					self.resolve_syslog_value(dictionary, key, pair.value())
				'''
				# New:
				if self.handle_as_untyped:
					self.resolve_dictionary_value(dictionary, key, pair.value())
				else:
					dictionary[key] = self.nacl_state.resolve_value(pair.value())
			else:
				# Recursion:
				# Then we have an obj inside an obj
				dictionary[key] = {} # creating new dictionary
				# loop through the obj and fill the new dictionary
				self.process_obj(dictionary[key], pair.value().obj(), (level + 1), key)

# < Element

# -------------------- Untyped --------------------

class Untyped(Element):
	def __init__(self, nacl_state, idx, name, ctx, base_type):
		super(Untyped, self).__init__(nacl_state, idx, name, ctx, base_type)

	# Overriding
	def validate_dictionary_key(self, key, parent_key, level, value_ctx):
		pass

	# Overriding
	def resolve_dictionary_value(self, dictionary, key, value_ctx):
		dictionary[key] = self.nacl_state.resolve_value(value_ctx)

	# Main processing method
	def process(self):
		if self.res is None:
			name_parts = self.name.split(DOT)

			if len(name_parts) > 1:
				# This is an assignment to an already existing element
				element_name = name_parts[0]
				if self.nacl_state.elements.get(element_name) is None:
					exit_NaCl(self.ctx, "No element with the name " + element_name + " exists")
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
	def __init__(self, nacl_state, idx, name, ctx, base_type, type_t):
		super(Typed, self).__init__(nacl_state, idx, name, ctx, base_type)
		self.type_t = type_t

# < Typed

'''
# -------------------- Conntrack --------------------

class Conntrack(Typed):
	def __init__(self, nacl_state, idx, name, ctx, base_type, type_t):
		super(Conntrack, self).__init__(nacl_state, idx, name, ctx, base_type, type_t)

	def add_conntrack(self):
		timeout = self.members.get(CONNTRACK_KEY_TIMEOUT)
		timeouts = []

		if timeout is not None:
			class_name = self.get_class_name()

			if not isinstance(timeout, dict):
				exit_NaCl(self.ctx, "Invalid " + CONNTRACK_KEY_TIMEOUT + " value of " + class_name + \
					" (needs to be an object)")

			for conntrack_type in timeout:
				t = timeout.get(conntrack_type)

				if not isinstance(t, dict):
					exit_NaCl(self.ctx, "Invalid " + conntrack_type + " value of " + class_name + \
						" (needs to be an object)")

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
				exit_NaCl(ctx, "Invalid " + class_name + " member " + key)
			return

		if parent_key == "":
			exit_NaCl(ctx, "Internal error: Parent key of " + key + " has not been given")

		if level == 2:
			if parent_key == CONNTRACK_KEY_TIMEOUT and key not in predefined_conntrack_timeout_keys:
				exit_NaCl(ctx, "Invalid " + class_name + " member " + key + " in " + self.name + "." + parent_key)
		elif level == 3:
			if parent_key not in predefined_conntrack_timeout_keys:
				exit_NaCl(ctx, "Internal error: Invalid parent key " + parent_key + " of " + key)
			if key not in predefined_conntrack_timeout_inner_keys:
				exit_NaCl(ctx, "Invalid " + class_name + " member " + key)
		else:
			exit_NaCl(ctx, "Invalid " + class_name + " member " + key)

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
'''

'''
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
'''

'''
# -------------------- Vlan --------------------

class Vlan(Typed):
	def __init__(self, nacl_state, idx, name, ctx, base_type, type_t):
		super(Vlan, self).__init__(nacl_state, idx, name, ctx, base_type, type_t)

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
'''

'''
# -------------------- Gateway --------------------

class Gateway(Typed):
	def __init__(self, nacl_state, idx, name, ctx, base_type, type_t):
		super(Gateway, self).__init__(nacl_state, idx, name, ctx, base_type, type_t)

		self.handle_as_untyped = False

		# New:
		self.pushes = []

		# self.members (in Element) to contain this Gateway's members as defined in NaCl file
		# Key: Name of route
		# Value: pystache route object

		self.not_route_members = {}

	def get_pystache_route_obj(self, name, route_ctx):
		route_obj = { "ctx": route_ctx }
		pairs = route_ctx.key_value_list().key_value_pair()

		for pair in pairs:
			orig_key = pair.key().getText()
			key = orig_key.lower()

			if route_obj.get(key) is not None:
				exit_NaCl(pair.key(), "Member " + key + " has already been set for route " + name)

			if key not in predefined_gateway_route_keys:
				exit_NaCl(pair.key(), orig_key + " is not a valid Gateway route member. " + \
					"Valid members are: " + ", ".join(predefined_gateway_route_keys))

			if key != GATEWAY_KEY_IFACE:
				route_obj[key] = self.nacl_state.resolve_value(pair.value())
			else:
				# Then the Iface element's name is to be added to the route_obj,
				# not the resolved Iface
				iface_name = pair.value().getText()

				if pair.value().value_name() is None:
					exit_NaCl(pair.value(), "Gateway route member iface contains an invalid value (" + iface_name + ")")

				element = elements.get(iface_name)
				if element is None or (hasattr(element, 'type_t') and element.type_t.lower() != TYPE_IFACE):
					exit_NaCl(pair.value(), "No Iface with the name " + iface_name + " exists")

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
					exit_NaCl(route_pair, "Invalid Gateway member " + orig_name)

				if name == GATEWAY_KEY_SEND_TIME_EXCEEDED or name == GATEWAY_KEY_FORWARD:
					if self.not_route_members.get(name) is not None:
						exit_NaCl(route_pair, name + " has already been set")
					self.not_route_members[name] = route_pair.value()
					continue

				if self.members.get(name) is not None:
					exit_NaCl(route_pair, "Route " + name + " has already been set")

				if route_pair.value().obj() is None:
					exit_NaCl(route_pair.value(), "A Gateway's routes must be objects (containing key value pairs)")

				# Add pystache route obj to members dictionary
				self.members[name] = self.get_pystache_route_obj(name, route_pair.value().obj())
		elif value.list_t() is not None:
			for i, val in enumerate(value.list_t().value_list().value()):
				if val.obj() is None:
					exit_NaCl(val, "A Gateway that constitutes a list must be a list of objects (containing key value pairs)")

				# Add pystache route obj to members dictionary
				# When unnamed routes, use index as key
				self.members[i] = self.get_pystache_route_obj(str(i), val.obj())
		else:
			exit_NaCl(value, "A Gateway must contain key value pairs (in which each pair's value is an object), or " + \
				"it must contain a list of objects")

	# Called in Element's process_assignments method
	# Old:
	# def process_gateway_assignment(self, element):
	# New:
	# Overriding:
	def process_assignment(self, element_key):
		element = elements.get(element_key)

		name_parts = element.name.split(DOT)
		orig_member = name_parts[1]
		member = orig_member.lower()
		num_name_parts = len(name_parts)

		if num_name_parts > 3:
			exit_NaCl(element.ctx, "Invalid Gateway member " + element.name)
		elif self.members.get(0) is not None:
			exit_NaCl(element.ctx, "Trying to access a named member in a Gateway without named members (" + element.name + ")")
			# Could support later: gateway.0.netmask: 255.255.255.0

		if num_name_parts == 2:
			# members:
			if member != GATEWAY_KEY_SEND_TIME_EXCEEDED and member != GATEWAY_KEY_FORWARD:
				# Then the user is adding an additional route to this Gateway
				# F.ex. gateway.r6: <value>
				if self.members.get(member) is None:
					# Then add the route if valid
					if element.ctx.value().obj() is None:
						exit_NaCl(element.ctx.value(), "A Gateway member's value needs to contain key value pairs")
					self.members[member] = self.get_pystache_route_obj(element.name, element.ctx.value().obj())
				else:
					exit_NaCl(element.ctx, "Gateway member " + member + " has already been set")
			# not_route_members:
			else:
				if self.not_route_members.get(member) is None:
					self.not_route_members[member] = element.ctx.value()
				else:
					exit_NaCl(element.ctx.value(), "Gateway member " + member + " has already been set")
		else:
			# Then num_name_parts are 3 and we're talking about adding a member to a route
			route = self.members.get(member)
			if route is None:
				exit_NaCl(element.ctx, "No member named " + member + " in Gateway " + self.name)

			route_member = name_parts[2].lower()

			if route.get(route_member) is not None:
				exit_NaCl(element.ctx, "Member " + route_member + " in route " + member + " has already been set")

			if route_member not in predefined_gateway_route_keys:
				exit_NaCl(element.ctx, route_member + " is not a valid Gateway route member. Valid members are: " + \
					", ".join(predefined_gateway_route_keys))

			if route_member != GATEWAY_KEY_IFACE:
				route[route_member] = self.nacl_state.resolve_value(element.ctx.value())
			else:
				# Then the Iface element's name is to be added to the route obj,
				# not the resolved Iface
				iface_name = element.ctx.value().getText()

				if element.ctx.value().value_name() is None:
					exit_NaCl(element.ctx.value(), "Invalid iface value " + iface_name + " (the value must be the name of an Iface)")

				iface_element = elements.get(iface_name)
				if iface_element is None or (hasattr(iface_element, 'type_t') and iface_element.type_t.lower() != TYPE_IFACE):
					exit_NaCl(element.ctx.value(), "No Iface with the name " + iface_name + " exists")

				route[route_member] = iface_name

	def process_push(self, chain, value_ctx):
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
				exit_NaCl(function, "No function with the name " + name + " exists")

			if element.type_t.lower() == TYPE_NAT:
				exit_NaCl(function, "A Nat function cannot be pushed onto a Gateway's forward chain")

			function_names.append({TEMPLATE_KEY_FUNCTION_NAME: name, TEMPLATE_KEY_COMMA: (i < (num_functions - 1))})

		# Old:
		# pushes.append({
		#	TEMPLATE_KEY_IS_GATEWAY_PUSH: 	True,
		#	TEMPLATE_KEY_NAME:				get_router_name(LANGUAGE),
		#	TEMPLATE_KEY_CHAIN: 			chain,
		#	TEMPLATE_KEY_FUNCTION_NAMES: 	function_names
		# })
		# New:
		self.pushes.append({
			# TEMPLATE_KEY_IS_GATEWAY_PUSH: 	True,
			TEMPLATE_KEY_NAME:				self.nacl_state.get_router_name(),
			TEMPLATE_KEY_CHAIN: 			chain,
			TEMPLATE_KEY_FUNCTION_NAMES: 	function_names
		})

	def validate_and_process_not_route_members(self):
		for key, value_ctx in self.not_route_members.iteritems():
			if key == GATEWAY_KEY_SEND_TIME_EXCEEDED:
				resolved_value = self.nacl_state.resolve_value(value_ctx)
				self.not_route_members[key] = resolved_value

				if resolved_value != TRUE and resolved_value != FALSE:
					exit_NaCl(value_ctx, "Invalid value of " + key + " (" + resolved_value + \
						"). Must be set to " + TRUE + " or " + FALSE)
			elif key == GATEWAY_KEY_FORWARD:
				self.process_push(key, value_ctx)

	def process_members(self):
		routes = []
		index = 0
		num_routes = len(self.members)

		# New:
		from type_processors.iface import TEMPLATE_KEY_ENABLE_CT_IFACES

		for _, route in self.members.iteritems():
			if GATEWAY_KEY_NETMASK not in route or \
				GATEWAY_KEY_IFACE not in route or \
				(GATEWAY_KEY_NET not in route and GATEWAY_KEY_HOST not in route):
				exit_NaCl(route.get("ctx"), "A Gateway route must specify " + GATEWAY_KEY_IFACE + ", " + \
					GATEWAY_KEY_NETMASK + " and either " + GATEWAY_KEY_NET + " or " + GATEWAY_KEY_HOST)

			# Add iface_name to ip_forward_ifaces pystache list if it is not in the
			# list already
			iface_name = route.get(GATEWAY_KEY_IFACE)
			if iface_name is not None and not any(ip_forward_iface[TEMPLATE_KEY_IFACE] == iface_name for ip_forward_iface in ip_forward_ifaces):
				ip_forward_ifaces.append({TEMPLATE_KEY_IFACE: iface_name})

			# Add iface_name to enable_ct_ifaces pystache list if it is not in the
			# list already
			# Old:
			# if iface_name is not None and not any(enable_ct_iface[TEMPLATE_KEY_IFACE] == iface_name for enable_ct_iface in enable_ct_ifaces):
			#	enable_ct_ifaces.append({TEMPLATE_KEY_IFACE: iface_name})
			# New:
			if iface_name is not None and not self.nacl_state.exists_in_pystache_list(TEMPLATE_KEY_ENABLE_CT_IFACES, TEMPLATE_KEY_IFACE, iface_name):
				self.nacl_state.append_to_pystache_data_list(TEMPLATE_KEY_ENABLE_CT_IFACES, {
					TEMPLATE_KEY_IFACE: iface_name
				})

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

			# New:
			# Add self.pushes to pystache data:
			self.nacl_state.register_pystache_data_object(TEMPLATE_KEY_GATEWAY_PUSHES, self.pushes)

		return self.res

	# Called from handle_input (NaCl.py) right before rendering, after the NaCl file has been processed
	# Register the last data here that can not be registered before this (set has-values f.ex.)
	@staticmethod
	def final_registration(nacl_state):
		gateways_is_empty = nacl_state.pystache_list_is_empty(TEMPLATE_KEY_GATEWAYS)

		# handle_input previously:
		# nacl_state.register_pystache_data_object(TEMPLATE_KEY_ENABLE_CT, (len(nats) > 0 or len(filters) > 0 or len(gateways) > 0))
		if not gateways_is_empty:
			nacl_state.register_pystache_data_object(TEMPLATE_KEY_ENABLE_CT, True)

# < Gateway
'''

'''
# -------------------- Load_balancer --------------------

class Load_balancer(Typed):
	def __init__(self, nacl_state, idx, name, ctx, base_type, type_t):
		super(Load_balancer, self).__init__(nacl_state, idx, name, ctx, base_type, type_t)

	def add_load_balancer(self):
		# Note: This method also validates that all the mandatory fields have been set
		# Note: The value has already been validated in process_ctx and process_assignments
		# Note: Only allowed to create one Load_balancer per layer

		layer = self.members.get(LB_KEY_LAYER)
		if layer is None:
			exit_NaCl(self.ctx, "Load_balancer member " + LB_KEY_LAYER + " has not been set")
		if any(lb[TEMPLATE_KEY_LB_LAYER] == layer for lb in load_balancers):
			exit_NaCl(self.ctx, "A " + layer.upper() + " Load_balancer has already been defined")

		clients = self.members.get(LB_KEY_CLIENTS)
		if clients is None:
			exit_NaCl(self.ctx, "Load_balancer member " + LB_KEY_CLIENTS + " has not been set")
		if not isinstance(clients, dict):
			exit_NaCl(self.ctx, "Invalid value of Load_balancer member " + LB_KEY_CLIENTS + \
				". It needs to be an object containing " + ", ".join(predefined_lb_clients_keys))

		servers = self.members.get(LB_KEY_SERVERS)
		if servers is None:
			exit_NaCl(self.ctx, "Load_balancer member " + LB_KEY_SERVERS + " has not been set")
		if not isinstance(servers, dict):
			exit_NaCl(self.ctx, "Invalid value of Load_balancer member " + LB_KEY_SERVERS + \
				". It needs to be an object containing " + ", ".join(predefined_lb_servers_keys))

		# Clients

		clients_iface_name = clients.get(LB_KEY_IFACE)
		if clients_iface_name is None:
			exit_NaCl(self.ctx, "Load_balancer member " + LB_KEY_CLIENTS + "." + LB_KEY_IFACE + " has not been set")

		port = clients.get(LB_KEY_PORT)
		if port is None:
			exit_NaCl(self.ctx, "Load_balancer member " + LB_KEY_CLIENTS + "." + LB_KEY_PORT + " has not been set")

		waitq_limit = clients.get(LB_CLIENTS_KEY_WAIT_QUEUE_LIMIT)
		if waitq_limit is None:
			waitq_limit = 1000

		session_limit = clients.get(LB_CLIENTS_KEY_SESSION_LIMIT)
		if session_limit is None:
			session_limit = 1000

		# Servers

		servers_iface_name = servers.get(LB_KEY_IFACE)
		if servers_iface_name is None:
			exit_NaCl(self.ctx, "Load_balancer member " + LB_KEY_SERVERS + "." + LB_KEY_IFACE + " has not been set")

		algo = servers.get(LB_SERVERS_KEY_ALGORITHM)
		if algo is None:
			exit_NaCl(self.ctx, "Load_balancer member " + LB_KEY_SERVERS + "." + LB_SERVERS_KEY_ALGORITHM + " has not been set")

		# pool is a list of nodes/servers, containing address and port
		pool = servers.get(LB_SERVERS_KEY_POOL)
		if pool is None:
			exit_NaCl(self.ctx, "Load_balancer member " + LB_KEY_SERVERS + "." + LB_SERVERS_KEY_POOL + " has not been set")
		if not isinstance(pool, list):
			exit_NaCl(self.ctx, "Invalid value of Load_balancer member " + LB_KEY_SERVERS + "." + LB_SERVERS_KEY_POOL + \
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
			TEMPLATE_KEY_PORT: 					port,
			TEMPLATE_KEY_LB_CLIENTS_IFACE: 		clients_iface_name,
			TEMPLATE_KEY_LB_SERVERS_IFACE: 		servers_iface_name,
			TEMPLATE_KEY_LB_POOL: 				pystache_pool
		})

	# Old:
	# def validate_lb_key(self, key, parent_key, level, ctx):
	# New:
	# Overriding
	def validate_dictionary_key(self, key, parent_key, level, value_ctx):
		class_name = self.get_class_name()

		if level == 1:
			if key not in predefined_lb_keys:
				exit_NaCl(value_ctx, "Invalid " + class_name + " member " + key)
		elif level == 2:
			if parent_key == "":
				exit_NaCl(value_ctx, "Internal error: Parent key of " + key + " has not been given")
			if parent_key == LB_KEY_CLIENTS and key not in predefined_lb_clients_keys:
				exit_NaCl(value_ctx, "Invalid " + class_name + " member " + key + " in " + self.name + "." + parent_key)
			if parent_key == LB_KEY_SERVERS and key not in predefined_lb_servers_keys:
				exit_NaCl(value_ctx, "Invalid " + class_name + " member " + key + " in " + self.name + "." + parent_key)
		else:
			exit_NaCl(value_ctx, "Invalid " + class_name + " member " + key)

	# Old:
	# def resolve_lb_value(self, dictionary, key, value):
	# New:
	# Overriding
	def resolve_dictionary_value(self, dictionary, key, value_ctx):
		class_name = self.get_class_name()
		found_element_value = value_ctx.getText()

		if key == LB_KEY_LAYER or key == LB_SERVERS_KEY_ALGORITHM:
			found_element_value = found_element_value.lower()

		if key == LB_KEY_LAYER:
			if value_ctx.value_name() is None or found_element_value not in valid_lb_layers:
				exit_NaCl(value_ctx, "Invalid " + LB_KEY_LAYER + " value (" + value_ctx.getText() + ")")
		elif key == LB_KEY_IFACE:
			# Then the Iface element's name is to be added, not the resolved Iface
			if value_ctx.value_name() is None:
				exit_NaCl(value_ctx, class_name + " member " + LB_KEY_IFACE + " contains an invalid value (" + \
					found_element_value + ")")
			element = elements.get(found_element_value)
			if element is None or (hasattr(element, 'type_t') and element.type_t.lower() != TYPE_IFACE):
				exit_NaCl(value_ctx, "No Iface with the name " + found_element_value + " exists")
		elif key == LB_SERVERS_KEY_ALGORITHM:
			if value_ctx.value_name() is None or found_element_value not in valid_lb_servers_algos:
				exit_NaCl(value_ctx, "Invalid algorithm " + value_ctx.getText())
		elif key == LB_SERVERS_KEY_POOL:
			if value_ctx.list_t() is None and value_ctx.value_name() is None:
				exit_NaCl(value_ctx, "Invalid " + LB_SERVERS_KEY_POOL + " value. It needs to be a list of objects or the name " + \
					"of a list of objects containing " + ", ".join(predefined_lb_node_keys))

			if value_ctx.value_name() is not None:
				element_name = value_ctx.value_name().getText()
				e = elements.get(element_name)
				if e is None:
					exit_NaCl(value_ctx, "No element with the name " + element_name + " exists")
				if e.ctx.value().list_t() is None:
					exit_NaCl(value_ctx, "Element " + element_name + " does not consist of a list")
				# Updating value_ctx to be the element e's ctx value
				value_ctx = e.ctx.value()

			pool = []
			for i, node in enumerate(value_ctx.list_t().value_list().value()):
				if node.obj() is None and node.value_name() is None:
					exit_NaCl(node, "Invalid " + LB_SERVERS_KEY_POOL + " value. It needs to be a list of objects containing " + \
						", ".join(predefined_lb_node_keys))

				if node.value_name() is not None:
					element_name = node.value_name().getText()
					e = elements.get(element_name)
					if e is None:
						exit_NaCl(node, "No element with the name " + element_name + " exists")
					if e.ctx.value().obj() is None:
						exit_NaCl(node, "Element " + element_name + " must be an object")
					node = e.ctx.value()

				n = {}
				n[TEMPLATE_KEY_INDEX] = i
				for pair in node.obj().key_value_list().key_value_pair():
					node_key = pair.key().getText().lower()
					if node_key not in predefined_lb_node_keys:
						exit_NaCl(pair.key(), "Invalid member in node " + str(i) + " in " + LB_KEY_SERVERS + "." + LB_SERVERS_KEY_POOL)
					n[node_key] = self.nacl_state.resolve_value(pair.value())

				if n.get(LB_NODE_KEY_ADDRESS) is None or n.get(LB_KEY_PORT) is None:
					exit_NaCl(node, "An object in a " + LB_SERVERS_KEY_POOL + " needs to specify " + ", ".join(predefined_lb_node_keys))

				pool.append(n)

			found_element_value = pool
		elif key == LB_KEY_CLIENTS or key == LB_KEY_SERVERS:
			if value_ctx.value_name() is not None:
				element_name = value_ctx.value_name().getText()
				e = elements.get(element_name)
				if e is None:
					exit_NaCl(value_ctx, "No element with the name " + element_name + " exists")
				if e.ctx.value().obj() is None:
					exit_NaCl(value_ctx, "Element " + element_name + " must be an object")
				# Updating value_ctx to be the element e's ctx value
				value_ctx = e.ctx.value()

			if value_ctx.obj() is None:
				mandatory_keys = ", ".join(predefined_lb_clients_keys) if key == LB_KEY_CLIENTS else ", ".join(predefined_lb_servers_keys)
				exit_NaCl(value_ctx, "Invalid " + key + " value. It needs to be an object containing " + mandatory_keys)

			found_element_value = {}
			for pair in value_ctx.obj().key_value_list().key_value_pair():
				k = pair.key().getText().lower()
				# Validate the key first
				# Old:
				# self.validate_lb_key(k, key, 2, value_ctx)
				# New:
				self.validate_dictionary_key(k, key, 2, value_ctx)
				# Then resolve the value
				# Old:
				# self.resolve_lb_value(found_element_value, k, pair.value())
				# New:
				self.resolve_dictionary_value(found_element_value, k, pair.value())
		else:
			found_element_value = self.nacl_state.resolve_value(value_ctx)

		# Add found value
		dictionary[key] = found_element_value

	# Overriding
	# def validate_and_resolve_dictionary_val(self, dictionary, level_key, parent_key, level, value):
	#	self.validate_lb_key(level_key, parent_key, level, value)
	#	self.resolve_lb_value(dictionary, level_key, value)

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
'''

'''
# -------------------- Syslog (settings) --------------------

class Syslog(Typed):
	def __init__(self, nacl_state, idx, name, ctx, base_type, type_t):
		super(Syslog, self).__init__(nacl_state, idx, name, ctx, base_type, type_t)

	def add_syslog(self):
		addr = self.members.get(SYSLOG_KEY_ADDRESS)
		port = self.members.get(SYSLOG_KEY_PORT)

		if addr is None or port is None:
			exit_NaCl(self.ctx, "Syslog address and/or port have not been specified")

		syslogs.append({ TEMPLATE_KEY_ADDRESS: addr, TEMPLATE_KEY_PORT: port })

	# Old:
	# def validate_syslog_key(self, key, parent_key, level, ctx):
	# New:
	# Overriding
	def validate_dictionary_key(self, key, parent_key, level, value_ctx):
		class_name = self.get_class_name()
		if level == 1:
			if key not in predefined_syslog_keys:
				exit_NaCl(value_ctx, "Invalid " + class_name + " member " + key)
		else:
			exit_NaCl(value_ctx, "Invalid " + class_name + " member " + key)

	# Old:
	# def resolve_syslog_value(self, dictionary, key, value):
	# New:
	# Overriding
	def resolve_dictionary_value(self, dictionary, key, value):
		dictionary[key] = self.nacl_state.resolve_value(value)

	# Overriding
	# def validate_and_resolve_dictionary_val(self, dictionary, level_key, parent_key, level, value):
	#	self.validate_syslog_key(level_key, parent_key, level, value)
	#	self.resolve_syslog_value(dictionary, level_key, value)

	def process(self):
		if self.res is None:
			# Then process

			self.process_ctx()
			self.process_assignments()
			self.add_syslog()

			self.res = self.members

		return self.res

# < Syslog (settings)
'''

'''
# -------------------- Function --------------------

# Filter and Nat are examples of functions

class Function(Element):
	def __init__(self, nacl_state, idx, name, ctx, base_type, type_t, subtype):
		super(Function, self).__init__(nacl_state, idx, name, ctx, base_type)
		self.type_t 	= type_t
		self.subtype 	= subtype

		self.handle_as_untyped = False # Probably not relevant at all, but in case

	def add_function(self):
		# Only if a function is mentioned in an assignment that is a push or
		# an Iface's chain, should it be added to filters/nats/rewrites pystache list

		pystache_function_obj = {
			TEMPLATE_KEY_NAME: 		self.name,
			TEMPLATE_KEY_TITLE: 	self.name.title(),
			TEMPLATE_KEY_CONTENT: 	self.res 	# Contains transpiled content
		}

		# Old:
		# for p in pushes:
		# Old 2:
		# for p in self.nacl_state.pushes:
		# New:
		# TODO: Constant
		TEMPLATE_KEY_IFACE_PUSHES = "pushes_iface"
		iface_pushes = self.nacl_state.pystache_data.get(TEMPLATE_KEY_IFACE_PUSHES)
		gateway_pushes = self.nacl_state.pystache_data.get(TEMPLATE_KEY_GATEWAY_PUSHES)

		# TODO: Reuse content of for loop - move to separate method (same as below)
		if iface_pushes is not None:
			for p in iface_pushes:
				for f in p[TEMPLATE_KEY_FUNCTION_NAMES]:
					if self.name == f[TEMPLATE_KEY_FUNCTION_NAME]:
						# Then we know that this function is called in the C++ code
						# And the function should be added to the correct pystache list
						type_t_lower = self.type_t.lower()

						# Display an error message if the function is a Filter and does not end in a default verdict
						if type_t_lower == TYPE_FILTER:
							if self.subtype.lower() != IP:
								exit_NaCl(self.ctx, "Only a function of subtype IP can be pushed onto an Iface's chain. " + \
									"However, you can create and call Filters of any subtype inside an IP Filter")

							elements = list(self.ctx.body().body_element())
							last_element = elements[len(elements) - 1]
							if last_element.action() is None or last_element.action().getText() not in valid_default_filter_verdicts:
								exit_NaCl(self.ctx, "Missing default verdict at the end of this Filter")

						if type_t_lower == TYPE_FILTER:
							filters.append(pystache_function_obj)
						elif type_t_lower == TYPE_NAT:
							nats.append(pystache_function_obj)
						elif type_t_lower == TYPE_REWRITE:
							rewrites.append(pystache_function_obj)
						else:
							exit_NaCl(self.ctx.type_t(), "Functions of type " + self.type_t + " are not handled")
						return self.res
		# New: ADDED: And the same for pushes_gateway?:
		# TODO: Reuse the content - move to separate method
		if gateway_pushes is not None:
			for p in gateway_pushes:
				for f in p[TEMPLATE_KEY_FUNCTION_NAMES]:
					if self.name == f[TEMPLATE_KEY_FUNCTION_NAME]:
						# Then we know that this function is called in the C++ code
						# And the function should be added to the correct pystache list
						type_t_lower = self.type_t.lower()

						# Display an error message if the function is a Filter and does not end in a default verdict
						if type_t_lower == TYPE_FILTER:
							if self.subtype.lower() != IP:
								exit_NaCl(self.ctx, "Only a function of subtype IP can be pushed onto an Iface's chain. " + \
									"However, you can create and call Filters of any subtype inside an IP Filter")

							elements = list(self.ctx.body().body_element())
							last_element = elements[len(elements) - 1]
							if last_element.action() is None or last_element.action().getText() not in valid_default_filter_verdicts:
								exit_NaCl(self.ctx, "Missing default verdict at the end of this Filter")

						if type_t_lower == TYPE_FILTER:
							filters.append(pystache_function_obj)
						elif type_t_lower == TYPE_NAT:
							nats.append(pystache_function_obj)
						elif type_t_lower == TYPE_REWRITE:
							rewrites.append(pystache_function_obj)
						else:
							exit_NaCl(self.ctx.type_t(), "Functions of type " + self.type_t + " are not handled")
						return self.res

	# Main processing method
	def process(self):
		if self.res is None:
			self.res = transpile_function(LANGUAGE, self.type_t, self.subtype, self.ctx)
			self.add_function()
		return self.res

# < Function
'''

# -------------------- 2. Process elements and write content to file --------------------

# nacl_types = {}
'''
nacl_types = {
	TYPE_IFACE: Iface,
	TYPE_VLAN: Vlan,
	TYPE_GATEWAY: Gateway,
	TYPE_CONNTRACK: Conntrack,
	TYPE_LOAD_BALANCER: Load_balancer,
	TYPE_SYSLOG: Syslog,
	TYPE_FILTER: Function,
	TYPE_REWRITE: Function,
	TYPE_NAT: Function
}
'''

# 1. Before visiting
'''
def register_all_type_processors():
	print "Register all type processors"
	# For each file in the type_processors folder, call the register function
	# from type_processors.iface import register
	#type_proc_dir = "type_processors"
	#import importlib
	# Call the register function in all type_processors
	#for filename in os.listdir(type_proc_dir):
	#	if filename.startswith("type") and filename.endswith(".py"):
	#		filename = filename[:-3] # remove .py
	#		path_to_file = os.path.join(type_proc_dir, filename)
	#		processor = importlib.import_module(path_to_file)
	#		processor.register()

	# import type_processors
	# type_processors.__init__()

	# from type_processors import __init__ as init
	# init()

	from type_processors import init as init_type_processors
	init_type_processors()
'''

# 2. Called by all type_processors when the register function is called
# in the register_all_type_processors function
'''
def register_type_processor(name, class_constructor):
	print "register_type_processor"
	print "Name:", name
	print "Class:", class_constructor
	nacl_types[name] = class_constructor

	print "Content of nacl_types after a register_type_processor: ", str(nacl_types)
'''

# -------------------- Pystache --------------------

# Connected to cpp_template.mustache
class Cpp_template(object):
	def __init__(self):
		pass

# ------------------ < Pystache ------------------

# Main function
# Called after all the elements in the NaCl text have been visited and saved in the elements dictionary
def handle_input(nacl_state):
	# print "handle_input - elements:", str(nacl_state.elements)

	# Process / transpile / fill the pystache lists
	function_elements = []
	for _, e in nacl_state.elements.iteritems():
		if e.base_type != BASE_TYPE_FUNCTION:
			e.process()
		else:
			function_elements.append(e)
	# When we arrive here, all the elements except the function elements have been processed
	for e in function_elements:
		e.process()

	# Old:
	# Create a data object containing all the pystache lists - to be sent to the
	# pystache Renderer's render method together with the cpp_template.mustache content
	# TODO: Push into this dictionary as well (from your class file)
	'''
	data = {
		# New:
		# TEMPLATE_KEY_IFACES: 				ifaces,
		# TEMPLATE_KEY_IFACES_WITH_VLANS: 	ifaces_with_vlans,
		TEMPLATE_KEY_CONNTRACKS: 			conntracks,
		TEMPLATE_KEY_LOAD_BALANCERS: 		load_balancers,
		TEMPLATE_KEY_SYSLOGS: 				syslogs,
		TEMPLATE_KEY_FILTERS: 				filters,
		TEMPLATE_KEY_NATS: 					nats,
		TEMPLATE_KEY_REWRITES: 				rewrites,
		# New:
		# TEMPLATE_KEY_PUSHES: 				pushes,
		TEMPLATE_KEY_GATEWAYS: 				gateways, # or only one gateway?
		TEMPLATE_KEY_IP_FORWARD_IFACES:		ip_forward_ifaces,
		TEMPLATE_KEY_ENABLE_CT_IFACES:		enable_ct_ifaces,
		TEMPLATE_KEY_MASQUERADES: 			masquerades,
		# New:
		# TEMPLATE_KEY_AUTO_NATTING_IFACES: 	auto_natting_ifaces,
		TEMPLATE_KEY_HAS_GATEWAYS: 			(len(gateways) > 0),
		TEMPLATE_KEY_HAS_NATS: 				(len(nats) > 0 or len(masquerades) > 0),
		TEMPLATE_KEY_HAS_MASQUERADES:		(len(masquerades) > 0),
		# New:
		# TEMPLATE_KEY_HAS_VLANS: 			(len(ifaces_with_vlans) > 0),
		# TEMPLATE_KEY_HAS_AUTO_NATTING_IFACES: (len(auto_natting_ifaces) > 0),
		TEMPLATE_KEY_HAS_FUNCTIONS: 		(len(nats) > 0 or len(filters) > 0),
		TEMPLATE_KEY_ENABLE_CT: 			(len(nats) > 0 or len(filters) > 0 or len(gateways) > 0),
		TEMPLATE_KEY_HAS_LOAD_BALANCERS: 	(len(load_balancers) > 0),
		TEMPLATE_KEY_HAS_SYSLOGS: 			(len(syslogs) > 0)
	}
	'''
	# New:
	# nacl_state.register_pystache_data_object(TEMPLATE_KEY_CONNTRACKS, conntracks)
	# New: Moved to load_balancer.py:
	# nacl_state.register_pystache_data_object(TEMPLATE_KEY_LOAD_BALANCERS, load_balancers)
	# New: Moved to syslog.py:
	# nacl_state.register_pystache_data_object(TEMPLATE_KEY_SYSLOGS, syslogs)
	# New: Moved to function.py:
	# nacl_state.register_pystache_data_object(TEMPLATE_KEY_FILTERS, filters)
	# nacl_state.register_pystache_data_object(TEMPLATE_KEY_NATS, nats)
	# nacl_state.register_pystache_data_object(TEMPLATE_KEY_REWRITES, rewrites)
	# New: Moved to gateway.py:
	# nacl_state.register_pystache_data_object(TEMPLATE_KEY_GATEWAYS, gateways)
	# New: Moved to gateway.py:
	# nacl_state.register_pystache_data_object(TEMPLATE_KEY_IP_FORWARD_IFACES, ip_forward_ifaces)
	# New:
	# nacl_state.register_pystache_data_object(TEMPLATE_KEY_ENABLE_CT_IFACES, enable_ct_ifaces)
	# nacl_state.register_pystache_data_object(TEMPLATE_KEY_MASQUERADES, masquerades)
	# New: Moved to gateway.py:
	# nacl_state.register_pystache_data_object(TEMPLATE_KEY_HAS_GATEWAYS, (len(gateways) > 0))
	# New: Moved into function.py and iface.py:
	# nacl_state.register_pystache_data_object(TEMPLATE_KEY_HAS_NATS, (len(nats) > 0 or len(masquerades) > 0))
	# nacl_state.register_pystache_data_object(TEMPLATE_KEY_HAS_MASQUERADES, (len(masquerades) > 0))

	# New: Moved into function.py:
	# nacl_state.register_pystache_data_object(TEMPLATE_KEY_HAS_FUNCTIONS, (len(nats) > 0 or len(filters) > 0))
	# Moved into function.py and Gateway class (only registering if is to be set to True):
	# nacl_state.register_pystache_data_object(TEMPLATE_KEY_ENABLE_CT, (len(nats) > 0 or len(filters) > 0 or len(gateways) > 0))

	# New: Moved to load_balancer.py:
	# nacl_state.register_pystache_data_object(TEMPLATE_KEY_HAS_LOAD_BALANCERS, (len(load_balancers) > 0))
	# New: Moved to syslog.py:
	# nacl_state.register_pystache_data_object(TEMPLATE_KEY_HAS_SYSLOGS, (len(syslogs) > 0))

	# New: Moved to function.py:
	'''
	new_nats = nacl_state.pystache_data.get(TEMPLATE_KEY_NATS)
	masqs = nacl_state.pystache_data.get("masquerades") # TEMPLATE_KEY_MASQUERADES (defined in Iface class/file)
	if ((new_nats is not None and (len(new_nats) > 0)) or (masqs is not None and (len(masqs) > 0))):
		print "HAS NATS"
		nacl_state.register_pystache_data_object(TEMPLATE_KEY_HAS_NATS, True)
	'''

	# Set the last pystache_data values (the has-values) before rendering:
	for _, c in nacl_state.nacl_type_processors.iteritems():
		c.final_registration(nacl_state) # static method

	if nacl_state.language == CPP:
		# Combine the data object with the Cpp_template (cpp_template.mustache file)
		# Pystache returns the transpiled C++ content
		# Old:
		# content = pystache.Renderer().render(Cpp_template(), data)
		# New:
		content = pystache.Renderer().render(Cpp_template(), nacl_state.pystache_data)

		# Create the C++ file and write the content to the file
		file = None
		if len(sys.argv) > 1:
			file = open(os.path.expanduser(sys.argv[1]), "w")

		if file is not None:
			file.write(content)
	else:
		exit_NaCl_internal_error("Internal error in handle_input: Transpilation to language " + nacl_state.language + " has not been implemented")

	print "Transpilation complete"

# -------------------- 1. Visiting --------------------
'''
invalid_names = [
	TCP,
	UDP,
	ICMP,
	CT,
	IP
]

# Validate the name that the user has given an element
# Called in save_element function
def validate_name(name_ctx):
	name_parts = name_ctx.getText().split(DOT)
	name = name_parts[0]

	if "-" in name:
		sys.exit("line " + get_line_and_column(name_ctx) + " Invalid character (-) in name " + name)

	if name.lower() in invalid_names:
		sys.exit("line " + get_line_and_column(name_ctx) + " Invalid name " + name)
'''

'''
# Add visited element to the elements dictionary
def save_element(base_type, ctx):
	print "save_element - content of nacl_types: ", str(nacl_types)

	if base_type != BASE_TYPE_TYPED_INIT and base_type != BASE_TYPE_UNTYPED_INIT and base_type != BASE_TYPE_FUNCTION:
		sys.exit("line " + get_line_and_column(ctx) + " NaCl elements of base type " + base_type + " are not handled")

	name_ctx = ctx.name() if base_type != BASE_TYPE_UNTYPED_INIT else ctx.value_name()
	if name_ctx is None:
		sys.exit("line " + get_line_and_column(ctx) + " Missing name of element")
	if name_ctx.getText() in elements:
		sys.exit("line " + get_line_and_column(name_ctx) + " Element " + name_ctx.getText() + " has already been defined")

	validate_name(name_ctx)

	name = name_ctx.getText()
	idx = len(elements)

	# BASE_TYPE_UNTYPED_INIT

	if base_type == BASE_TYPE_UNTYPED_INIT:
		elements[name] = Untyped(idx, name, ctx, base_type)
		return

	type_t_ctx = ctx.type_t()
	type_t = type_t_ctx.getText()
	type_t_lower = type_t.lower()

	# Old: if type_t.lower() not in valid_nacl_types:
	# New:
	if type_t_lower not in nacl_types:
		sys.exit("line " + get_line_and_column(type_t_ctx) + " Undefined type " + type_t)

	# BASE_TYPE_FUNCTION

	if base_type == BASE_TYPE_FUNCTION:
		elements[name] = Function(idx, name, ctx, base_type, type_t, ctx.subtype().getText())
		return

	# BASE_TYPE_TYPED_INIT
	# TODO: Use dictionary
	nacl_types[type_t_lower](idx, name, ctx, base_type, type_t)
	# TODO: Each class in its own file
	# Load_balancer / all classes in pyton you can call type processors
	# Type_processors (folder) contains one file per class
	# In load_balancer.py f.ex.: from Ncl import Types
	# -> NaCl.register("Load_balancer", Load_balancer) in the dictioary nacl_types/valid_nacl_types ()
	# (So don't need to change)
'''
'''
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
		elements[name] = Conntrack(idx, name, ctx, base_type, type_t)
		conntrack_exists = True
	elif type_t_lower == TYPE_SYSLOG:
		global syslog_exists
		if syslog_exists:
			sys.exit("line " + get_line_and_column(type_t_ctx) + " A Syslog has already been defined")
		elements[name] = Syslog(idx, name, ctx, base_type, type_t)
		syslog_exists = True
	else:
		sys.exit("line " + get_line_and_column(type_t_ctx) + " NaCl elements of type " + type_t + " are not handled")
'''

class NaClRecordingVisitor(NaClVisitor):
	def __init__(self, nacl_state):
		self.nacl_state = nacl_state

	def visitTyped_initializer(self, ctx):
		# Typed: Could indicate that C++ code is going to be created from this - depends on the
		# type_t specified (Iface, Gateway special)
		self.nacl_state.save_element(BASE_TYPE_TYPED_INIT, ctx)

	def visitInitializer(self, ctx):
		# Untyped: Means generally that no C++ code is going to be created from this - exists only in NaCl
		# Except: Assignments
		self.nacl_state.save_element(BASE_TYPE_UNTYPED_INIT, ctx)

	def visitFunction(self, ctx):
		self.nacl_state.save_element(BASE_TYPE_FUNCTION, ctx)

# Code to be executed when NaCl.py is run directly, but not when imported:
if __name__ == "__main__":
	nacl_state = NaCl_state(CPP)

	# Option 1:
	# nacl_state.register_all_type_processors() # init
	# Each type processor calls nacl_state.add_type_processor

	# Option 2:
	# print "Register all type processors"
	# The init function in type_processors/__init__.py will loop through all the modules (.py files)
	# in the folder and will in turn call each module's init function:
	from type_processors import init as init_type_processors
	init_type_processors(nacl_state)

	lexer = NaClLexer(StdinStream())
	stream = CommonTokenStream(lexer)
	parser = NaClParser(stream)
	tree = parser.prog()
	visitor = NaClRecordingVisitor(nacl_state)
	visitor.visit(tree)

	handle_input(nacl_state)
