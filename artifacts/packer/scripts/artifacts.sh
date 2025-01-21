#!/bin/bash

function md5_hash_file {
    (md5sum $1 2> /dev/null || echo 0 ) | awk '{ print $1 }'
}

ARTIFACTS_FILE=$BUILD_DIR.yaml
ARTIFACTS_BASE=$(basename $BUILD_DIR)

DISK_NAME=${PACKER_BUILD_NAME}.img
DISK_PATH=$BUILD_ARCH/disks/$DISK_NAME
DISK_HASH=$(md5_hash_file $BUILD_DIR/$DISK_PATH)
DISK_VER="Debian ${BUILD_VERSION}"

BOOT1_NAME="boot.arm64"
BOOT1_PATH=$BUILD_ARCH/binaries/$BOOT1_NAME
BOOT1_HASH=$(md5_hash_file $BUILD_DIR/$BOOT1_PATH)
BOOT1_VER="V1"

BOOT2_NAME="boot_v2.arm64"
BOOT2_PATH=$BUILD_ARCH/binaries/$BOOT2_NAME
BOOT2_HASH=$(md5_hash_file $BUILD_DIR/$BOOT2_PATH)
BOOT2_VER="V2"

KERNEL_NAME="vmlinux"
KERNEL_PATH=$BUILD_ARCH/binaries/$KERNEL_NAME
KERNEL_HASH=$(md5_hash_file $BUILD_DIR/$KERNEL_PATH)
KERNEL_VER=${KERNEL_VERSION}

cat >$ARTIFACTS_FILE <<EOL
$BUILD_ARCH:
- bintype: "DISK"
  name:    $DISK_NAME
  path:    $ARTIFACTS_BASE/$DISK_PATH
  md5hash: $DISK_HASH
  version: $DISK_VER
  metadata: /dev/vda2
- bintype: "KERNEL"
  name:    $KERNEL_NAME
  path:    $ARTIFACTS_BASE/$KERNEL_PATH
  md5hash: $KERNEL_HASH
  version: "$KERNEL_VER"
  metadata: earlyprintk=pl011,0x1c090000 console=ttyAMA0 lpj=19988480 norandmaps rw loglevel=8
- bintype: "BOOT"
  name:    $BOOT1_NAME
  path:    $ARTIFACTS_BASE/$BOOT1_PATH
  md5hash: $BOOT1_HASH
  version: $BOOT1_VER
  metadata: VExpress_GEM5_$BOOT1_VER
- bintype: "BOOT"
  name:    $BOOT2_NAME
  path:    $ARTIFACTS_BASE/$BOOT2_PATH
  md5hash: $BOOT2_HASH
  version: $BOOT2_VER
  metadata: VExpress_GEM5_$BOOT2_VER
EOL
