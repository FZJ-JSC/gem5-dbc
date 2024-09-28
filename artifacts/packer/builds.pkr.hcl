# Builds

build {
  sources = ["source.qemu.debian"]

  provisioner "file" {
    source      = "${path.root}/provision"
    destination = "/tmp"
  }

  provisioner "shell" {
    scripts = [
      "${path.root}/scripts/gem5.sh",
      "${path.root}/scripts/mini_stream.sh",
      "${path.root}/scripts/linux.sh",
    ]
  }

  provisioner "file" {
    source = "/root/binaries/"
    destination = "${path.cwd}/${var.build_dir}/${var.build_arch}/"
    direction = "download"
  }

  provisioner "shell-local" {
    scripts = [
      "${path.root}/scripts/artifacts.sh",
    ]
    environment_vars = [
      "BUILD_DIR=${path.cwd}/${var.build_dir}",
      "BUILD_ARCH=${var.build_arch}",
      "BUILD_VERSION=Debian_${var.debian_version}",
      "KERNEL_VERSION=5.15.68",
    ]
  }
}
