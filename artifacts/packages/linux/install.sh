#!/bin/bash

# PKG
PKG_NAME="linux"
PKG_VER="5.15.68"
PKG_URL="https://mirrors.edge.kernel.org/pub/linux/kernel/v${PKG_VER%%.*}.x/$PKG_NAME-$PKG_VER.tar.xz"

# Build Linux Kernel
## Download Kernel sources
curl -L $PKG_URL -o $SRCDIR/$PKG_NAME-$PKG_VER.tar.xz
## Extract Kernel sources
tar -C $SRCDIR -xf $SRCDIR/$PKG_NAME-$PKG_VER.tar.xz

for P in *.patch; do
    patch -d $SRCDIR/$PKG_NAME-$PKG_VER -p1 < $P
done

## Copy Kernel config
cp $PKG_NAME-$PKG_VER.config  $SRCDIR/$PKG_NAME-$PKG_VER/.config
## Read Kernel config
make -C $SRCDIR/$PKG_NAME-$PKG_VER olddefconfig
## Set Kernel LOCALVERSION
$SRCDIR/$PKG_NAME-$PKG_VER/scripts/config --file  $SRCDIR/$PKG_NAME-$PKG_VER/.config --set-str LOCALVERSION "-gem5"
## Compile Kernel
make -C $SRCDIR/$PKG_NAME-$PKG_VER -j$(nproc) Image vmlinux 

# Move compiled binaries to $OUTDIR for download
mv $SRCDIR/$PKG_NAME-$PKG_VER/arch/arm64/boot/Image $OUTDIR/Image-$PKG_VER
mv $SRCDIR/$PKG_NAME-$PKG_VER/vmlinux               $OUTDIR/vmlinux-$PKG_VER

# Clean up
rm -rf $SRCDIR/$PKG_NAME-$PKG_VER.tar.xz
rm -rf $SRCDIR/$PKG_NAME-$PKG_VER