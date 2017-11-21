antlr4 -Dlanguage=Python2 NaCl.g4 -visitor -o bin

TARFILE="nacl_bin.tar.gz"
tar -zcvf $TARFILE bin
echo -e "> Created $TARFILE"
