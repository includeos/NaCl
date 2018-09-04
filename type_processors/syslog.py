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
# To avoid: <...>/NaCl/type_processors/syslog.py:1: RuntimeWarning: Parent module '<...>/NaCl/type_processors' not found while handling absolute import

from NaCl import exit_NaCl, Typed

# -------------------- CONSTANTS Syslog --------------------

TYPE_SYSLOG = "syslog"

# ---- Syslog keys ----

SYSLOG_KEY_ADDRESS 	= "address"
SYSLOG_KEY_PORT 	= "port"

PREDEFINED_SYSLOG_KEYS = [
	SYSLOG_KEY_ADDRESS,
	SYSLOG_KEY_PORT
]

# ---- Syslog severity levels ----

EMERG = "emerg"
ALERT = "alert"
CRIT = "crit"
ERR = "err"
WARNING = "warning"
NOTICE = "notice"
INFO = "info"
DEBUG = "debug"

# ---- IncludeOS syslog severity levels

INCLUDEOS_SYSLOG_SEVERITY_EMERG = "LOG_EMERG"
INCLUDEOS_SYSLOG_SEVERITY_ALERT = "LOG_ALERT"
INCLUDEOS_SYSLOG_SEVERITY_CRIT = "LOG_CRIT"
INCLUDEOS_SYSLOG_SEVERITY_ERR = "LOG_ERR"
INCLUDEOS_SYSLOG_SEVERITY_WARNING = "LOG_WARNING"
INCLUDEOS_SYSLOG_SEVERITY_NOTICE = "LOG_NOTICE"
INCLUDEOS_SYSLOG_SEVERITY_INFO = "LOG_INFO"
INCLUDEOS_SYSLOG_SEVERITY_DEBUG = "LOG_DEBUG"

# ---- TEMPLATE KEYS (pystache) ----

TEMPLATE_KEY_SYSLOGS        = "syslogs"
TEMPLATE_KEY_ADDRESS        = "address"
TEMPLATE_KEY_PORT           = "port"

TEMPLATE_KEY_HAS_SYSLOGS    = "has_syslogs"

# -------------------- Syslog (settings) --------------------

class Syslog(Typed):
    def __init__(self, nacl_state, idx, name, ctx, base_type, type_t):
        super(Syslog, self).__init__(nacl_state, idx, name, ctx, base_type, type_t)

    def add_syslog(self):
        addr = self.members.get(SYSLOG_KEY_ADDRESS)
        port = self.members.get(SYSLOG_KEY_PORT)

        if addr is None or port is None:
            exit_NaCl(self.ctx, "Syslog address and/or port have not been specified")

        self.nacl_state.append_to_pystache_data_list(TEMPLATE_KEY_SYSLOGS, {
            TEMPLATE_KEY_ADDRESS: addr,
            TEMPLATE_KEY_PORT: port
        })

    # Overriding
    def validate_dictionary_key(self, key, parent_key, level, value_ctx):
        if level == 1:
            if key not in PREDEFINED_SYSLOG_KEYS:
                exit_NaCl(value_ctx, "Invalid Syslog member " + key)
        else:
            exit_NaCl(value_ctx, "Invalid Syslog member " + key)

    # Overriding
    def resolve_dictionary_value(self, dictionary, key, value):
        dictionary[key] = self.nacl_state.transpile_value(value)

    def process(self):
        if self.res is None:
            # Then process

            self.process_ctx()
            self.process_assignments()
            self.add_syslog()

            self.res = self.members

        return self.res

    # Called from handle_input (NaCl.py) right before rendering, after the NaCl file has been processed
    # Register the last data here that can not be registered before this (set has-values f.ex.)
    @staticmethod
    def final_registration(nacl_state):
        if not nacl_state.pystache_list_is_empty(TEMPLATE_KEY_SYSLOGS):
            nacl_state.register_pystache_data_object(TEMPLATE_KEY_HAS_SYSLOGS, True)

# < Syslog (settings)

def create_syslog_pystache_lists(nacl_state):
    nacl_state.create_pystache_data_lists([
        TEMPLATE_KEY_SYSLOGS
    ])

def init(nacl_state):
    # print "Init syslog: Syslog"
    nacl_state.add_type_processor(TYPE_SYSLOG, Syslog, True)
    create_syslog_pystache_lists(nacl_state)
