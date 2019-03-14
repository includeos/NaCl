
from conans import ConanFile,tools
import shutil

def get_version():
    git = tools.Git()
    try:
        prev_tag = git.run("describe --tags --abbrev=0")
        commits_behind = int(git.run("rev-list --count %s..HEAD" % (prev_tag)))
        # Commented out checksum due to a potential bug when downloading from bintray
        #checksum = git.run("rev-parse --short HEAD")
        if prev_tag.startswith("v"):
            prev_tag = prev_tag[1:]
        if commits_behind > 0:
            prev_tag_split = prev_tag.split(".")
            prev_tag_split[-1] = str(int(prev_tag_split[-1]) + 1)
            output = "%s-%d" % (".".join(prev_tag_split), commits_behind)
        else:
            output = "%s" % (prev_tag)
        return output
    except:
        return '0.0.0'

class NaClConan(ConanFile):
    name = 'NaCl'
    version = get_version()
    license = 'Apache-2.0'
    description='NaCl is a configuration language for IncludeOS that you can use to add for example interfaces and firewall rules to your service.'
    url='https://github.com/includeos/NaCl'

    scm = {
        "type" : "git",
        "url" : "auto",
        "subfolder": ".",
        "revision" : "auto"
    }

    default_user="includeos"
    default_channel="test"

    def build(self):
        #you need antlr4 installed to do this
        self.run("antlr4 -Dlanguage=Python2 NaCl.g4 -visitor")

    def package(self):
        name='NaCl'
        self.copy('*',dst=name+"/subtranspilers",src="subtranspilers")
        self.copy('*',dst=name+"/type_processors",src="type_processors")
        self.copy('*.py',dst=name,src=".")
        self.copy('cpp_template.mustache',dst=name,src='.')
        self.copy('NaCl.tokens',dst=name,src=".")
        self.copy('NaClLexer.tokens',dst=name,src=".")

    def package_id(self):
        self.info.header_only()

    def deploy(self):
        self.copy("*",dst="NaCl",src="NaCl")
