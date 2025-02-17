#!/bin/bash

# PKG
PKG_NAME="ietubench"
PKG_VER="main"
PKG_GIT="https://github.com/FZJ-JSC/ietubench.git"

git -C $SRCDIR clone --depth 1 --branch $PKG_VER $PKG_GIT

for P in *.patch; do
    patch -d $SRCDIR/$PKG_NAME -p1 < $P
done

cmake -B $BLDDIR/$PKG_NAME $SRCDIR/$PKG_NAME -DCMAKE_BUILD_TYPE="Release" -DPROJECT_LOOP_LENGTHS="256;4096" -DPROJECT_USE_M5="OFF"

make  -C $BLDDIR/$PKG_NAME -j$(nproc)

install -D -m 0755 -t $BENCHD/$PKG_NAME/bin $BLDDIR/$PKG_NAME/src/micro/**/*.x

cmake -B $BLDDIR/$PKG_NAME $SRCDIR/$PKG_NAME -DCMAKE_BUILD_TYPE="Release" -DPROJECT_LOOP_LENGTHS="256;4096" -DPROJECT_USE_M5="ON"

make  -C $BLDDIR/$PKG_NAME -j$(nproc)

install -D -m 0755 -t $BENCHD/$PKG_NAME/bin $BLDDIR/$PKG_NAME/src/micro/**/*.x
