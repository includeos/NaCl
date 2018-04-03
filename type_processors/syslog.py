from __future__ import absolute_import
# To avoid: <...>/NaCl/type_processors/syslog.py:1: RuntimeWarning: Parent module '<...>/NaCl/type_processors' not found while handling absolute import

from NaCl import exit_NaCl, Typed, TEMPLATE_KEY_ADDRESS, TEMPLATE_KEY_PORT

# -------------------- CONSTANTS Syslog --------------------

TYPE_SYSLOG = "syslog"

# ---- Syslog keys ----

SYSLOG_KEY_ADDRESS 	= "address"
SYSLOG_KEY_PORT 	= "port"

PREDEFINED_SYSLOG_KEYS = [
	SYSLOG_KEY_ADDRESS,
	SYSLOG_KEY_PORT
]

TEMPLATE_KEY_SYSLOGS        = "syslogs"
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

        # Old:
        # syslogs.append({ TEMPLATE_KEY_ADDRESS: addr, TEMPLATE_KEY_PORT: port })
        # New:
        self.nacl_state.append_to_pystache_data_list(TEMPLATE_KEY_SYSLOGS, {
            TEMPLATE_KEY_ADDRESS: addr,
            TEMPLATE_KEY_PORT: port
        })

    # Old:
    # def validate_syslog_key(self, key, parent_key, level, ctx):
    # New:
    # Overriding
    def validate_dictionary_key(self, key, parent_key, level, value_ctx):
        if level == 1:
            if key not in PREDEFINED_SYSLOG_KEYS:
                exit_NaCl(value_ctx, "Invalid Syslog member " + key)
        else:
            exit_NaCl(value_ctx, "Invalid Syslog member " + key)

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

    # Called from handle_input (NaCl.py) right before rendering, after the NaCl file has been processed
    # Register the last data here that can not be registered before this (set has-values f.ex.)
    @staticmethod
    def final_registration(nacl_state):
        # Previously in handle_input: nacl_state.register_pystache_data_object(TEMPLATE_KEY_HAS_SYSLOGS, (len(syslogs) > 0))
        if not nacl_state.pystache_list_is_empty(TEMPLATE_KEY_SYSLOGS):
            nacl_state.register_pystache_data_object(TEMPLATE_KEY_HAS_SYSLOGS, True)

# < Syslog (settings)

def create_syslog_pystache_lists(nacl_state):
    nacl_state.create_pystache_data_lists([
        TEMPLATE_KEY_SYSLOGS
    ])

def init(nacl_state):
    print "Init syslog: Syslog"

    nacl_state.add_type_processor(TYPE_SYSLOG, Syslog)

    create_syslog_pystache_lists(nacl_state)
