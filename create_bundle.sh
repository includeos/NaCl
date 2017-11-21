#!/bin/bash

TARFILE="nacl_bin.tar.gz"
tar -zcvf $TARFILE bin
echo -e "> Created $TARFILE"
md5 $TARFILE
