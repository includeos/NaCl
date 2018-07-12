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
# To avoid: <...>/NaCl/type_processors/timer.py:1: RuntimeWarning: Parent module '<...>/NaCl/type_processors' not found while handling absolute import

from NaCl import exit_NaCl, Typed

# -------------------- CONSTANTS Timer --------------------

TYPE_TIMER = "timer"

# ---- Timer keys ----

TIMER_KEY_INTERVAL  = "interval"
TIMER_KEY_DATA      = "data"

PREDEFINED_TIMER_KEYS = [
	TIMER_KEY_INTERVAL,
	TIMER_KEY_DATA
]

# ---- Timer values ----

TIMER_DATA_VALUE_TIMESTAMP      = "timestamp"
TIMER_DATA_VALUE_STATS          = "stats"
TIMER_DATA_VALUE_MEMORY         = "memory"
TIMER_DATA_VALUE_CPU            = "cpu"
# TIMER_DATA_VALUE_STORAGE      = "storage"
TIMER_DATA_VALUE_LB             = "lb"
TIMER_DATA_VALUE_STACK_SAMPLING = "stack-sampling"
TIMER_DATA_VALUE_TIMERS         = "timers"

VALID_TIMER_DATA = [
    TIMER_DATA_VALUE_TIMESTAMP,
    TIMER_DATA_VALUE_STATS,
    TIMER_DATA_VALUE_MEMORY,
    TIMER_DATA_VALUE_CPU,
    # TIMER_DATA_VALUE_STORAGE,
    TIMER_DATA_VALUE_LB,
    TIMER_DATA_VALUE_STACK_SAMPLING,
    TIMER_DATA_VALUE_TIMERS
]

# -------------------- TEMPLATE KEYS (pystache) --------------------

TEMPLATE_KEY_TIMERS     = "timers"
TEMPLATE_KEY_INTERVAL   = TIMER_KEY_INTERVAL
TEMPLATE_KEY_DATA       = TIMER_KEY_DATA
TEMPLATE_KEY_HAS_TIMERS = "has_timers"

TEMPLATE_KEY_HAS_TIMESTAMP      = "has_timestamp"
TEMPLATE_KEY_HAS_STATS          = "has_stats"
TEMPLATE_KEY_HAS_MEMORY         = "has_memory"
TEMPLATE_KEY_HAS_CPU            = "has_cpu"
# TEMPLATE_KEY_HAS_STORAGE      = "has_storage"
TEMPLATE_KEY_HAS_LB             = "has_lb"
TEMPLATE_KEY_HAS_STACK_SAMPLING = "has_stack_sampling"
TEMPLATE_KEY_TIMER_HAS_TIMERS   = "timer_has_timers"

# -------------------- class Timer --------------------

class Timer(Typed):
    def __init__(self, nacl_state, idx, name, ctx, base_type, type_t):
        super(Timer, self).__init__(nacl_state, idx, name, ctx, base_type, type_t)

    def add_timer(self):
        pystache_obj = {
            TEMPLATE_KEY_INTERVAL: self.members.get(TIMER_KEY_INTERVAL)
        }

        data = self.members.get(TIMER_KEY_DATA)
        if not isinstance(data, list):
            exit_NaCl(self.ctx, "Invalid value of Timer member " + TIMER_KEY_DATA + \
                ". It needs to be a list containing one or more of these values: " + ", ".join(VALID_TIMER_DATA))

        for val in data:
            if val == TIMER_DATA_VALUE_TIMESTAMP:
                pystache_obj[TEMPLATE_KEY_HAS_TIMESTAMP] = True
            elif val == TIMER_DATA_VALUE_STATS:
                pystache_obj[TEMPLATE_KEY_HAS_STATS] = True
            elif val == TIMER_DATA_VALUE_MEMORY:
                pystache_obj[TEMPLATE_KEY_HAS_MEMORY] = True
            elif val == TIMER_DATA_VALUE_CPU:
                pystache_obj[TEMPLATE_KEY_HAS_CPU] = True
            # elif val == TIMER_DATA_VALUE_STORAGE:
            #    pystache_obj[TEMPLATE_KEY_HAS_STORAGE] = True
            elif val == TIMER_DATA_VALUE_LB:
                pystache_obj[TEMPLATE_KEY_HAS_LB] = True
            elif val == TIMER_DATA_VALUE_STACK_SAMPLING:
                pystache_obj[TEMPLATE_KEY_HAS_STACK_SAMPLING] = True
            elif val == TIMER_DATA_VALUE_TIMERS:
                pystache_obj[TEMPLATE_KEY_TIMER_HAS_TIMERS] = True
            else:
                exit_NaCl(self.ctx, "Invalid value of Timer member " + TIMER_KEY_DATA + \
                    ". Valid values are: " + ", ".join(VALID_TIMER_DATA))

        self.nacl_state.append_to_pystache_data_list(TEMPLATE_KEY_TIMERS, pystache_obj)

    # Overriding
    def validate_dictionary_key(self, key, parent_key, level, value_ctx):
        class_name = self.get_class_name()

        if level == 1:
            if key.lower() not in PREDEFINED_TIMER_KEYS:
                exit_NaCl(value_ctx, "Invalid " + class_name + " member " + key)
        else:
            exit_NaCl(value_ctx, "Invalid " + class_name + " member " + key)

    # Overriding
    def resolve_dictionary_value(self, dictionary, key, value_ctx):
        value_text = value_ctx.getText()
        key_lower = key.lower() # Necessary?

        if key_lower == TIMER_KEY_INTERVAL:
            resolved_val = self.nacl_state.transpile_value(value_ctx)
            if not resolved_val.isdigit() or resolved_val == "0":
                exit_NaCl(value_ctx, "Invalid " + TIMER_KEY_INTERVAL + " value (" + value_text + "). It needs to resolve to a positive number (number of seconds)")
            dictionary[key_lower] = resolved_val
        elif key_lower == TIMER_KEY_DATA:
            if value_ctx.list_t() is None and value_ctx.value_name() is None:
                exit_NaCl(value_ctx, "Invalid " + TIMER_KEY_DATA + " value. It needs to be a list containing one or more of these values: " + ", ".join(VALID_TIMER_DATA))

            if value_ctx.value_name() is not None:
                element_name = value_ctx.value_name().getText()
                e = self.nacl_state.elements.get(element_name)
                if e is None:
                    exit_NaCl(value_ctx, "No element with the name " + element_name + " exists")
                if e.ctx.value().list_t() is None:
                    exit_NaCl(value_ctx, "Element " + element_name + " does not consist of a list")
                # Updating value_ctx to be the element e's ctx value
                value_ctx = e.ctx.value()

            data = []
            for i, data_type in enumerate(value_ctx.list_t().value_list().value()):
                if data_type.value_name() is None:
                    exit_NaCl(data_type, "Invalid " + TIMER_KEY_DATA + " value. It needs to be a list containing one or more of these values: " + \
                        ", ".join(VALID_TIMER_DATA))

                data_type_name = data_type.value_name().getText().lower()

                if data_type_name not in VALID_TIMER_DATA:
                    exit_NaCl(data_type, "Invalid " + TIMER_KEY_DATA + " value (" + data_type.getText() + "). Valid values are: " + ", ".join(VALID_TIMER_DATA))

                data.append(data_type_name)

            # Add found value
            dictionary[key_lower] = data

    # Main processing method
    def process(self):
        if self.res is None:
            # Then process

            self.process_ctx()
            self.process_assignments()
            self.add_timer()

            self.res = self.members

        return self.res

    # Called from handle_input (NaCl.py) right before rendering, after the NaCl file has been processed
    # Register the last data here that can not be registered before this (set has-values f.ex.)
    @staticmethod
    def final_registration(nacl_state):
        timers_is_empty = nacl_state.pystache_list_is_empty(TEMPLATE_KEY_TIMERS)

        if not timers_is_empty:
            nacl_state.register_pystache_data_object(TEMPLATE_KEY_HAS_TIMERS, True)

# < class Timer

def create_timer_pystache_lists(nacl_state):
    nacl_state.create_pystache_data_lists([
        TEMPLATE_KEY_TIMERS
    ])

def init(nacl_state):
    # print "Init timer: Timer"
    nacl_state.add_type_processor(TYPE_TIMER, Timer)
    create_timer_pystache_lists(nacl_state)
