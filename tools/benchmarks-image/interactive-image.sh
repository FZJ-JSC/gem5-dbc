#!/bin/bash -ex

# This script assumes the env paths are set. See README.md
BASE_DIR=$IMGDIR/disks/
GEM5_DIR=$SRCDIR/gem5/
APPS_DIR=$SRCDIR/apps/

# Our default base ubuntu 20.04 disk image
DISKIMG=rootfs.img
# Secondary disk image with benchmarks (binaries, inputes, etc...)
BENCHIMG=benchmarks.img

# Execute this on exit or failure
teardown() {
    # final cleanup
    sudo rm -rf $BASE_DIR/tmp

    # Unmount system directories
    sudo umount $BASE_DIR/mnt/proc
    sudo umount $BASE_DIR/mnt/sys
    sudo umount $BASE_DIR/mnt/dev

    $GEM5_DIR/util/gem5img.py umount $BASE_DIR/mnt/data
    #sudo umount $BASE_DIR/mnt/data

    # Unmount system image
    sudo umount $BASE_DIR/mnt
    sudo rm -rf $BASE_DIR/mnt
}

# Install teardown function
trap "teardown" INT TERM EXIT

# Cleanup directories
sudo rm -rf $BASE_DIR/tmp

# Mount system image
mkdir -p $BASE_DIR/mnt
sudo mount -o loop,offset=65536 $BASE_DIR/${DISKIMG} $BASE_DIR/mnt

# Mount system directories
sudo mount --bind /proc $BASE_DIR/mnt/proc
sudo mount --bind /sys $BASE_DIR/mnt/sys
sudo mount --bind /dev $BASE_DIR/mnt/dev

# Mount benchmarks dir
sudo mkdir -p $BASE_DIR/mnt/data
$GEM5_DIR/util/gem5img.py mount $BASE_DIR/${BENCHIMG} $BASE_DIR/mnt/data

xterm -fa 'Monospace' -fs 16 -e "sudo chroot $IMGDIR/disks/mnt /bin/env HOME=/root /bin/bash -i"

