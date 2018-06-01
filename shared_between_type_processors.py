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

# Containing constants that needs to be available for more than one type_processor
# Mainly related to mustache

TEMPLATE_KEY_FUNCTION_NAME 	= "function_name"
TEMPLATE_KEY_COMMA 			= "comma"
TEMPLATE_KEY_IFACE 			= "iface"
TEMPLATE_KEY_CHAIN 			= "chain"
TEMPLATE_KEY_FUNCTION_NAMES = "function_names"
TEMPLATE_KEY_NAME 			= "name"
TEMPLATE_KEY_TITLE 			= "title"

# Constants closely connected to the Iface type_processor:
TYPE_IFACE = "iface"    # from type_processors.iface import TYPE_IFACE
TEMPLATE_KEY_IFACE_PUSHES = "pushes_iface"
TEMPLATE_KEY_ENABLE_CT_IFACES = "enable_ct_ifaces"

# Constants closely connected to the Gateway type_processor:
TEMPLATE_KEY_GATEWAY_PUSHES = "pushes_gateway"

# Constants closely connected to the Conntrack type_processor:
TEMPLATE_KEY_ENABLE_CT = "enable_ct"

# Constants closely connected to the Function type_processor:
TYPE_NAT = "nat"
TEMPLATE_KEY_HAS_NATS = "has_nats"
