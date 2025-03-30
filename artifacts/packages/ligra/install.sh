#!/bin/bash

# PKG
PKG_NAME="ligra"
PKG_VER="master"
PKG_GIT="https://github.com/jshun/ligra"

git -C $SRCDIR clone --depth 1 --branch $PKG_VER $PKG_GIT

for P in *.patch; do
    patch -d $SRCDIR/$PKG_NAME -p1 < $P
done

make -C $SRCDIR/$PKG_NAME/apps -f Makefile.m5 -j$(nproc) MARCH=armv8.2-a OPENMP=1

install -D -m 0755 -t $BENCHD/$PKG_NAME/bin $SRCDIR/$PKG_NAME/apps/*.x

make -C $SRCDIR/$PKG_NAME/apps -f Makefile.m5 -j$(nproc) MARCH=armv8.2-a OPENMP=1 M5_PREFIX=/usr

install -D -m 0755 -t $BENCHD/$PKG_NAME/bin $SRCDIR/$PKG_NAME/apps/*-m5.x

make -C $SRCDIR/$PKG_NAME/utils -j$(nproc) rMatGraph adjGraphAddWeights

install -D -m 0755 -t $BENCHD/$PKG_NAME/bin $SRCDIR/$PKG_NAME/utils/rMatGraph $SRCDIR/$PKG_NAME/utils/adjGraphAddWeights
