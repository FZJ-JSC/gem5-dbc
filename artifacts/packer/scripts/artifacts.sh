#!/bin/bash

function md5_hash_file {
    (md5sum $1 2> /dev/null || echo 0 ) | awk '{ print $1 }'
}

ARTIFACTS_PATH=$(dirname $ARTIFACTS_DIR)/$(basename $ARTIFACTS_DIR)
INDEX_FILE="$ARTIFACTS_PATH/index.yaml"

echo -en "$ARTIFACTS_ARCH:\n" > $INDEX_FILE

SUFFIX=disks
for o in $ARTIFACTS_PATH/$ARTIFACTS_ARCH/$SUFFIX/*.img* ; do
    f=$(basename $o)
    NAME=${f%%-*}
    VER=${f#*-}
    FPATH=$ARTIFACTS_ARCH/$SUFFIX/$f
    BINTYPE="DISK"
    META="/dev/vda2"
    HASH=$(md5_hash_file $ARTIFACTS_PATH/$FPATH)
    echo -en "- bintype: \"$BINTYPE\"\n  name: $NAME\n  path: $FPATH\n  md5hash: $HASH\n  version: $VER\n  metadata: $META\n" >> $INDEX_FILE
done

SUFFIX=binaries
for o in $ARTIFACTS_PATH/$ARTIFACTS_ARCH/$SUFFIX/* ; do
    f=$(basename $o)
    NAME=${f%%-*}
    VER=${f#*-}
    FPATH=$ARTIFACTS_ARCH/$SUFFIX/$f
    BINTYPE=""
    META=""
    HASH=$(md5_hash_file $ARTIFACTS_PATH/$FPATH)
    case $NAME in
        vmlinux)
        BINTYPE="KERNEL"
        META="earlyprintk=pl011,0x1c090000 console=ttyAMA0 lpj=19988480 norandmaps rw loglevel=8"
        ;;
        Image)
        BINTYPE="KERNEL"
        META="qemu"
        ;;
        boot.arm64)
        BINTYPE="BOOT"
        META=$VER
        ;;
        *)
        ;;
    esac
    echo -en "- bintype: \"$BINTYPE\"\n  name: $NAME\n  path: $FPATH\n  md5hash: $HASH\n  version: $VER\n  metadata: $META\n" >> $INDEX_FILE
done

echo -en "\n" >> $INDEX_FILE
