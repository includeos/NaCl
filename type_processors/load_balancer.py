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
# To avoid: <...>/NaCl/type_processors/load_balancer.py:1: RuntimeWarning: Parent module '<...>/NaCl/type_processors' not found while handling absolute import

# TODO later: Own mustache file as well for Load_balancer - then import into main mustache file if possible

from NaCl import exit_NaCl, Typed
from shared import *
# TCP, predefined_values_cpp

TYPE_LOAD_BALANCER = "load_balancer"

# ---- Load_balancer keys ----

LB_KEY_LAYER = "layer"
LB_KEY_CLIENTS = "clients"
LB_KEY_SERVERS = "servers"

predefined_lb_keys = [
	LB_KEY_LAYER,
	LB_KEY_CLIENTS,
	LB_KEY_SERVERS
]

LB_KEY_IFACE = "iface"
LB_KEY_PORT = "port"

LB_CLIENTS_KEY_WAIT_QUEUE_LIMIT = "wait_queue_limit"
LB_CLIENTS_KEY_SESSION_LIMIT = "session_limit"

predefined_lb_clients_keys = [
	LB_KEY_IFACE,
	LB_KEY_PORT,
	LB_CLIENTS_KEY_WAIT_QUEUE_LIMIT,
	LB_CLIENTS_KEY_SESSION_LIMIT
]

LB_SERVERS_KEY_ALGORITHM = "algorithm"
LB_SERVERS_KEY_POOL = "pool"

predefined_lb_servers_keys = [
	LB_KEY_IFACE,
	LB_SERVERS_KEY_ALGORITHM,
	LB_SERVERS_KEY_POOL
]

LB_NODE_KEY_ADDRESS = "address"

predefined_lb_node_keys = [
	LB_NODE_KEY_ADDRESS,
	LB_KEY_PORT
]

# Load balancer algorithms
# Note: Only round_robin is supported in microLB for now (the algo/algorithm field is ignored)
ROUND_ROBIN = "round_robin"

# FEWEST_CONNECTIONS = "fewest_connections"
valid_lb_servers_algos = [
	ROUND_ROBIN
	# FEWEST_CONNECTIONS
]

INCLUDEOS_ROUND_ROBIN = ROUND_ROBIN

# Registering INCLUDEOS_ROUND_ROBIN in predefined_values_cpp dictionary in shared.py
predefined_values_cpp[ROUND_ROBIN] = INCLUDEOS_ROUND_ROBIN

# Load balancer layers

VALID_LB_LAYERS = [
	TCP
]

# ---- TEMPLATE KEYS (pystache) ----

TEMPLATE_KEY_LOAD_BALANCERS         = "load_balancers"

TEMPLATE_KEY_INDEX                  = "index"
TEMPLATE_KEY_PORT                   = "port"
TEMPLATE_KEY_LB_LAYER               = "layer"
TEMPLATE_KEY_LB_ALGORITHM           = "algorithm"
TEMPLATE_KEY_LB_WAIT_QUEUE_LIMIT    = "wait_queue_limit"
TEMPLATE_KEY_LB_SESSION_LIMIT       = "session_limit"
TEMPLATE_KEY_LB_CLIENTS_IFACE       = "clients_iface_name"
TEMPLATE_KEY_LB_SERVERS_IFACE       = "servers_iface_name"
TEMPLATE_KEY_LB_POOL                = "pool"
TEMPLATE_KEY_LB_NODE_ADDRESS        = "address"
TEMPLATE_KEY_LB_NODE_PORT           = "port"

TEMPLATE_KEY_HAS_LOAD_BALANCERS     = "has_load_balancers"

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

        if self.nacl_state.exists_in_pystache_list(TEMPLATE_KEY_LOAD_BALANCERS, TEMPLATE_KEY_LB_LAYER, layer):
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

        self.nacl_state.append_to_pystache_data_list(TEMPLATE_KEY_LOAD_BALANCERS, {
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

    # Overriding
    def validate_dictionary_key(self, key, parent_key, level, value_ctx):
        if level == 1:
            if key not in predefined_lb_keys:
                exit_NaCl(value_ctx, "Invalid Load_balancer member " + key)
        elif level == 2:
            if parent_key == "":
                exit_NaCl(value_ctx, "Internal error: Parent key of " + key + " has not been given")
            if parent_key == LB_KEY_CLIENTS and key not in predefined_lb_clients_keys:
                exit_NaCl(value_ctx, "Invalid Load_balancer member " + key + " in " + self.name + "." + parent_key)
            if parent_key == LB_KEY_SERVERS and key not in predefined_lb_servers_keys:
                exit_NaCl(value_ctx, "Invalid Load_balancer member " + key + " in " + self.name + "." + parent_key)
        else:
            exit_NaCl(value_ctx, "Invalid Load_balancer member " + key)

    # Overriding
    def resolve_dictionary_value(self, dictionary, key, value_ctx):
        found_element_value = value_ctx.getText()

        if key == LB_KEY_LAYER or key == LB_SERVERS_KEY_ALGORITHM:
            found_element_value = found_element_value.lower()

        if key == LB_KEY_LAYER:
            if value_ctx.value_name() is None or found_element_value not in VALID_LB_LAYERS:
                exit_NaCl(value_ctx, "Invalid " + LB_KEY_LAYER + " value (" + value_ctx.getText() + ")")
        elif key == LB_KEY_IFACE:
            # Then the Iface element's name is to be added, not the transpiled Iface
            if value_ctx.value_name() is None:
                exit_NaCl(value_ctx, "Load_balancer member " + LB_KEY_IFACE + " contains an invalid value (" + \
                    found_element_value + ")")
            element = self.nacl_state.elements.get(found_element_value)
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
                e = self.nacl_state.elements.get(element_name)
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
                    e = self.nacl_state.elements.get(element_name)
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
                    n[node_key] = self.nacl_state.transpile_value(pair.value())

                if n.get(LB_NODE_KEY_ADDRESS) is None or n.get(LB_KEY_PORT) is None:
                    exit_NaCl(node, "An object in a " + LB_SERVERS_KEY_POOL + " needs to specify " + ", ".join(predefined_lb_node_keys))

                pool.append(n)

            found_element_value = pool
        elif key == LB_KEY_CLIENTS or key == LB_KEY_SERVERS:
            if value_ctx.value_name() is not None:
                element_name = value_ctx.value_name().getText()
                e = self.nacl_state.elements.get(element_name)
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
                self.validate_dictionary_key(k, key, 2, value_ctx)
                # Then resolve the value
                self.resolve_dictionary_value(found_element_value, k, pair.value())
        else:
            found_element_value = self.nacl_state.transpile_value(value_ctx)

        # Add found value
        dictionary[key] = found_element_value

    def process(self):
        if self.res is None:
            # Then process

            self.process_ctx()
            self.process_assignments()
            self.add_load_balancer()

            self.res = self.members

        return self.res

    # Called from handle_input (NaCl.py) right before rendering, after the NaCl file has been processed
    # Register the last data here that can not be registered before this (set has-values f.ex.)
    @staticmethod
    def final_registration(nacl_state):
        load_balancers_is_empty = nacl_state.pystache_list_is_empty(TEMPLATE_KEY_LOAD_BALANCERS)

        if not load_balancers_is_empty:
            nacl_state.register_pystache_data_object(TEMPLATE_KEY_HAS_LOAD_BALANCERS, True)

# < Load_balancer

def create_load_balancer_pystache_lists(nacl_state):
    nacl_state.create_pystache_data_lists([
        TEMPLATE_KEY_LOAD_BALANCERS
    ])

def init(nacl_state):
    # print "Init load_balancer: Load_balancer"
    nacl_state.add_type_processor(TYPE_LOAD_BALANCER, Load_balancer)
    create_load_balancer_pystache_lists(nacl_state)
