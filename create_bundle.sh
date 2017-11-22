#!/bin/bash

FILES="NaCl.tokens NaClLexer.py NaClLexer.tokens NaClListener.py NaClParser.py NaClVisitor.py"
TARFILE="nacl_bin.tar.gz"
tar -zcvf $TARFILE $FILES
echo -e "> Created $TARFILE"
md5 $TARFILE
