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
# To avoid: <...>/NaCl/type_processors/gateway.py:1: RuntimeWarning: Parent module '<...>/NaCl/type_processors' not found while handling absolute import

from NaCl import exit_NaCl, Typed, CPP, DOT, BASE_TYPE_FUNCTION
from shared import *
# INCLUDEOS_ROUTER_OBJ_NAME, TRUE, FALSE

TYPE_GATEWAY = "gateway"

IFACE_IS_VLAN = "is_vlan"
IFACE_IS_NOT_VLAN = "is_not_vlan"

# ---- Gateway keys ----

GATEWAY_KEY_SEND_TIME_EXCEEDED 	= "send_time_exceeded"
GATEWAY_KEY_FORWARD 			= "forward"

GATEWAY_KEY_HOST 	= "host"
GATEWAY_KEY_NET 	= "net"
GATEWAY_KEY_NETMASK = "netmask"
GATEWAY_KEY_NEXTHOP = "nexthop"
GATEWAY_KEY_IFACE 	= "iface"
GATEWAY_KEY_COST 	= "cost"

# Valid keys for Gateway routes
PREDEFINED_GATEWAY_ROUTE_KEYS = [
	GATEWAY_KEY_HOST,
	GATEWAY_KEY_NET,
	GATEWAY_KEY_NETMASK,
	GATEWAY_KEY_NEXTHOP,
	GATEWAY_KEY_IFACE,
	GATEWAY_KEY_COST
]

# Valid Gateway keys for members that are not objects (routes)
PREDEFINED_GATEWAY_KEYS = [
	GATEWAY_KEY_SEND_TIME_EXCEEDED,
	GATEWAY_KEY_FORWARD
]

# ---- TEMPLATE KEYS (pystache) ----

TEMPLATE_KEY_GATEWAYS           = "gateways"
TEMPLATE_KEY_IP_FORWARD_IFACES  = "ip_forward_ifaces"
TEMPLATE_KEY_ROUTES             = "routes"
# Moved to shared.py: TEMPLATE_KEY_GATEWAY_PUSHES = "pushes_gateway"

TEMPLATE_KEY_HAS_GATEWAYS       = "has_gateways"

# -------------------- Gateway --------------------

class Gateway(Typed):
    def __init__(self, nacl_state, idx, name, ctx, base_type, type_t):
        super(Gateway, self).__init__(nacl_state, idx, name, ctx, base_type, type_t)

        self.handle_as_untyped = False
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

            if key not in PREDEFINED_GATEWAY_ROUTE_KEYS:
                exit_NaCl(pair.key(), orig_key + " is not a valid Gateway route member. " + \
                    "Valid members are: " + ", ".join(PREDEFINED_GATEWAY_ROUTE_KEYS))

            if key != GATEWAY_KEY_IFACE:
                route_obj[key] = self.nacl_state.transpile_value(pair.value())
            else:
                # Then the Iface element's name is to be added to the route_obj,
                # not the transpiled Iface
                iface_name = pair.value().getText()

                if pair.value().value_name() is None:
                    exit_NaCl(pair.value(), "Gateway route member iface contains an invalid value (" + iface_name + ")")

                element = self.nacl_state.elements.get(iface_name)
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

                if route_pair.value().obj() is None and name not in PREDEFINED_GATEWAY_KEYS:
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
    # Overriding:
    def process_assignment(self, element_key):
        element = self.nacl_state.elements.get(element_key)

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

            if route_member not in PREDEFINED_GATEWAY_ROUTE_KEYS:
                exit_NaCl(element.ctx, route_member + " is not a valid Gateway route member. Valid members are: " + \
                    ", ".join(PREDEFINED_GATEWAY_ROUTE_KEYS))

            if route_member != GATEWAY_KEY_IFACE:
                route[route_member] = self.nacl_state.transpile_value(element.ctx.value())
            else:
                # Then the Iface element's name is to be added to the route obj,
                # not the transpiled Iface
                iface_name = element.ctx.value().getText()

                if element.ctx.value().value_name() is None:
                    exit_NaCl(element.ctx.value(), "Invalid iface value " + iface_name + " (the value must be the name of an Iface)")

                iface_element = self.nacl_state.elements.get(iface_name)
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
            element = self.nacl_state.elements.get(name)
            if element is None or element.base_type != BASE_TYPE_FUNCTION:
                exit_NaCl(function, "No function with the name " + name + " exists")

            if element.type_t.lower() == TYPE_NAT:
                exit_NaCl(function, "A Nat function cannot be pushed onto a Gateway's forward chain")

            function_names.append({TEMPLATE_KEY_FUNCTION_NAME: name, TEMPLATE_KEY_COMMA: (i < (num_functions - 1))})

        router_obj_name = INCLUDEOS_ROUTER_OBJ_NAME if self.nacl_state.language == CPP else exit_NaCl(self.ctx, \
            "Gateway can not transpile to other languages than C++")
        self.pushes.append({
            TEMPLATE_KEY_NAME:              router_obj_name,
            TEMPLATE_KEY_CHAIN:             chain,
            TEMPLATE_KEY_FUNCTION_NAMES:    function_names
        })

    def validate_and_process_not_route_members(self):
        for key, value_ctx in self.not_route_members.iteritems():
            if key == GATEWAY_KEY_SEND_TIME_EXCEEDED:
                resolved_value = self.nacl_state.transpile_value(value_ctx)
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
        iface_type_in_gateway = "" # collect the iface type (whether the iface is a vlan or not) of all ifaces in the gateway routes

        for _, route in self.members.iteritems():
            if GATEWAY_KEY_NETMASK not in route or \
                GATEWAY_KEY_IFACE not in route or \
                (GATEWAY_KEY_NET not in route and GATEWAY_KEY_HOST not in route):
                exit_NaCl(route.get("ctx"), "A Gateway route must specify " + GATEWAY_KEY_IFACE + ", " + \
                    GATEWAY_KEY_NETMASK + " and either " + GATEWAY_KEY_NET + " or " + GATEWAY_KEY_HOST)

            iface_name = route.get(GATEWAY_KEY_IFACE)

            # Verify that all routes contain ifaces of the same type (either vlan or not vlan)
            iface_element = self.nacl_state.elements.get(iface_name)
            # Make sure the Iface element has been processed before checking the vlan member
            iface_element.process()
            if iface_element.members.get(IFACE_KEY_VLAN) is None:
                if iface_type_in_gateway != "" and iface_type_in_gateway == IFACE_IS_VLAN:
                    exit_NaCl(self.ctx, "All iface members in a Gateway's routes must be of the same type (either only Ifaces with the vlan member set or only regular Ifaces)")
                iface_type_in_gateway = IFACE_IS_NOT_VLAN
            else:
                if iface_type_in_gateway != "" and iface_type_in_gateway == IFACE_IS_NOT_VLAN:
                    exit_NaCl(self.ctx, "All iface members in a Gateway's routes must be of the same type (either only Ifaces with the vlan member set or only regular Ifaces)")
                iface_type_in_gateway = IFACE_IS_VLAN

            # Add iface_name to ip_forward_ifaces pystache list if it is not in the
            # list already
            if iface_name is not None and not self.nacl_state.exists_in_pystache_list(TEMPLATE_KEY_IP_FORWARD_IFACES, TEMPLATE_KEY_IFACE, iface_name):
                self.nacl_state.append_to_pystache_data_list(TEMPLATE_KEY_IP_FORWARD_IFACES, {
                    TEMPLATE_KEY_IFACE: iface_name
                })

            # Add iface_name to enable_ct_ifaces pystache list if it is not in the
            # list already
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
        self.nacl_state.append_to_pystache_data_list(TEMPLATE_KEY_GATEWAYS, {
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

            # Add self.pushes to pystache data:
            self.nacl_state.register_pystache_data_object(TEMPLATE_KEY_GATEWAY_PUSHES, self.pushes)

        return self.res

    # Called from handle_input (NaCl.py) right before rendering, after the NaCl file has been processed
    # Register the last data here that can not be registered before this (set has-values f.ex.)
    @staticmethod
    def final_registration(nacl_state):
        gateways_is_empty = nacl_state.pystache_list_is_empty(TEMPLATE_KEY_GATEWAYS)
        if not gateways_is_empty:
            nacl_state.register_pystache_data_object(TEMPLATE_KEY_ENABLE_CT, True)
            nacl_state.register_pystache_data_object(TEMPLATE_KEY_HAS_GATEWAYS, True)

# < Gateway

def create_gateway_pystache_lists(nacl_state):
    nacl_state.create_pystache_data_lists([
        TEMPLATE_KEY_GATEWAYS,
        TEMPLATE_KEY_IP_FORWARD_IFACES
    ])

def init(nacl_state):
    # print "Init gateway: Gateway"
    nacl_state.add_type_processor(TYPE_GATEWAY, Gateway, True)
    create_gateway_pystache_lists(nacl_state)
