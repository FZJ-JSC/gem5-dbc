# Artifact generation

This directory contains a set of [Packer](https://developer.hashicorp.com/packer)
templates for automatic generation of binary artifacts needed to run
full system (FS) gem5 simulations.

Currently, artifact generation is supported only for the ARM64 architecture.

```bash
# Set the correct paths for your system
export G5DBC_SOURCE=$HOME/sources/gem5-dbc
export G5DBC_IMAGES=$G5DBC_PREFIX/share/g5dbc
```

## Artifact generation for ARM64 architecture

### Create binary artifacts using Packer

```bash
# Directory where artifacts will be generated
cd $G5DBC_IMAGES

# Init packer plugins
packer init $G5DBC_SOURCE/artifacts/packer

# Create packer build
packer build $G5DBC_SOURCE/artifacts/packer

# You can set the correct path for the Arm Virtual Machine Firmware EFI
packer build -var="qemu_efi_aarch64=/usr/share/AAVMF/AAVMF_CODE.fd" $G5DBC_SOURCE/artifacts/packer
```

After the build is finished, the directory `$G5DBC_IMAGES/artifacts`
and the file `$G5DBC_IMAGES/artifacts.yaml`
can be copied to `$G5DBC_PREFIX/share/g5dbc`.
```bash
# Copy generated artifacts to $G5DBC_PREFIX
cp -rv $G5DBC_IMAGES/artifacts* $G5DBC_PREFIX/share/g5dbc/
```

The directory `$G5DBC_IMAGES` will contain

| File | Description |
| ---- | ----------- |
| $G5DBC_IMAGES/artifacts/arm64/disks    | Disk Images   |
| $G5DBC_IMAGES/artifacts/arm64/binaries | ARM64 bootloaders and Linux kernels |
