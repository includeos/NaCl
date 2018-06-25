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
# To avoid: <...>/NaCl/subtranspilers/function_transpiler.py:1: RuntimeWarning: Parent module '<...>/NaCl/subtranspilers' not found while handling absolute import

from NaCl import exit_NaCl, exit_NaCl_internal_error, BASE_TYPE_FUNCTION
from shared import *
from subtranspilers.value_transpiler import VALUE_TRANSPILER
from type_processors.syslog import EMERG, ALERT, CRIT, ERR, WARNING, NOTICE, INFO, DEBUG, \
	INCLUDEOS_SYSLOG_SEVERITY_EMERG, INCLUDEOS_SYSLOG_SEVERITY_ALERT, INCLUDEOS_SYSLOG_SEVERITY_CRIT, \
	INCLUDEOS_SYSLOG_SEVERITY_ERR, INCLUDEOS_SYSLOG_SEVERITY_WARNING, INCLUDEOS_SYSLOG_SEVERITY_NOTICE, \
	INCLUDEOS_SYSLOG_SEVERITY_INFO, INCLUDEOS_SYSLOG_SEVERITY_DEBUG

FUNCTION_TRANSPILER = "function_transpiler"

TYPE_FILTER = "filter"
TYPE_NAT 	= "nat" # TODO: Defined in shared.py as well

# NaCl verdicts/actions
ACCEPT 	= 'accept'
DROP 	= 'drop'
LOG 	= 'log'
SYSLOG 	= 'syslog'
SNAT 	= 'snat'
DNAT 	= 'dnat'

# TODO: Move to another file (__init__.py or make function_transpiler into a folder
# containing function_transpiler.py and cpp_function_transpiler.py? (or function_transpiler.py,
# cpp_function_transpiler.py, action_transpiler.py and cpp_action_transpiler.py))
# -------------------- Action_transpiler --------------------

# Actions are only used in functions
class Action_transpiler(object):
	def __init__(self, nacl_state):
		# print "Action_transpiler"
		self.nacl_state = nacl_state

		self.actions = {
			ACCEPT,
			DROP,
			LOG,
			SYSLOG,
			SNAT,
			DNAT
		}

		self.legal_actions = {
			TYPE_FILTER: 	[ ACCEPT, DROP, LOG, SYSLOG ],
			TYPE_NAT: 		[ DNAT, SNAT, LOG, SYSLOG ]
		}

	def get_class_name(self):
		return self.__class__.__name__

	def transpile(self, type_t, subtype, action_ctx):
		# Should be implemented by class that extends this class
		exit_NaCl_internal_error("The class " + self.get_class_name() + " needs to override the method " + \
			"transpile")

# < Action_transpiler

# -------------------- Cpp_action_transpiler --------------------

class Cpp_action_transpiler(Action_transpiler):
	def __init__(self, nacl_state):
		super(Cpp_action_transpiler, self).__init__(nacl_state)
		# print "Cpp_action_transpiler"

		self.actions = {
			ACCEPT: self.transpile_accept,
			DROP: 	self.transpile_drop,
			LOG: 	self.transpile_log,
			SYSLOG: self.transpile_syslog,
			SNAT:	self.transpile_snat,
			DNAT: 	self.transpile_dnat
		}

		self.syslog_severities = {
			EMERG: 		INCLUDEOS_SYSLOG_SEVERITY_EMERG,
			ALERT: 		INCLUDEOS_SYSLOG_SEVERITY_ALERT,
			CRIT: 		INCLUDEOS_SYSLOG_SEVERITY_CRIT,
			ERR: 		INCLUDEOS_SYSLOG_SEVERITY_ERR,
			WARNING: 	INCLUDEOS_SYSLOG_SEVERITY_WARNING,
			NOTICE: 	INCLUDEOS_SYSLOG_SEVERITY_NOTICE,
			INFO: 		INCLUDEOS_SYSLOG_SEVERITY_INFO,
			DEBUG: 		INCLUDEOS_SYSLOG_SEVERITY_DEBUG
		}

	def transpile(self, type_t, subtype, action_ctx):
	# def transpile_action_cpp(self, type_t, subtype, action_ctx):
		parameters = [] if action_ctx.value_list() is None else action_ctx.value_list().value() # list
		name = action_ctx.name().getText()
		name_lower = name.lower()

		if name_lower not in self.actions:
			# Then the action name could be the name of a function
			element = self.nacl_state.elements.get(name)
			if element is None or element.base_type != BASE_TYPE_FUNCTION:
				exit_NaCl(action_ctx, "Couldn't identify action or function name " + name)
			return self.transpile_function_call(name, parameters, type_t, subtype, action_ctx)

		# If get here, name is the name of an action in self.actions

		actions = self.legal_actions[type_t.lower()]

		if name_lower not in actions:
			exit_NaCl(action_ctx, "Error transpiling action " + name + ": Legal actions for a function of type " + \
				type_t + " are: " + ", ".join(actions))

		return self.actions[name_lower](parameters, subtype, action_ctx)

	def transpile_function_call(self, name, parameter_ctx_list, type_t, subtype, action_ctx):
		# This was the name of a function, and a function takes no parameters:
		if len(parameter_ctx_list) > 0:
			exit_NaCl(action_ctx, "A function call takes no parameters")

		element = self.nacl_state.elements.get(name)
		if element is None or element.base_type != BASE_TYPE_FUNCTION:
			exit_NaCl(action_ctx, "No function with the name " + name + " exists")

		# element is a Function
		
		# A function of type Filter can only call functions of type Filter,
		# a function of type Nat can only call functions of type Nat, etc.
		if element.type_t.lower() != type_t.lower():
			exit_NaCl(action_ctx, "Error transpiling call to " + name + ": A function of type " + type_t + " can only call functions of the same type")

		if element.subtype.lower() not in legal_nested_subtypes[subtype.lower()]:
			exit_NaCl(action_ctx, "Cannot call a function of subtype " + element.subtype + " inside a function of subtype " + subtype)

		# return e.process()
		# Cannot call this and use the element's process method and res attribute because
		# the pckt name will be affected of/be different based on the subtype of the parent function
		# Therefore:
		return self.nacl_state.subtranspilers[FUNCTION_TRANSPILER].transpile(element.type_t, element.subtype, element.ctx, subtype)

	def transpile_accept(self, parameter_ctx_list, subtype, action_ctx):
		# This was the accept action, and this takes no parameters:
		if len(parameter_ctx_list) > 0:
			exit_NaCl(action_ctx, "An accept action takes no parameters")

		return INCLUDEOS_ACCEPT(subtype)

	def transpile_drop(self, parameter_ctx_list, subtype, action_ctx):
		# This was the drop action, and this takes no parameters:
		if len(parameter_ctx_list) > 0:
			exit_NaCl(action_ctx, "A drop action takes no parameters")

		return INCLUDEOS_DROP

	def transpile_log(self, parameter_ctx_list, subtype, action_ctx):
		content = "std::cout << "

		if len(parameter_ctx_list) > 0:
			for i, p in enumerate(parameter_ctx_list):
				if p.string() is not None:
					content += self.nacl_state.transpile_value(p, subtype)
				else:
					t = self.nacl_state.subtranspilers[VALUE_TRANSPILER].get_cout_convert_to_type(p)
					if t == TO_UNSIGNED:
						content += "static_cast<unsigned>(" + self.nacl_state.transpile_value(p, subtype) + ")"
					elif t == TO_STRING:
						content += self.nacl_state.transpile_value(p, subtype) + ".to_string()"
					else:
						exit_NaCl(p, "Internal error: std::cout conversion for " + t + " has not been implemented")

				if i < (len(parameter_ctx_list) - 1):
					content += " << "

		return content + ";\n"

	def transpile_syslog(self, parameter_ctx_list, subtype, action_ctx):
		main_string = "\""
		parameters_string = ""

		if len(parameter_ctx_list) < 2:
			exit_NaCl(action_ctx, "Too few arguments (syslog takes at least 2)")

		severity_ctx = parameter_ctx_list[0]
		severity = severity_ctx.getText().lower()

		if severity_ctx.value_name() is None or severity not in self.syslog_severities:
			exit_NaCl(severity_ctx, "Invalid syslog severity level. Valid severity levels are " + \
				", ".join(self.syslog_severities))

		for i, p in enumerate(parameter_ctx_list):
			if i > 0:
				if p.string() is not None:
					string = self.nacl_state.transpile_value(p, subtype)
					main_string += string[1:-1] # Not including first and last character of string (")
				else:
					t = self.nacl_state.subtranspilers[VALUE_TRANSPILER].get_cout_convert_to_type(p)
					if t == TO_UNSIGNED:
						main_string += "%u"
						parameters_string += ", " + self.nacl_state.transpile_value(p, subtype)
					elif t == TO_STRING:
						main_string += "%s"
						parameters_string += ", " + self.nacl_state.transpile_value(p, subtype) + ".to_string().c_str()"
					else:
						exit_NaCl(p, "Internal error: Syslog conversion for " + t + " has not been implemented")

		return "Syslog::syslog(" + self.syslog_severities[severity] + ", " + main_string + "\"" + parameters_string + ");\n"

	def transpile_nat(self, type_nat, parameter_ctx_list, subtype, action_ctx):
		if type_nat != SNAT and type_nat != DNAT:
			exit_NaCl_internal_error("Internal error in transpile_nat_cpp: Invalid NAT type " + type_nat)

		# pckt_name = self.nacl_state.subtranspilers[VALUE_TRANSPILER].get_pckt_name(subtype)

		parameters = ""
		num_params = len(parameter_ctx_list)
		if num_params == 1:
			first = self.nacl_state.transpile_value(parameter_ctx_list[0])
			# parameters = pckt_name + ", " + INCLUDEOS_CT_ENTRY + ", " + str(first)
			parameters = INCLUDEOS_DEREFERENCE_OP + IP_PCKT + ", " + INCLUDEOS_CT_ENTRY + ", " + str(first)
		elif num_params > 1:
			first 	= self.nacl_state.transpile_value(parameter_ctx_list[0])
			second 	= self.nacl_state.transpile_value(parameter_ctx_list[1])
			# parameters = pckt_name + ", " + INCLUDEOS_CT_ENTRY + ", {" + str(first) + ", " + str(second) + "}"
			parameters = INCLUDEOS_DEREFERENCE_OP + IP_PCKT + ", " + INCLUDEOS_CT_ENTRY + ", {" + str(first) + ", " + str(second) + "}"
		else:
			exit_NaCl(action_ctx, "No arguments provided to " + type_nat)

		return INCLUDEOS_NAT_OBJ_NAME + ARROW + type_nat + "(" + parameters + ");\n" + \
			self.transpile_accept([], subtype, action_ctx)

	def transpile_snat(self, parameter_ctx_list, subtype, action_ctx):
		return self.transpile_nat(SNAT, parameter_ctx_list, subtype, action_ctx)

	def transpile_dnat(self, parameter_ctx_list, subtype, action_ctx):
		return self.transpile_nat(DNAT, parameter_ctx_list, subtype, action_ctx)

# < Cpp_action_transpiler

# TODO: Move to another file (__init__.py?)
# -------------------- Function_transpiler --------------------

class Function_transpiler(object):
	def __init__(self, nacl_state):
		self.nacl_state = nacl_state
		# print "Function transpiler"
		# Default?:
		# self.action_transpiler = Action_transpiler(nacl_state)

	def get_class_name(self):
		return self.__class__.__name__

	def transpile(self, type_t, subtype, ctx, parent_subtype=""):
		# Should be implemented by class that extends this class
		exit_NaCl_internal_error("Internal error: The class " + self.get_class_name() + " needs to override the method " + \
			"transpile")

# < Function_transpiler

# -------------------- Cpp_function_transpiler --------------------

class Cpp_function_transpiler(Function_transpiler):
	def __init__(self, nacl_state):
		super(Cpp_function_transpiler, self).__init__(nacl_state)
		self.action_transpiler = Cpp_action_transpiler(nacl_state)
		# print "Cpp_function_transpiler"

	# Main function - starting point to transpile a NaCl function:
	# def transpile_function(self, type_t, subtype, ctx, parent_subtype=""):
	def transpile(self, type_t, subtype, ctx, parent_subtype=""):
		# Return a string with all the code
		content = ""

		if parent_subtype == "":
			content += INCLUDEOS_CT_ENTRY_NULLPTR_CHECK

		subtype_lower = subtype.lower()
		is_ip = subtype_lower == IP
		parent_pckt_name = ""
		parent_subtype = parent_subtype.lower()

		# 1. Before the main content:
		if not is_ip:
			# The content of a Filter always starts with validating that the incoming packet's protocol
			# matches the protocol that the subtype of the Filter indicates.
			# If the incoming packet is not of this protocol, there's nothing to check for in the Filter,
			# and the packet is returned.
			# If the subtype of the Filter indicates another protocol than IP, the incoming packet
			# is cast to a packet of the correct protocol, following the test on the packet's protocol field.

			value_transpiler = self.nacl_state.subtranspilers[VALUE_TRANSPILER]

			protocol_method = Ip_obj.resolve_method_cpp(PROTOCOL, ctx)
			protocol_val 	= Ip_obj.resolve_protocol_cpp(subtype, ctx)
			pckt_cast 		= value_transpiler.get_pckt_cast(subtype, ctx)

			# If we are in a nested function and the parent function was not IP,
			# we have another pckt_name than 'pckt' to take into account:
			if parent_subtype == "" or parent_subtype == IP:
				content += "if (" + IP_PCKT + value_transpiler.get_access_op(IP) + protocol_method + " " + EQUALS + " " + protocol_val + ") {\n" + \
					pckt_cast + "\n\n"
			elif parent_subtype != "" and subtype_lower != parent_subtype and parent_subtype != IP:
				# If subtype == parent_subtype, we don't need this if-check on protocol at all (has been tested above in the C++ code)
				parent_pckt_name = value_transpiler.get_pckt_name(parent_subtype)
				parent_access_op = value_transpiler.get_access_op(parent_subtype)

				if parent_subtype == ICMP:
					protocol_method = INCLUDEOS_ICMP_IP_ACCESS_METHOD + parent_access_op + protocol_method

				content += "if (" + parent_pckt_name + parent_access_op + protocol_method + " " + EQUALS + " " + protocol_val + ") {\n" + \
					pckt_cast + "\n\n"

		# 2. Main operation - produces the main content:
		if parent_subtype != "" and is_ip:
			# We have to change the name of the ip pckt and we do this by sending in the parent_subtype
			# instead of the subtype
			content += self.transpile_body_elements(type_t, parent_subtype, ctx.body().body_element())
		else:
			content += self.transpile_body_elements(type_t, subtype, ctx.body().body_element())

		# 3. After the main content:

		# If this was an ICMP function: Release
		if subtype_lower == ICMP:
			content += IP_PCKT + " = " + ICMP_PCKT + DOT + INCLUDEOS_ICMP_RELEASE_METHOD + ";\n"

		if not is_ip:
			# Finish the if added above
			if subtype_lower != parent_subtype:
				content += "}\n"

		return content

	# ---- Helper functions for transpile_comparison_cpp ----

	def construct_rng_comparison(self, resolved_rng_list, resolved_lhs):
		# A rng can only consist of integers or ipv4_addrs

		if len(resolved_rng_list) != 2:
			exit_NaCl_internal_error("Internal error: Resolved list should be a rng consisting of two values instead of " + \
				str(resolved_rng_list))

		from_val 	= resolved_rng_list[0]
		to_val 		= resolved_rng_list[1]
		logical_op 	= AND

		return "(" + str(resolved_lhs) + " " + GREATER_THAN_OR_EQUAL + " " + str(from_val) + " " + logical_op + " " + \
			str(resolved_lhs) + " " + LESS_THAN_OR_EQUAL + " " + str(to_val) + ")"

	def construct_comparisons_from_list(self, resolved_rhs_list, resolved_lhs, is_inner_list=False):
		if isinstance(resolved_rhs_list[0], bool):
			# Then resolved_rhs_list is a list_t or obj

			# Remove the first element from the list (the bool value):
			resolved_rhs_list.pop(0)

			# Note: An element in a list could be a new list with or without a bool value
			# If not bool value: rng. Else: list_t/obj

			# To avoid parentheses around an inner obj or list_t element's comparisons - we want all of the
			# obj/list_t values to be equal (on the top level), even though they are deeper inside the
			# obj/list_t hierarchy (nested)
			result = "" if is_inner_list else "("

			num_rhs_vals = len(resolved_rhs_list)
			for i, rhs_val in enumerate(resolved_rhs_list):
				if isinstance(rhs_val, list):
					# Then the rhs_val is a new list_t or obj, or it is a rng
					result += self.construct_comparisons_from_list(rhs_val, resolved_lhs, True)
				elif INCLUDEOS_IP4_CIDR_CLASS in str(rhs_val):
					result += str(rhs_val) + ".contains(" + str(resolved_lhs) + ")"
				else:
					result += str(resolved_lhs) + " " + EQUALS + " " + str(rhs_val)

				if i < (num_rhs_vals - 1):
					result += " " + OR + " "

			if not is_inner_list:
				return result + ")"

			return result
		else:
			# Then this was a rng (containing a from-value and a to-value)
			return self.construct_rng_comparison(resolved_rhs_list, resolved_lhs)

	def construct_comparison(self, comp_ctx, resolved_lhs, resolved_rhs, comparison_op, op):
		lhs_is_list = True if isinstance(resolved_lhs, list) else False
		rhs_is_list = True if isinstance(resolved_rhs, list) else False

		result = ""

		# If none of these are lists, we have the resolved values
		if not lhs_is_list and not rhs_is_list:
			if INCLUDEOS_IP4_CIDR_CLASS in str(resolved_rhs):
				if comparison_op.lower() != IN:
					exit_NaCl(comp_ctx.comparison_operator(), "Invalid operator (" + comparison_op + "). Only the 'in' " + \
						"operator is valid when comparing a property to a range, cidr, list or object")

				result = str(resolved_rhs) + ".contains(" + str(resolved_lhs) + ")"
			else:
				if comparison_op.lower() == IN:
					exit_NaCl(comp_ctx.comparison_operator(), "The 'in' operator can only be used when comparing a property to " + \
						"a range, cidr, list or object")

				result = str(resolved_lhs) + " " + comparison_op + " " + str(resolved_rhs)

			if op != "":
				result = "(" + result + ") " + op + " "

			return result

		# If any of the resolved sides is a list, the 'in' operator should have been used
		# (rng, ip4_cidr, list_t, obj)
		if comparison_op != IN:
			exit_NaCl(comp_ctx.comparison_operator(), "Invalid operator (" + comparison_op + \
				"). Only the 'in' operator is valid when comparing a value to a range, cidr, list or object")

		# If the 'in' operator has been used, only the resolved_rhs should be a list, not
		# the resolved_lhs
		if lhs_is_list:
			exit_NaCl(comp_ctx.lhs().value(), "The left hand side of a comparison can not resolve to a set " + \
				"of values, e.g. a range, cidr, list or object")

		if rhs_is_list:
			result = self.construct_comparisons_from_list(resolved_rhs, resolved_lhs)

		if op != "":
			return "(" + result + ") " + op + " "

		return result

	# ---- < Helper functions for transpile_comparison ----

	def transpile_comparison(self, subtype, comp, op=""):
		# Resolve the values
		resolved_lhs = self.nacl_state.transpile_value(comp.lhs().value(), subtype)
		comparison_op = comp.comparison_operator().getText()
		resolved_rhs = self.nacl_state.transpile_value(comp.rhs().value(), subtype)

		# And construct the comparison(s) based on the resolved values
		return self.construct_comparison(comp, resolved_lhs, resolved_rhs, comparison_op, op)

	def transpile_bool_expr(self, type_t, subtype, expr, op=""):
		content = ""

		# End of recursion condition - option 1
		# Has reached a comparison
		if hasattr(expr, 'comparison') and expr.comparison() is not None:
			has_not = hasattr(expr, 'Not') and expr.Not() is not None

			if has_not:
				content += NOT

			if hasattr(expr, 'Parenthesis_start') and expr.Parenthesis_start() is not None:
				content += expr.Parenthesis_start().getText()
			elif has_not:
				content += PARENTHESIS_START

			content += self.transpile_comparison(subtype, expr.comparison(), op)

			if hasattr(expr, 'Parenthesis_end') and expr.Parenthesis_end() is not None:
				content += expr.Parenthesis_end().getText()
			elif has_not:
				content += PARENTHESIS_END

			return content

		# End of recursion condition - option 2
		# Has reached a value
		if hasattr(expr, 'value') and expr.value() is not None:
			if hasattr(expr, 'Not') and expr.Not() is not None:
				content += NOT
			return content + self.nacl_state.transpile_value(expr.value())

		# Recursion:
		if isinstance(expr, list):
			# Optional not and parentheses around the list of bool_exprs

			if hasattr(expr, 'Not') and expr.Not() is not None:
				content += NOT
			if hasattr(expr, 'Parenthesis_start') and expr.Parenthesis_start() is not None:
				content += expr.Parenthesis_start().getText()

			for i, e in enumerate(expr):
				content += self.transpile_bool_expr(type_t, subtype, e)
				if i < (len(expr) - 1) and op != "":
					content += " " + op + " "

			if hasattr(expr, 'Parenthesis_end') and expr.Parenthesis_end() is not None:
				content += expr.Parenthesis_end().getText()

			return content
		else:
			logical_op = ""

			if hasattr(expr, 'Not') and expr.Not() is not None:
				content += NOT

			if hasattr(expr, 'Parenthesis_start') and expr.Parenthesis_start() is not None:
				content += expr.Parenthesis_start().getText()

			if hasattr(expr, 'logical_operator') and expr.logical_operator() is not None:
				logical_op = expr.logical_operator().getText()

			content += self.transpile_bool_expr(type_t, subtype, expr.bool_expr(), logical_op)

			if hasattr(expr, 'Parenthesis_end') and expr.Parenthesis_end() is not None:
				content += expr.Parenthesis_end().getText()

			return content

	def transpile_conditional(self, type_t, subtype, cond):
		content = ""
		bodies = cond.body()
		num_bodies = len(bodies)

		if hasattr(cond, 'If') and cond.If() is not None:
			if num_bodies < 1:
				exit_NaCl(cond, "Invalid syntax")

			# If-body is always first (index 0)
			content += cond.If().getText() + " " + self.transpile_bool_expr(type_t, subtype, cond) + \
				" {\n" + self.transpile_body_elements(type_t, subtype, bodies[0].body_element()) + "}\n"

		if hasattr(cond, 'Else') and cond.Else() is not None:
			if num_bodies < 2:
				exit_NaCl(cond, "Invalid syntax")

			# Else-body is always second/last (index 1)
			content += cond.Else().getText() + " {\n" + \
				self.transpile_body_elements(type_t, subtype, bodies[1].body_element()) + "}\n"

		return content

	def transpile_body_elements(self, type_t, subtype, body_elements):
		content = ""

		for e in body_elements:
			if e.conditional() is not None:
				content += self.transpile_conditional(type_t, subtype, e.conditional())
			elif e.action() is not None:
				content += self.action_transpiler.transpile(type_t, subtype, e.action())
			elif e.function() is not None:
				# Validate if valid type_t and subtype
				nested_type_t 	= e.function().type_t().getText()
				nested_subtype 	= e.function().subtype().getText()

				# Can only nest functions of the same type_t
				if type_t.lower() != nested_type_t.lower():
					exit_NaCl(e.function().type_t(), "You cannot create a function of type " + \
						nested_type_t + " inside a function of type " + type_t)

				# If this is a function, we have to validate that the subtype is legal based on the subtype of
				# the parent function
				if nested_subtype.lower() not in legal_nested_subtypes[subtype.lower()]:
					exit_NaCl(e.function().subtype(), "You cannot create a function of subtype " + \
						nested_subtype + " inside a function of subtype " + subtype)

				content += self.transpile(nested_type_t, nested_subtype, e.function(), subtype)

		return content

# < Cpp_function_transpiler

def init(nacl_state):
    # print "Init function_transpiler: Cpp_function_transpiler"
    nacl_state.register_subtranspiler(FUNCTION_TRANSPILER, Cpp_function_transpiler(nacl_state))
