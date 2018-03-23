from NaCl import Function

# Move class Function(Element) here later

TYPE_FILTER 		= "filter"
TYPE_REWRITE 		= "rewrite"
TYPE_NAT 			= "nat"

def init(nacl_state):
    print "Init function: Function"
    nacl_state.add_type_processor(TYPE_FILTER, Function)
    nacl_state.add_type_processor(TYPE_REWRITE, Function)
    nacl_state.add_type_processor(TYPE_NAT, Function)
