# NaCl

1. Install antlr4 exactly like described under Quick start: http://www.antlr.org/
2. `pip install antlr4-python2-runtime`
3. `pip install pystache`
4. Generate python parser / lexer for `NaCl.g4` grammar WITH visitor (NaClVisitor.py): `antlr4 -Dlanguage=Python2 NaCl.g4 -visitor`
5. Make transpiler program executable: `chmod u+x NaCl.py`
6. run with `cat nacl.txt | ./NaCl.py`
7. For testing, using the `grun` program (alias really) is nice. This requires that you generate the java lexer / parser
8. `antlr4 NaCl.g4 && javac NaCl*.java`
9. `cat nacl.txt | grun NaCl prog -gui`
