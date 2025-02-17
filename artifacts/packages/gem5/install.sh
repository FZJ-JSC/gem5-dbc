#!/bin/bash

# PKG
PKG_NAME="gem5"
PKG_VER="v24.0.0.1"
PKG_GIT="https://github.com/gem5/gem5.git"

git -C $SRCDIR clone --depth 1 --branch $PKG_VER $PKG_GIT

for P in *.patch; do
    patch -d $SRCDIR/$PKG_NAME -p1 < $P
done

## Compile m5 utility
make GEM5_DIST=$SRCDIR/$PKG_NAME -C $SRCDIR/$PKG_NAME/util/m5/src -f Makefile -j$(nproc)

## Install binaries
install -D -m 0755 $SRCDIR/$PKG_NAME/util/m5/src/m5       /sbin/m5
install -D -m 0755 $SRCDIR/$PKG_NAME/util/m5/src/libm5.a  /usr/lib/libm5.a

## Install headers
install -D -m 0644 $SRCDIR/$PKG_NAME/include/gem5/m5ops.h             /usr/include/$PKG_NAME/m5ops.h
install -D -m 0644 $SRCDIR/$PKG_NAME/include/gem5/asm/generic/m5ops.h /usr/include/$PKG_NAME/asm/generic/m5ops.h

## Compile bootloader
make -C $SRCDIR/$PKG_NAME/system/arm/bootloader/arm64 -f makefile -j$(nproc)

# Move compiled binaries to $BINDIR for download
mv $SRCDIR/$PKG_NAME/system/arm/bootloader/arm64/boot.arm64    $OUTDIR/boot.arm64-V1
mv $SRCDIR/$PKG_NAME/system/arm/bootloader/arm64/boot_v2.arm64 $OUTDIR/boot.arm64-V2

# Clean up
rm -rf $SRCDIR/$PKG_NAME
