# NaCl

1. Install antlr4 exactly like described under Quick start: http://www.antlr.org/
   * To use the python program I think there was also another step using pip, but don't know if it was really necessary.

2. Generate python parser / lexer for `NaCl.g4` grammar WITH visitor (NaClVisitor.py): `antlr4 -Dlanguage=Python2 NaCl.g4 -visitor`
3. Make transpiler program executable: `chmod u+x NaCl.py`
4. run with `cat nacl.txt | ./NaCl.py`
5. For testing, using the `grun` program (alias really) is nice. This requires that you generate the java lexer / parser
6. `antlr4 NaCl.g4 && javac NaCl*.java`
7. `cat nacl.txt | grun NaCl prog -gui`
