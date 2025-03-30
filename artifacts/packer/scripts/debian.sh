#!/bin/bash

PRVDIR=$PACKER_PROVISION_SYSTEM
KEYDIR=$PACKER_PROVISION_KEYS

# Block systemd, see https://wiki.debian.org/Init
mkdir -p /etc/apt/preferences.d
mv $PRVDIR/etc/apt/preferences.d/local-pin-init /etc/apt/preferences.d/
chmod 0644 /etc/apt/preferences.d/local-pin-init

# Network interfaces
mv $PRVDIR/etc/network/interfaces /etc/network/interfaces
chmod 0644 /etc/network/interfaces

# Setup gem5 init service
mv $PRVDIR/etc/init.d/gem5 /etc/init.d/gem5
chmod 0755 /etc/init.d/gem5
update-rc.d gem5 defaults

# disable udev
# update-rc.d  udev disable S

# generate keys
mkdir -p $KEYDIR .ssh/
ssh-keygen -t ed25519 -C "root@gem5" -f $KEYDIR/debian_gem5 -q -N ""
cat $KEYDIR/debian_gem5.pub > /root/.ssh/authorized_keys
chmod 0600 /root/.ssh/authorized_keys
chmod 0700 /root/.ssh
