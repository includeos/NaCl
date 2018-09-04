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

# antlr4 -Dlanguage=Python2 NaCl.g4 -visitor

# -------------------- Constants --------------------

# Temporary:
VALUE_TRANSPILER = "value_transpiler"

# Language to transpile to
CPP = "cpp"

DOT = "."

BASE_TYPE_FUNCTION 		= "function"
BASE_TYPE_UNTYPED_INIT 	= "untyped_init"
BASE_TYPE_TYPED_INIT 	= "typed_init"

TCP 	= "tcp"
UDP 	= "udp"
ICMP 	= "icmp"
CT 		= "ct"
IP 		= "ip"

# -------------------- Error handling --------------------

def get_line_and_column(ctx):
	return str(ctx.start.line) + ":" + str(ctx.start.column)

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

# < Error handling

# -------------------- NaCl_state --------------------

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
		# self.value_transpiler = Cpp_value_transpiler(self.elements)
		self.subtranspilers = {}

	def register_subtranspiler(self, key, value):
		# F.ex. Cpp_value_transpiler
		self.subtranspilers[key] = value

	def set_language(self, language):
		if language not in self.valid_languages:
			exit_NaCl_internal_error("Internal error in handle_input: Cannot transpile to language " + language)
		self.language = language

	def transpile_value(self, value_ctx, subtype=""):
		return self.subtranspilers[VALUE_TRANSPILER].transpile(value_ctx, subtype)

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

		if type_t_lower not in self.nacl_type_processors:
			exit_NaCl(type_t_ctx, "Undefined type " + type_t)

		# If only ONE element of this type is allowed and an element of the type already exists,
		# exit with error
		if type_t_lower in self.singletons and self.element_of_type_exists(type_t_lower):
			exit_NaCl(type_t_ctx, "A " + type_t + " has already been defined")

		# BASE_TYPE_FUNCTION
		if base_type == BASE_TYPE_FUNCTION:
			self.elements[name] = self.nacl_type_processors[type_t_lower](self, idx, name, ctx, base_type, type_t, ctx.subtype().getText())
			return

		# BASE_TYPE_TYPED_INIT
		self.elements[name] = self.nacl_type_processors[type_t_lower](self, idx, name, ctx, base_type, type_t)

# < NaCl_state

# -------------------- Element --------------------
# Each Element is a top NaCl element from the NaCl file given as input to this python script
# The Antlr parser identifies these elements and they are visited in

class Element(object):
	def __init__(self, nacl_state, idx, name, ctx, base_type):
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

	# Can be overridden in subclass
	# Called from the handle_input function right before rendering, after the NaCl file has been processed
	# Register the last data here that can not be registered before this (set has-values f.ex. like
	# has_nats, has_vlans, has_load_balancers)
	@staticmethod
	def final_registration(nacl_state):
		pass

	# All subclasses MUST implement the process method - this is the main processing method for all NaCl elements, the
	# starting point for every transpilation of every NaCl element
	def process(self):
		exit_NaCl(self.ctx, "Internal error: Subclass of class Element has not implemented the process method")

	def get_class_name(self):
		return self.__class__.__name__

	# TODO - make handle_as_untyped the only option - then this method will be redundant: Vlan and Iface
	# This is ONLY implemented in the Vlan and Iface classes
	# Every other class does nothing here
	# If not valid - throw exception
	def validate_key(self, key):
		pass

	# Can be overridden in subclass
	# Iface is special here and should override the method
	def add_member(self, key, value):
		if self.members.get(key) is None:
			self.members[key] = value
		else:
			raise NaCl_exception(self.get_class_name() + " member " + key + " has already been set")

	# This is a special case, where we create a Typed element in NaCl (meaning the element is of a NaCl type,
	# f.ex. Iface) and the value of the element is NOT an object ({}). Example: 'Iface eth0 dhcp'
	# (type is Iface and value is dhcp)
	def add_not_obj_value(self, value_ctx):
		raise NaCl_exception(self.get_class_name() + " has to contain key value pairs")

	# The first method that is called in every standard type_processor's process method
	# (not in function, which is special and don't use the self.members dictionary)
	# Adding to self.members (dictionary)
	# Rename to process_object f.ex.
	def process_ctx(self):
		# Handle the Element's value ctx object: Fill self.members dictionary
		# Note: Gateway has its own process_ctx method

		value = self.ctx.value() if hasattr(self.ctx, 'value') else self.ctx
		class_name = self.get_class_name()

		# Using Untyped methods (placed in Element) since depth is more than 1 level deep
		if self.handle_as_untyped:
			if value.obj() is None:
				exit_NaCl(value, class_name + " must be an object")
			self.process_obj(self.members, value.obj())
			return

		# TODO: This approach should NOT be an option - Gateway, Vlan and Iface should be updated to handle_as_untyped
		# Everything else but Load_balancer, Conntrack and Syslog (meaning Gateway, Vlan and Iface):
		if value.obj() is not None:
			for pair in value.obj().key_value_list().key_value_pair():
				orig_key 	= pair.key().getText()
				key 		= orig_key.lower()
				pair_value 	= pair.value()

				try:
					# TODO: Make handle_as_untyped the only option - then this method will be redundant: Vlan and Iface
					# are the only classes that (need to) call this method
					# The old solution only tested this for vlan and iface:
					# Default (if method is not implemented in subclass): Do nothing
					self.validate_key(orig_key) # check if key exists in predefined_iface_keys f.ex.
				except NaCl_exception as e:
					exit_NaCl(pair.key(), e.value)

				# TODO: Can probably be removed later. Checked in self.add_member-method
				if self.members.get(key) is not None:
					exit_NaCl(pair.key(), class_name + " member " + key + " has already been set")

				# TODO: Implement this method in all classes that needs to do other operations
				# than just adding the key value pair to the self.members dictionary
				try:
					self.add_member(key, pair_value)
				except NaCl_exception as e:
					exit_NaCl(pair.key(), e.value)
				# Default add_member behavior: self.members[key] = pair_value
				# Special if is_iface and key in chains: self.process_push(key, pair_value)
		else:
			try:
				self.add_not_obj_value(value)
			except NaCl_exception as e:
				exit_NaCl(value, e.value)
				# sys.exit("line " + get_line_and_column(value) + " A " + class_name + " has to contain key value pairs")

	def process_assignments(self):
		# Loop through elements that are assignments
		# Find assignments (f.ex. x.y: <value> or x.y.z: <value>) that refers to this Element

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
			self.process_assignment(key)

	# ---------- Methods related to dictionary self.members (for Untyped, Load_balancer, Conntrack and Syslog) ----------

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

	# Get a specific value from the given dictionary (at top level the dictionary input is normally self.members)
	# based on the given key_list (could f.ex. be lb.clients.iface)
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

				# We don't want to modify the input parameter (key_list), therefore key_list[1:] here:
				return self.get_dictionary_val(new_dict, key_list[1:], error_ctx)

	# Add a specific value (ctx) to the given dictionary (at top level the dictionary input is normally self.members)
	# The key_list (f.ex. lb.clients.iface) indicates where in the dictionary the new value should be put
	def add_dictionary_val(self, dictionary, key_list, value, level=1, parent_key=""):
		level_key = key_list[0] if self.handle_as_untyped else key_list[0].lower()

		# End of recursion condition
		if len(key_list) == 1:
			if value.obj() is not None:
				# Then the value is a new dictionary
				dictionary[level_key] = {} # Create new dictionary
				return self.process_obj(dictionary[level_key], value.obj(), (level + 1), level_key)
			else:
				if self.handle_as_untyped:
					self.validate_dictionary_key(level_key, parent_key, level, value)
					self.resolve_dictionary_value(dictionary, level_key, value)
				else:
					dictionary[level_key] = self.nacl_state.transpile_value(value)
				return

		# Error
		if level_key not in dictionary:
			exit_NaCl(value, "Trying to add to a member (" + level_key + ") that doesn't exist")

		# Recursion
		for key in dictionary:
			if key == level_key:
				# We don't want to modify the input parameter (key_list), therefore key_list[1:] here:
				return self.add_dictionary_val(dictionary[key], key_list[1:], value, level, level_key)

	def process_obj(self, dictionary, ctx, level=1, parent_key=""):
		# Could be either Untyped, Load_balancer, Conntrack or Syslog
		# Level only relevant for Load_balancer, Conntrack and Syslog

		for pair in ctx.key_value_list().key_value_pair():
			key = pair.key().getText() if self.handle_as_untyped else pair.key().getText().lower()

			if dictionary.get(key) is not None:
				exit_NaCl(pair.key(), "Member " + key + " has already been set")

			# Validate key

			if self.handle_as_untyped:
				self.validate_dictionary_key(key, parent_key, level, pair.key())

			# End of recursion:
			if pair.value().obj() is None:
				if self.handle_as_untyped:
					self.resolve_dictionary_value(dictionary, key, pair.value())
				else:
					dictionary[key] = self.nacl_state.transpile_value(pair.value())
			else:
				# Recursion:
				# Then we have an obj inside an obj
				dictionary[key] = {} # Creating new dictionary
				# Loop through the obj and fill the new dictionary
				self.process_obj(dictionary[key], pair.value().obj(), (level + 1), key)

	# Should be overridden in subclass
	def validate_dictionary_key(self, key, parent_key, level, value_ctx):
		exit_NaCl(value_ctx, "Internal error: The class " + self.get_class_name() + " needs to override the method " + \
			"validate_dictionary_key")

	# Should be overridden in subclass
	def resolve_dictionary_value(self, dictionary, key, value_ctx):
		exit_NaCl(value_ctx, "Internal error: The class " + self.get_class_name() + " needs to override the method " + \
			"resolve_dictionary_value")

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
		dictionary[key] = self.nacl_state.transpile_value(value_ctx)

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

# -------------------- 2. Process elements and write transpiled content to file --------------------

# ---- Pystache ----
# Connected to cpp_template.mustache
class Cpp_template(object):
	def __init__(self):
		pass
# < Pystache

# Main function
# Called after all the elements in the NaCl file have been visited and saved in the
# nacl_state's elements dictionary
def handle_input(nacl_state):
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

	# Set the last pystache_data values (the has-values) before rendering:
	for _, c in nacl_state.nacl_type_processors.iteritems():
		c.final_registration(nacl_state) # static method

	if nacl_state.language == CPP:
		# Combine the data object with the Cpp_template (cpp_template.mustache file)
		# Pystache returns the transpiled C++ content
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

# < 2. Process elements and write transpiled content to file

# -------------------- 1. Visiting --------------------
# Visiting each NaCl element in the NaCl file given as input to this python script

class NaClRecordingVisitor(NaClVisitor):
	def __init__(self, nacl_state):
		self.nacl_state = nacl_state

	# Executed when a typed_initializer is identified in the NaCl file by the Antlr parser (defined in NaCl.g4)
	def visitTyped_initializer(self, ctx):
		# Typed: Could indicate that C++ code is going to be created from this - depends on the
		# type_t specified (Iface, Gateway special)
		self.nacl_state.save_element(BASE_TYPE_TYPED_INIT, ctx)

	# Executed when an initializer is identified in the NaCl file by the Antlr parser (defined in NaCl.g4)
	def visitInitializer(self, ctx):
		# Untyped: Means generally that no C++ code is going to be created from this - exists only in NaCl
		# Except: Assignments
		self.nacl_state.save_element(BASE_TYPE_UNTYPED_INIT, ctx)

	# Executed when a function is identified in the NaCl file by the Antlr parser (defined in NaCl.g4)
	def visitFunction(self, ctx):
		self.nacl_state.save_element(BASE_TYPE_FUNCTION, ctx)

# Code to be executed when NaCl.py is run directly, but not when imported:
if __name__ == "__main__":
	nacl_state = NaCl_state(CPP)

	# print "Register all subtranspilers"
	from subtranspilers import init as init_subtranspilers
	init_subtranspilers(nacl_state)

	# print "Register all type processors"
	# The init function in type_processors/__init__.py will loop through all the modules (.py files)
	# in the folder and will in turn call each module's init function:
	from type_processors import init as init_type_processors
	init_type_processors(nacl_state)

	lexer = NaClLexer(StdinStream())
	stream = CommonTokenStream(lexer)
	parser = NaClParser(stream)
	tree = parser.prog()

	# Visit
	visitor = NaClRecordingVisitor(nacl_state)
	visitor.visit(tree)

	# Process the visited elements that have been registered in the nacl_state's elements dictionary
	handle_input(nacl_state)

# < 1. Visiting
