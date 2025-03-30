#!/bin/bash

# PKG
PKG_NAME="mini_stream"

mkdir -p $SRCDIR/$PKG_NAME

cp Makefile *.c $SRCDIR/$PKG_NAME

make MARCH="armv8-a+sve" -C $SRCDIR/$PKG_NAME

make MARCH="armv8-a+sve"  M5_PREFIX=/usr -C $SRCDIR/$PKG_NAME

install -D -m 0755 -t $BENCHD/$PKG_NAME/bin $SRCDIR/$PKG_NAME/*.x
