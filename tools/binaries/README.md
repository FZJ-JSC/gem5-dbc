## Binaries for full-system simulation

gem5 requires a linux kernel image, a disk image and a bootloader. 

Disk images should be copied to `$IMGDIR/disks/`, and kernel and bootloaders to `$IMGDIR/binaries/`.

The following sections contain the instructions to generate your own set.

### Create Linux image

You may use an existing gem5 linux kernel repo to compile kernel v4.15 following the instructions [here](https://www.gem5.org/documentation/general_docs/fullsystem/building_arm_kernel). If you want a newer kernel there are config files for `v4.19.16`, `v5.2.3` and `v5.4.65` in the `tools/binaries/kernel/` folders.

Instructions for `v5.4.65`.

```bash
cd $SRCDIR
# Clone the linux kernel repo
git clone git://git.kernel.org/pub/scm/linux/kernel/git/stable/linux-stable.git
# Checkout the branch
cd $SRCDIR/linux-stable
git checkout v5.4.65
# Copy the defconfig
cp $SRCDIR/epi-gem5/tools/binaries/kernel/gem5-linux5/arm64/linux-5.4.65.config $SRCDIR/linux-stable/arch/arm64/configs/linux-5.4.65.config
cp $SRCDIR/epi-gem5/tools/binaries/kernel/gem5-linux5/arm64/linux-5.4.65.config $SRCDIR/linux-stable/.config
# Setup the configuration file
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- linux-5.4.65.config
# Optional: If you need to tweak your build, use menuconfig
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- menuconfig
# Build the kernel - grab a coffee
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j 4
# Move vmlinux image
cp vmlinux $IMGDIR/binaries/vmlinux-5.4.65.aarch64
# The infrastructure expect the linux image to be called vmlinux
cd $IMGDIR/binaries/
ln -s vmlinux-5.4.65.aarch64 vmlinux
```

### Create disk image

You may create a new base disk image if you need to add additional software to it. The setup is based on Docker containers.

```bash
cd $SRCDIR/epi-gem5/tools/binaries/disk-image
# Copy the (cross-)compiled 'm5' utility
cp $SRCDIR/gem5/util/m5/build/arm64/out/m5 m5.aarch64
# Download the 'qemu-aarch64-static' binary
wget https://github.com/multiarch/qemu-user-static/releases/download/v6.1.0-8/qemu-aarch64-static
chmod 755 qemu-aarch64-static
# Check and edit the Dockerfile to ensure all the necessary software and installation steps are included.
vi Dockerfile
# If you're using Docker 23.0, disable BuildKit
export DOCKER_BUILDKIT=0 
# Create an Ubuntu 22.04 base image
docker build -t gem5-ubuntu22.04 .
# Check if the image is there
docker images
# Start a new container using the image, check if everything is okay. This will drop you into an interactive shell. 'exit' to finish the session.
docker run --name gem5-img-container -i -t gem5-ubuntu22.04
# Export the container into a tar file
docker export gem5-img-container > ubuntu22.04.img.tar
# Convert the tar file into a disk image
guestfish --rw -N "gem5-ubuntu22.04-aarch64.img=fs:ext4:2GB" -m /dev/sda1:/ tar-in - / < ubuntu22.04.img.tar
# Move the disk image
mv gem5-ubuntu22.04-aarch64.img $IMGDIR/disks/
# The infrastructure expects the disk image to be called rootfs.img
cd $IMGDIR/disks/
ln -s gem5-ubuntu22.04-aarch64.img rootfs.img
```

### Build the bootloaders

Simply compile the provided bootloader from gem5.

```bash
cd $SRCDIR/gem5/system/arm/bootloader/arm64
make
mv boot_v2.arm64 $IMGDIR/binaries/
```

Note that `boot_v2.arm64` is for simulations using the `VExpress_GEM5_V2` system, which may be the default nowadays. If you use `VExpress_GEM5_V1` use the generated `boot.arm64` bootloader.


### Prepare disk image to run benchmarks
To compile the mess benchmark, copy it into the $SRCDIR/apps directory 

```bash
cd $SRCDIR/epi-gem5/tools/benchmarks-image/
## Modify the script to compile the Mess benchmark 
./benchmarks-image.sh
```

The new benchmark image is located in `$IMGDIR/disks`. An interactive session that mounts the main ubuntu disk image and the benchmarks image under `/data` can be opened.

```bash
cd $SRCDIR/epi-gem5/tools/benchmarks-image/
./interactive-image.sh
```

This will open a new terminal with the `chroot` environment of the ubuntu disk image. You may now check the contents of `benchmarks.img` that is mounted under `/data`, and even run your benchmarks!
