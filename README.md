# NaCl

NaCl is a configuration language for IncludeOS that you can use to add for example interfaces and firewall rules to your service.

Documentation: http://includeos.readthedocs.io/en/latest/NaCl.html

1. Install antlr4 exactly like described under Quick start: http://www.antlr.org/
2. `pip install antlr4-python2-runtime`
3. `pip install pystache`
4. Generate python parser / lexer for `NaCl.g4` grammar WITH visitor (NaClVisitor.py): `antlr4 -Dlanguage=Python2 NaCl.g4 -visitor`
5. Make transpiler program executable: `chmod u+x NaCl.py`
6. run with `cat examples/nacl.nacl | ./NaCl.py`
7. For testing, using the `grun` program (alias really) is nice. This requires that you generate the java lexer / parser
8. `antlr4 NaCl.g4 && javac NaCl*.java`
9. `cat examples/nacl.nacl | grun NaCl prog -gui`

### Creating NaCl conan package

The [conanfile.py](conanfile.py) contains the recipe for building a conan package.

You can set up your remotes and profiles from [conan_config](https://github.com/includeos/conan_config)

To build the NaCl package:

```
  conan create <path to NaCl repo> includeos/latest -pr <profile name>
```

To upload the package:

```
  conan upload --all -r includeos NaCl/<version>@includeos/latest
```
> **Note:** For more information checkout the [Jenkinsfile](Jenkinsfile)
