# Artifact generation with Packer

This directory contains a set of [Packer](https://developer.hashicorp.com/packer)
templates for automatic generation of binary artifacts needed to run
full system (FS) gem5 simulations.

Currently, artifact generation is supported only for the ARM64 architecture.

The [QEMU](https://developer.hashicorp.com/packer/integrations/hashicorp/qemu/latest/components/builder/qemu)
Packer builder is used to boot a virtual machine and install Debian Linux.
The installed Debian Linux image is the rebooted, and the image is configured
for use with gem5 full system simulation.

In particular, following files are [generated](../packages/gem5/install.sh) and installed in the image:

| File | Description |
| --- | --- |
| /sbin/m5 | [m5 utility](https://www.gem5.org/documentation/general_docs/m5ops/) |
| /usr/lib/libm5.a |  [M5ops static library](https://www.gem5.org/documentation/general_docs/m5ops/) |
| [/etc/init.d/gem5](provision/debian//etc/init.d/gem5) | [sysvinit](https://wiki.debian.org/Init) script to execute scripts from the host system |

## Artifact generation for ARM64 architecture

### Compile gem5 binary
```bash
# Clone gem5 repository
git clone https://github.com/gem5/gem5.git

# Compile gem5 binary
scons -C gem5 --ignore-style -j $(nproc) gem5/build/ARM/gem5.fast

# Add gem5 binary to local artifact index
g5dbc --resource-add gem5/build/ARM/gem5.fast --resource-type GEM5

```

### Create Linux image binaries using Packer

```bash
# Directory where binary artifacts will be generated
export ARTIFACTS=$HOME/artifacts

# Init packer plugins
packer init gem5-dbc/artifacts/packer

# Generate binary images
packer build -var artifacts_dir=$ARTIFACTS gem5-dbc/artifacts/packer
```

If you want to debug the image build, you should run

```bash
# Generate binary images
packer build -on-error=ask -var qemu_headless=false -var artifacts_dir=$ARTIFACTS gem5-dbc/artifacts/packer
```

You can specify the correct path for the Arm Virtual Machine Firmware EFI:

```bash
# Create packer build 
packer build -var artifacts_dir=$ARTIFACTS -var qemu_efi_aarch64=/usr/share/AAVMF/AAVMF_CODE.fd gem5-dbc/artifacts/packer
```

After the build is finished, the directory `$ARTIFACTS`
will contain the generated binary artifacts.

| File | Description |
| ---- | ----------- |
| $ARTIFACTS/index.yaml     | Index of binary artifacts for use with `g5dbc`  |
| $ARTIFACTS/arm64/disks    | Disk Images   |
| $ARTIFACTS/arm64/keys     | SSH Keys for generated image   |
| $ARTIFACTS/arm64/binaries | ARM64 bootloaders and Linux kernels |

The directory `$ARTIFACTS` can be referenced when generating simulation scripts with `g5dbc`,

```bash
# Generate simulation scripts, include artifacts in $G5DBC_IMAGES
g5dbc --generate stream/mini_triad --init-config garnet --artifacts-dir $ARTIFACTS --nprocs 4
```
