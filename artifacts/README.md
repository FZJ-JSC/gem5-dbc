# Artifact generation

This directory contains a set of [Packer](https://developer.hashicorp.com/packer)
templates for automatic generation of binary artifacts needed to run
full system (FS) gem5 simulations.

Currently, artifact generation is supported only for the ARM64 architecture.


## Artifact generation for ARM64 architecture

### Create gem5 binary
```bash
# Clone gem5 repository
git clone https://github.com/gem5/gem5.git

# Compile gem5 binary
scons -C gem5 --ignore-style -j 8 gem5/build/ARM/gem5.fast

# Add gem5 binary to local artifact index
g5dbc --resource-add GEM5 gem5/build/ARM/gem5.fast
```

### Create Linux image binaries using Packer

```bash
# Directory where images will be generated
export G5DBC_IMAGES=$HOME/images

# Init packer plugins
packer init gem5-dbc/artifacts/packer

# Generate binary images
packer build -var output_dir=$G5DBC_IMAGES gem5-dbc/artifacts/packer
```

If you want to debug the image build, you should run

```bash
# Generate binary images
packer build -on-error=ask -var qemu_headless=false -var output_dir=$G5DBC_IMAGES gem5-dbc/artifacts/packer
```

You can specify the correct path for the Arm Virtual Machine Firmware EFI:

```bash
# Create packer build 
packer build -var output_dir=$G5DBC_IMAGES -var qemu_efi_aarch64=/usr/share/AAVMF/AAVMF_CODE.fd gem5-dbc/artifacts/packer
```

After the build is finished, the directory `$G5DBC_IMAGES`
will contain the generated binary artifacts.

| File | Description |
| ---- | ----------- |
| $G5DBC_IMAGES/artifacts/index.yaml     | Index of binary artifacts for use with `g5dbc`  |
| $G5DBC_IMAGES/artifacts/arm64/disks    | Disk Images   |
| $G5DBC_IMAGES/artifacts/arm64/keys     | SSH Keys for generated image   |
| $G5DBC_IMAGES/artifacts/arm64/binaries | ARM64 bootloaders and Linux kernels |

The directory `$G5DBC_IMAGES` can be referenced when generating simulation scripts with `g5dbc`,

```bash
# Generate simulation scripts, include artifacts in $G5DBC_IMAGES
g5dbc --generate stream example/garnet-DDR4 --artifacts-dir $G5DBC_IMAGES/artifacts
```
