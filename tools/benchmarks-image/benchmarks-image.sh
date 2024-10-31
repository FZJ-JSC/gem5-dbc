#!/bin/bash -ex

# This script assumes the env paths are set. See README.md
BASE_DIR=$IMGDIR/disks/
GEM5_DIR=$SRCDIR/gem5/
APPS_DIR=$SRCDIR/epi-apps/

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

    sudo umount $BASE_DIR/mnt/apps

    # Unmount system image
    sudo umount $BASE_DIR/mnt
    sudo rm -rf $BASE_DIR/mnt

    # Unmount benchmarks image
    $GEM5_DIR/util/gem5img.py umount $BASE_DIR/mnt2
    sudo rm -rf $BASE_DIR/mnt2

    sudo rm -rf $BASE_DIR/benchmarks
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

# Mount apps directory
sudo mkdir -p $BASE_DIR/mnt/apps/
sudo mount --bind $APPS_DIR/ $BASE_DIR/mnt/apps

# chroot into the image and compile
sudo chroot $BASE_DIR/mnt /bin/bash -x -i <<'EOF'
cd /apps/
## COMPILE THE MESS BENCHMARK
ls -la bin
EOF

# Prepare benchmark files
mkdir -p $BASE_DIR/benchmarks
sudo cp -a $APPS_DIR/lib $BASE_DIR/benchmarks/
sudo cp -a $APPS_DIR/include $BASE_DIR/benchmarks/
sudo cp -a $APPS_DIR/bin $BASE_DIR/benchmarks/
sudo cp -a $APPS_DIR/inputs $BASE_DIR/benchmarks/

# Generate benchmarks image
mkdir -p $BASE_DIR/mnt2
$GEM5_DIR/util/gem5img.py init $BASE_DIR/${BENCHIMG} 512 # empty image 2G
$GEM5_DIR/util/gem5img.py mount $BASE_DIR/${BENCHIMG} $BASE_DIR/mnt2
sudo cp -a $BASE_DIR/benchmarks/* $BASE_DIR/mnt2
echo "Benchmarks image successfully created: $BASE_DIR/$BENCHIMG"
