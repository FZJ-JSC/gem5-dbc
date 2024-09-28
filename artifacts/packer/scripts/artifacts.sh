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

BOOT_NAME="boot_v2.arm64"
BOOT_PATH=$BUILD_ARCH/binaries/$BOOT_NAME
BOOT_HASH=$(md5_hash_file $BUILD_DIR/$BOOT_PATH)
BOOT_VER="v2"

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
  name:    $BOOT_NAME
  path:    $ARTIFACTS_BASE/$BOOT_PATH
  md5hash: $BOOT_HASH
  version: $BOOT_VER
  metadata: VExpress_GEM5_V2
EOL
