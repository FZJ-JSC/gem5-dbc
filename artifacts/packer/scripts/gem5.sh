#!/bin/bash

PRVDIR=/tmp/provision/gem5

SRCDIR=/root/sources
BINDIR=/root/binaries

GEM5_VER="v24.0.0.1"
GEM5_GIT="https://github.com/gem5/gem5.git"

mkdir -p $SRCDIR $BINDIR

# Setup gem5 init service
mv $PRVDIR/gem5_service /etc/init.d/gem5
chmod 0755 /etc/init.d/gem5
update-rc.d gem5 defaults

# Install gem5 m5 util and compile bootloaders
## Clone gem5 repo
git -C $SRCDIR clone --depth 1 --branch $GEM5_VER $GEM5_GIT
## Apply patch
git -C $SRCDIR/gem5 apply $PRVDIR/gem5-0010-libm5.patch
## Compile bootloader
make -C $SRCDIR/gem5/system/arm/bootloader/arm64 -f makefile -j$(nproc)
## Compile m5 utility
make GEM5_DIST=$SRCDIR/gem5 -C $SRCDIR/gem5/util/m5/src -f Makefile -j$(nproc)
## Install binaries
install -D -m 0755 $SRCDIR/gem5/util/m5/src/m5       /sbin/m5
install -D -m 0755 $SRCDIR/gem5/util/m5/src/libm5.a  /usr/lib/libm5.a
## Install headers
install -D -m 0644 $SRCDIR/gem5/include/gem5/m5ops.h             /usr/include/gem5/m5ops.h
install -D -m 0644 $SRCDIR/gem5/include/gem5/asm/generic/m5ops.h /usr/include/gem5/asm/generic/m5ops.h

# Move compiled binaries to $BINDIR for download
mv $SRCDIR/gem5/system/arm/bootloader/arm64/boot.arm64 $BINDIR
mv $SRCDIR/gem5/system/arm/bootloader/arm64/boot_v2.arm64 $BINDIR

# Clean up
rm -rf $SRCDIR/gem5
