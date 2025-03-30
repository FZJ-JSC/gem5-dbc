#!/bin/bash

# PKG
PKG_NAME="hpcg"
PKG_VER="master"
PKG_GIT="https://github.com/hpcg-benchmark/hpcg.git"

git -C $SRCDIR clone --depth 1 --branch $PKG_VER $PKG_GIT

for P in *.patch; do
    patch -d $SRCDIR/$PKG_NAME -p1 < $P
done

cmake -B $BLDDIR/$PKG_NAME $SRCDIR/$PKG_NAME -DCMAKE_BUILD_TYPE="Release" -DHPCG_ENABLE_CONTIGUOUS_ARRAYS="ON" -DHPCG_ENABLE_OPENMP="ON" -DHPCG_USE_M5="OFF"

make  -C $BLDDIR/$PKG_NAME -j$(nproc)

install -D -m 0755 -t $BENCHD/$PKG_NAME/bin $BLDDIR/$PKG_NAME/xhpcg

cmake -B $BLDDIR/$PKG_NAME $SRCDIR/$PKG_NAME -DCMAKE_BUILD_TYPE="Release" -DHPCG_ENABLE_CONTIGUOUS_ARRAYS="ON" -DHPCG_ENABLE_OPENMP="ON" -DHPCG_USE_M5="ON"

make  -C $BLDDIR/$PKG_NAME -j$(nproc)

install -D -m 0755 -t $BENCHD/$PKG_NAME/bin $BLDDIR/$PKG_NAME/xhpcg-m5
