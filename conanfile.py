import os
from conans import ConanFile, python_requires

conan_tools = python_requires("conan-tools/[>=1.0.0]@includeos/stable")

class NaClConan(ConanFile):
    name = 'NaCl'
    version = conan_tools.git_get_semver()
    license = 'Apache-2.0'
    description='NaCl is a configuration language for IncludeOS that you can use to add for example interfaces and firewall rules to your service.'
    url='https://github.com/includeos/NaCl'

    scm = {
        "type" : "git",
        "url" : "auto",
        "subfolder": ".",
        "revision" : "auto"
    }

    def build(self):
        #you need antlr4 installed to do this
        self.run("antlr4 -Dlanguage=Python2 NaCl.g4 -visitor")

    def package(self):
        name='bin'
        self.copy('*',dst=name+"/subtranspilers",src="subtranspilers")
        self.copy('*',dst=name+"/type_processors",src="type_processors")
        self.copy('*.py',dst=name,src=".")
        self.copy('cpp_template.mustache',dst=name,src='.')
        self.copy('NaCl.tokens',dst=name,src=".")
        self.copy('NaClLexer.tokens',dst=name,src=".")

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.env_info.path.append(os.path.join(self.package_folder, "bin"))

    def deploy(self):
        self.copy("*",dst="NaCl",src="NaCl")
