#!/bin/bash

PRVDIR=/tmp/provision/linux
SRCDIR=/root/sources
BINDIR=/root/binaries

LINUX_MIRROR="https://mirrors.edge.kernel.org"
LINUX_VER="5.15.68"
LINUX_MAJ="5"
LINUX_URL="$LINUX_MIRROR/pub/linux/kernel/v$LINUX_MAJ.x/linux-$LINUX_VER.tar.xz"

mkdir -p $SRCDIR $BINDIR

# Build Linux Kernel
## Download Kernel sources
curl -L $LINUX_URL -o $SRCDIR/linux-$LINUX_VER.tar.xz
## Extract Kernel sources
tar -C $SRCDIR -xf $SRCDIR/linux-$LINUX_VER.tar.xz
## Copy Kernel config
cp $PRVDIR/linux-$LINUX_VER.config  $SRCDIR/linux-$LINUX_VER/.config
## Read Kernel config
make -C $SRCDIR/linux-$LINUX_VER olddefconfig
## Set Kernel LOCALVERSION
$SRCDIR/linux-$LINUX_VER/scripts/config --file  $SRCDIR/linux-$LINUX_VER/.config --set-str LOCALVERSION "-gem5"
## Compile Kernel
make -C $SRCDIR/linux-$LINUX_VER -j$(nproc) Image vmlinux 

# Move compiled binaries to $BINDIR for download
mv $SRCDIR/linux-$LINUX_VER/arch/arm64/boot/Image $BINDIR
mv $SRCDIR/linux-$LINUX_VER/vmlinux               $BINDIR

# Clean up
rm -rf $SRCDIR/linux-$LINUX_VER.tar.xz
rm -rf $SRCDIR/linux-$LINUX_VER
