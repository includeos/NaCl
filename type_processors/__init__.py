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

import pkgutil
import sys
import os

def init(nacl_state):
    # print "Init type_processors"

    # If we already know the package name:
    # from iface import init as init_iface
    # init_iface(nacl_state)

    # Dynamically (if exists in folder):

    # dirname = "type_processors"
    # Get the absolute path to the directory that this file is in (type_processors):
    dirname = os.path.dirname(os.path.abspath(__file__))

    for importer, package_name, _ in pkgutil.iter_modules([dirname]):
        full_package_name = '%s.%s' % (dirname, package_name)
        if full_package_name not in sys.modules:
            module = importer.find_module(package_name).load_module(full_package_name)
            # print module
            module.init(nacl_state)
