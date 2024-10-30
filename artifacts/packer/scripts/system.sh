#!/bin/bash

PRVDIR=/tmp/provision

# Network interfaces
mv $PRVDIR/etc/network/interfaces /etc/network/interfaces
chmod 0644 /etc/network/interfaces

# disable udev
# update-rc.d  udev disable S
