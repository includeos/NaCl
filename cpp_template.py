from cpp_resolve_values import *

import pystache

# -------------------- Pystache --------------------

class Cpp_template(object):
	def __init__(self):
		pass

# ------------------ < Pystache ------------------

# NOTE
# Action_handler was previously placed in shared_constants.py together with the
# get_pckt_name_cpp function (this function is now back in cpp_resolve_values.py)
# Action_handler is placed here for now because it uses the transpile_function_cpp
# method
class Action_handler:
	def __init__(self):
		self.actions = {
			ACCEPT,
			DROP,
			LOG,
			SNAT,
			DNAT
		}

		self.cpp_actions = {
			ACCEPT: self.transpile_accept_cpp,
			DROP: 	self.transpile_drop_cpp,
			LOG: 	self.transpile_log_cpp,
			SNAT:	self.transpile_snat_cpp,
			DNAT: 	self.transpile_dnat_cpp
		}

		self.legal_actions = {
			TYPE_FILTER: 	[ ACCEPT, DROP, LOG ],
			TYPE_NAT: 		[ DNAT, SNAT, LOG ]
		}

	def transpile_action(self, language, type_t, subtype, action_ctx):
		if language == CPP:
			return self.transpile_action_cpp(type_t, subtype, action_ctx)

	def transpile_action_cpp(self, type_t, subtype, action_ctx):
		parameters = [] if action_ctx.value_list() is None else action_ctx.value_list().value() # list
		name = action_ctx.name().getText()
		name_lower = name.lower()

		if name_lower not in self.actions:
			# Then the action name could be the name of a function
			element = elements.get(name)
			if element is None or element.base_type != BASE_TYPE_FUNCTION:
				sys.exit("line " + get_line_and_column(action_ctx) + \
					" Couldn't identify action or function name " + name)
			return self.transpile_function_call_cpp(name, parameters, type_t, subtype, action_ctx)

		# If get here, name is the name of an action in self.actions
		
		actions = self.legal_actions[type_t.lower()]

		if name_lower not in actions:
			sys.exit("line " + get_line_and_column(action_ctx) + " Error transpiling action " + name + \
				": Legal actions for a function of type " + type_t + " are: " + ", ".join(actions))

		return self.cpp_actions[name_lower](parameters, subtype, action_ctx)

	def transpile_function_call_cpp(self, name, parameter_ctx_list, type_t, subtype, action_ctx):
		# This was the name of a function, and a function takes no parameters:
		if len(parameter_ctx_list) > 0:
			sys.exit("line " + get_line_and_column(action_ctx) + " A function call takes no parameters")

		element = elements.get(name)
		if element is None or element.base_type != BASE_TYPE_FUNCTION:
			sys.exit("line " + get_line_and_column(action_ctx) + " No function with the name " + name + " exists")

		# element is a Function
		
		# A function of type Filter can only call functions of type Filter,
		# a function of type Nat can only call functions of type Nat, etc.
		if element.type_t.lower() != type_t.lower():
			sys.exit("line " + get_line_and_column(action_ctx) + " Error transpiling call to " + \
				name + ": A function of type " + type_t + " can only call functions of the same type")

		if element.subtype.lower() not in legal_nested_subtypes[subtype.lower()]:
			sys.exit("line " + get_line_and_column(action_ctx) + " Cannot call a function of subtype " + \
				element.subtype + " inside a function of subtype " + subtype)

		# return e.process()
		# Cannot call this and use the element's process method and res attribute because
		# the pckt name will be affected of/be different based on the subtype of the parent function
		# Therefore:
		return transpile_function_cpp(element.type_t, element.subtype, element.ctx, subtype)

	def transpile_accept_cpp(self, parameter_ctx_list, subtype, action_ctx):
		# This was the accept action, and this takes no parameters:
		if len(parameter_ctx_list) > 0:
			sys.exit("line " + get_line_and_column(action_ctx) + " An accept action takes no parameters")

		return INCLUDEOS_ACCEPT

	def transpile_drop_cpp(self, parameter_ctx_list, subtype, action_ctx):
		# This was the drop action, and this takes no parameters:
		if len(parameter_ctx_list) > 0:
			sys.exit("line " + get_line_and_column(action_ctx) + " A drop action takes no parameters")
		
		return INCLUDEOS_DROP

	def transpile_log_cpp(self, parameter_ctx_list, subtype, action_ctx):
		content = "std::cout << "

		if len(parameter_ctx_list) > 0:
			for i, p in enumerate(parameter_ctx_list):
				if p.string() is not None:
					content += resolve_value_cpp(p, subtype)
				else:
					t = get_cout_convert_to_type_cpp(p)
					if t == TO_UNSIGNED:
						content += "static_cast<unsigned>(" + resolve_value_cpp(p, subtype) + ")"
					elif t == TO_STRING:
						content += resolve_value_cpp(p, subtype) + ".to_string()"
					else:
						sys.exit("line " + get_line_and_column(p) + " Internal error: std::cout conversion for " + t + " has not been implemented")

				if i < (len(parameter_ctx_list) - 1):
					content += " << "

		return content + ";\n"

	def transpile_nat_cpp(self, type_nat, parameter_ctx_list, subtype, action_ctx):
		if type_nat != SNAT and type_nat != DNAT:
			sys.exit("line 1:0 Internal error in transpile_nat_cpp: Invalid NAT type " + type_nat)

		pckt_name = get_pckt_name_cpp(subtype)

		parameters = ""
		num_params = len(parameter_ctx_list)
		if num_params == 1:
			first = resolve_value_cpp(parameter_ctx_list[0])
			# parameters = pckt_name + ", " + INCLUDEOS_CT_ENTRY + ", " + str(first)
			parameters = IP_PCKT + ", " + INCLUDEOS_CT_ENTRY + ", " + str(first)
		elif num_params > 1:
			first 	= resolve_value_cpp(parameter_ctx_list[0])
			second 	= resolve_value_cpp(parameter_ctx_list[1])
			# parameters = pckt_name + ", " + INCLUDEOS_CT_ENTRY + ", {" + str(first) + ", " + str(second) + "}"
			parameters = IP_PCKT + ", " + INCLUDEOS_CT_ENTRY + ", {" + str(first) + ", " + str(second) + "}"
		else:
			sys.exit("line " + get_line_and_column(action_ctx) + " No arguments provided to " + type_nat)

		return NAT_OBJ_NAME + ARROW + type_nat + "(" + parameters + ");\n" + \
			self.transpile_accept_cpp([], subtype, action_ctx)

	def transpile_snat_cpp(self, parameter_ctx_list, subtype, action_ctx):
		return self.transpile_nat_cpp(SNAT, parameter_ctx_list, subtype, action_ctx)

	def transpile_dnat_cpp(self, parameter_ctx_list, subtype, action_ctx):
		return self.transpile_nat_cpp(DNAT, parameter_ctx_list, subtype, action_ctx)

Action_hdlr = Action_handler()

# ---- Helper functions for transpile_comparison_cpp ----

def construct_rng_comparison(resolved_rng_list, resolved_lhs):
	# A rng can only consist of integers or ipv4_addrs

	if len(resolved_rng_list) != 2:
		sys.exit("line 1:0 Internal error: Resolved list should be a rng consisting of two values instead of " + \
			str(resolved_rng_list))

	from_val 	= resolved_rng_list[0]
	to_val 		= resolved_rng_list[1]
	logical_op 	= AND

	return "(" + str(resolved_lhs) + " " + GREATER_THAN_OR_EQUAL + " " + str(from_val) + " " + logical_op + " " + \
		str(resolved_lhs) + " " + LESS_THAN_OR_EQUAL + " " + str(to_val) + ")"

def construct_comparisons_from_list(resolved_rhs_list, resolved_lhs, is_inner_list=False):
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
				result += construct_comparisons_from_list(rhs_val, resolved_lhs, True)
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
		return construct_rng_comparison(resolved_rhs_list, resolved_lhs)

def construct_comparison_cpp(comp_ctx, resolved_lhs, resolved_rhs, comparison_op, op):
	lhs_is_list = True if isinstance(resolved_lhs, list) else False
	rhs_is_list = True if isinstance(resolved_rhs, list) else False

	result = ""

	# If none of these are lists, we have the resolved values
	if not lhs_is_list and not rhs_is_list:
		if INCLUDEOS_IP4_CIDR_CLASS in str(resolved_rhs):
			if comparison_op.lower() != IN:
				sys.exit("line " + get_line_and_column(comp_ctx.comparison_operator()) + \
					" Invalid operator (" + comparison_op + "). Only the 'in' " + \
					"operator is valid when comparing a property to a range, cidr, list or object")

			result = str(resolved_rhs) + ".contains(" + str(resolved_lhs) + ")"
		else:
			if comparison_op.lower() == IN:
				sys.exit("line " + get_line_and_column(comp_ctx.comparison_operator()) + \
					" The 'in' operator can only be used when comparing a property to " + \
					"a range, cidr, list or object")

			result = str(resolved_lhs) + " " + comparison_op + " " + str(resolved_rhs)

		if op != "":
			result = "(" + result + ") " + op + " "

		return result

	# If any of the resolved sides is a list, the 'in' operator should have been used
	# (rng, ip4_cidr, list_t, obj)
	if comparison_op != IN:
		sys.exit("line " + get_line_and_column(comp_ctx.comparison_operator()) + " Invalid operator (" + \
			comparison_op + "). Only the 'in' operator is valid when comparing a value to a range, cidr, list or object")

	# If the 'in' operator has been used, only the resolved_rhs should be a list, not
	# the resolved_lhs
	if lhs_is_list:
		sys.exit("line " + get_line_and_column(comp_ctx.lhs().value()) + \
			" The left hand side of a comparison can not resolve to a set of values, e.g. " + \
			"a range, cidr, list or object")

	if rhs_is_list:
		result = construct_comparisons_from_list(resolved_rhs, resolved_lhs)

	if op != "":
		return "(" + result + ") " + op + " "

	return result

# ---- < Helper functions for transpile_comparison_cpp ----

def transpile_comparison_cpp(subtype, comp, op=""):
	# Resolve the values
	resolved_lhs = resolve_value_cpp(comp.lhs().value(), subtype)
	comparison_op = comp.comparison_operator().getText()
	resolved_rhs = resolve_value_cpp(comp.rhs().value(), subtype)

	# And construct the comparison(s) based on the resolved values
	return construct_comparison_cpp(comp, resolved_lhs, resolved_rhs, comparison_op, op)

def transpile_bool_expr_cpp(type_t, subtype, expr, op=""):
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

		content += transpile_comparison_cpp(subtype, expr.comparison(), op)

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
		return content + resolve_value_cpp(expr.value())

	# Recursion:
	if isinstance(expr, list):
		# Optional not and parentheses around the list of bool_exprs

		if hasattr(expr, 'Not') and expr.Not() is not None:
			content += NOT
		if hasattr(expr, 'Parenthesis_start') and expr.Parenthesis_start() is not None:
			content += expr.Parenthesis_start().getText()

		for i, e in enumerate(expr):
			content += transpile_bool_expr_cpp(type_t, subtype, e)
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
		
		content += transpile_bool_expr_cpp(type_t, subtype, expr.bool_expr(), logical_op)

		if hasattr(expr, 'Parenthesis_end') and expr.Parenthesis_end() is not None:
			content += expr.Parenthesis_end().getText()

		return content

def transpile_conditional_cpp(type_t, subtype, cond):
	content = ""
	bodies = cond.body()

	if hasattr(cond, 'If') and cond.If() is not None:
		# If-body is always first (index 0)
		content += cond.If().getText() + " " + transpile_bool_expr_cpp(type_t, subtype, cond) + \
			" {\n" + transpile_body_elements_cpp(type_t, subtype, bodies[0].body_element()) + "}\n"

	if hasattr(cond, 'Else') and cond.Else() is not None:
		# Else-body is always second/last (index 1)
		content += cond.Else().getText() + " {\n" + \
			transpile_body_elements_cpp(type_t, subtype, bodies[1].body_element()) + "}\n"
	
	return content

def transpile_body_elements_cpp(type_t, subtype, body_elements):
	content = ""

	for e in body_elements:
		if e.conditional() is not None:
			content += transpile_conditional_cpp(type_t, subtype, e.conditional())
		
		elif e.action() is not None:
			content += Action_hdlr.transpile_action_cpp(type_t, subtype, e.action())
		
		elif e.function() is not None:
			# Validate if valid type_t and subtype
			nested_type_t 	= e.function().type_t().getText()
			nested_subtype 	= e.function().subtype().getText()

			# Can only nest functions of the same type_t
			if type_t.lower() != nested_type_t.lower():
				sys.exit("line " + get_line_and_column(e.function().type_t()) + " You cannot create a function of type " + \
					nested_type_t + " inside a function of type " + type_t)

			# If this is a function, we have to validate that the subtype is legal based on the subtype of
			# the parent function
			if nested_subtype.lower() not in legal_nested_subtypes[subtype.lower()]:
				sys.exit("line " + get_line_and_column(e.function().subtype()) + " You cannot create a function of subtype " + \
					nested_subtype + " inside a function of subtype " + subtype)

			content += transpile_function_cpp(nested_type_t, nested_subtype, e.function(), subtype)

	return content

# Main function - starting point to transpile a NaCl function:
def transpile_function_cpp(type_t, subtype, ctx, parent_subtype=""):
	# Display an error message if the function is a Filter and does not end in a default verdict
	if type_t == TYPE_FILTER:
		elements = list(ctx.body().body_element())
		last_element = elements[len(elements) - 1]
		if last_element.action() is None or last_element.action().getText() not in valid_default_filter_verdicts:
			sys.exit("line " + get_line_and_column(ctx) + " Missing default verdict at the end of this Filter")

	# Return a string with all the code
	content = ""

	if parent_subtype == "":
		content += INCLUDEOS_CT_ENTRY_NULLPTR_CHECK

	is_ip = subtype.lower() == IP
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
		
		protocol_method = Ip_obj.resolve_method_cpp(PROTOCOL, ctx)
		protocol_val 	= Ip_obj.resolve_protocol_cpp(subtype, ctx)
		pckt_cast 		= get_pckt_cast_cpp(subtype, ctx)
		
		# If we are in a nested function and the parent function was not IP,
		# we have another pckt_name than 'pckt' to take into account:
		if parent_subtype == "" or parent_subtype == IP:
			content += "if (" + IP_PCKT + get_access_op_cpp(IP) + protocol_method + " " + EQUALS + " " + protocol_val + ") {\n" + \
				pckt_cast + "\n\n"
		elif parent_subtype != "" and subtype.lower() != parent_subtype and parent_subtype != IP:
			# If subtype == parent_subtype, we don't need this if-check on protocol at all (has been tested above in the C++ code)
			parent_pckt_name = get_pckt_name_cpp(parent_subtype)
			parent_access_op = get_access_op_cpp(parent_subtype)

			if parent_subtype == ICMP:
				protocol_method = INCLUDEOS_ICMP_IP_ACCESS_METHOD + parent_access_op + protocol_method

			content += "if (" + parent_pckt_name + parent_access_op + protocol_method + " " + EQUALS + " " + protocol_val + ") {\n" + \
				pckt_cast + "\n\n"

	# 2. Main operation - produces the main content:
	if parent_subtype != "" and is_ip:
		# We have to change the name of the ip pckt and we do this by sending in the parent_subtype
		# instead of the subtype
		content += transpile_body_elements_cpp(type_t, parent_subtype, ctx.body().body_element())
	else:
		content += transpile_body_elements_cpp(type_t, subtype, ctx.body().body_element())

	# 3. After the main content:
	if not is_ip:
		# Finish the if added above
		if subtype.lower() != parent_subtype:
			content += "}\n"
	
	return content
