import pkgutil
import sys

def init(nacl_state):
    print "init type_processors"

    # If we already know the package name:
    # from iface import init as init_iface
    # init_iface(nacl_state)

    # Dynamically (if exists in folder):
    dirname = "type_processors"
    for importer, package_name, _ in pkgutil.iter_modules([dirname]):
        full_package_name = '%s.%s' % (dirname, package_name)
        if full_package_name not in sys.modules:
            module = importer.find_module(package_name).load_module(full_package_name)
            # print module
            module.init(nacl_state)
