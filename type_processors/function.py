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
# To avoid: <...>/NaCl/type_processors/function.py:1: RuntimeWarning: Parent module '<...>/NaCl/type_processors' not found while handling absolute import

from NaCl import exit_NaCl, Element, CPP
from subtranspilers.function_transpiler import FUNCTION_TRANSPILER, ACCEPT, DROP
from shared import *

TYPE_FILTER 		= "filter"
TYPE_REWRITE 		= "rewrite"
# Moved to shared.py: TYPE_NAT = "nat"

VALID_DEFAULT_FILTER_VERDICTS = [
	ACCEPT,
	DROP
]

# ---- TEMPLATE KEYS (pystache) ----

TEMPLATE_KEY_CONTENT		= "content"
TEMPLATE_KEY_FILTERS 		= "filters"
TEMPLATE_KEY_NATS 			= "nats"
TEMPLATE_KEY_REWRITES 		= "rewrites"
TEMPLATE_KEY_HAS_FUNCTIONS  = "has_functions"
# Moved to shared.py: TEMPLATE_KEY_HAS_NATS = "has_nats"

# -------------------- class Function --------------------

# Filter and Nat are examples of functions

class Function(Element):
    def __init__(self, nacl_state, idx, name, ctx, base_type, type_t, subtype):
        super(Function, self).__init__(nacl_state, idx, name, ctx, base_type)
        self.type_t 	= type_t
        self.subtype 	= subtype

        self.handle_as_untyped = False # Necessary?

    def transpile_function(self):
        return self.nacl_state.subtranspilers[FUNCTION_TRANSPILER].transpile(self.type_t, self.subtype, self.ctx)

    def add_function(self):
        # Only if a function is mentioned in an assignment that is a push or
        # an Iface's chain, should it be added to filters/nats/rewrites pystache list

        pystache_function_obj = {
            TEMPLATE_KEY_NAME: 		self.name,
            TEMPLATE_KEY_TITLE: 	self.name.title(),
            TEMPLATE_KEY_CONTENT: 	self.res 	# Contains transpiled content
        }

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
                            if last_element.action() is None or last_element.action().getText() not in VALID_DEFAULT_FILTER_VERDICTS:
                                exit_NaCl(self.ctx, "Missing default verdict at the end of this Filter")

                        if type_t_lower == TYPE_FILTER:
                            self.nacl_state.append_to_pystache_data_list(TEMPLATE_KEY_FILTERS, pystache_function_obj)
                        elif type_t_lower == TYPE_NAT:
							self.nacl_state.append_to_pystache_data_list(TEMPLATE_KEY_NATS, pystache_function_obj)
                        elif type_t_lower == TYPE_REWRITE:
							self.nacl_state.append_to_pystache_data_list(TEMPLATE_KEY_REWRITES, pystache_function_obj)
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
                            if last_element.action() is None or last_element.action().getText() not in VALID_DEFAULT_FILTER_VERDICTS:
                                exit_NaCl(self.ctx, "Missing default verdict at the end of this Filter")

                        if type_t_lower == TYPE_FILTER:
                            self.nacl_state.append_to_pystache_data_list(TEMPLATE_KEY_FILTERS, pystache_function_obj)
                        elif type_t_lower == TYPE_NAT:
                            self.nacl_state.append_to_pystache_data_list(TEMPLATE_KEY_NATS, pystache_function_obj)
                        elif type_t_lower == TYPE_REWRITE:
                            self.nacl_state.append_to_pystache_data_list(TEMPLATE_KEY_REWRITES, pystache_function_obj)
                        else:
                            exit_NaCl(self.ctx.type_t(), "Functions of type " + self.type_t + " are not handled")
                        return self.res

    # Main processing method
    def process(self):
        if self.res is None:
            self.res = self.transpile_function()
            self.add_function()
        return self.res

    # Called from handle_input (NaCl.py) right before rendering, after the NaCl file has been processed
    # Register the last data here that can not be registered before this (set has-values f.ex.)
    @staticmethod
    def final_registration(nacl_state):
        # TODO: Function is added 3 times to nacl_state's nacl_type_processors and this method
        # is therefore called 3 times (because of Filter, Nat and Rewrite) - make sure it is only
        # called once by f.ex. checking if the pystache lists TEMPLATE_KEY_HAS_FUNCTIONS,
        # TEMPLATE_KEY_ENABLE_CT and TEMPLATE_KEY_HAS_NATS already exist?

        filters_is_empty = nacl_state.pystache_list_is_empty(TEMPLATE_KEY_FILTERS)
        nats_is_empty = nacl_state.pystache_list_is_empty(TEMPLATE_KEY_NATS)

        if (not filters_is_empty) or (not nats_is_empty):
            nacl_state.register_pystache_data_object(TEMPLATE_KEY_HAS_FUNCTIONS, True)
            nacl_state.register_pystache_data_object(TEMPLATE_KEY_ENABLE_CT, True)

        if not nats_is_empty:
            nacl_state.register_pystache_data_object(TEMPLATE_KEY_HAS_NATS, True)

# < class Function

def create_function_pystache_lists(nacl_state):
    nacl_state.create_pystache_data_lists([
        TEMPLATE_KEY_FILTERS,
        TEMPLATE_KEY_NATS,
        TEMPLATE_KEY_REWRITES
	])
    # So pystache/mustache lists in nacl_state: filters, nats, rewrites

def init(nacl_state):
    # print "Init function: Function (Filter, Nat, Rewrite)"

    # Moved to subtranspilers/function_transpiler.py:
    # nacl_state.register_subtranspiler(FUNCTION_TRANSPILER, Cpp_function_transpiler(nacl_state))

    nacl_state.add_type_processor(TYPE_FILTER, Function)
    nacl_state.add_type_processor(TYPE_REWRITE, Function)
    nacl_state.add_type_processor(TYPE_NAT, Function)

    create_function_pystache_lists(nacl_state)
