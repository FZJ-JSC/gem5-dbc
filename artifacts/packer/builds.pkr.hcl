# Builds

build {
  sources = ["source.qemu.linux_image"]

  provisioner "shell" {
    inline = ["mkdir -p ${local.provision_dir}"]
  }

  provisioner "file" {
    source      = "${path.root}/provision/${var.distro_name}"
    destination = "${local.provision_dir}"
  }

  provisioner "file" {
    source      = "${dirname(path.root)}/packages"
    destination = "${local.provision_dir}"
  }

  provisioner "shell" {
    scripts = [
      "${path.root}/scripts/${var.distro_name}.sh",
      "${path.root}/scripts/packages.sh",
    ]
    environment_vars = [
      "PACKER_PROVISION_SYSTEM=${local.provision_dir}/${var.distro_name}",
      "PACKER_PROVISION_PKGDIR=${local.provision_dir}/packages",
      "PACKER_PROVISION_SRCDIR=${local.package_source_dir}",
      "PACKER_PROVISION_BLDDIR=${local.package_build_dir}",
      "PACKER_PROVISION_OUTDIR=${local.binaries_output}",
      "PACKER_PROVISION_INSTALL=${local.package_install_dir}",
      "PACKER_PROVISION_KEYS=${local.ssh_keys_output}",
      "PACKER_PACKAGE_LIST=${local.package_list}",
    ]
  }

  provisioner "file" {
    source = "${local.ssh_keys_output}/"
    destination = "${local.output_dir}/${var.artifacts_dir}/${var.image_arch}/"
    direction = "download"
  }

  provisioner "file" {
    source = "${local.binaries_output}/"
    destination = "${local.output_dir}/${var.artifacts_dir}/${var.image_arch}/"
    direction = "download"
  }

  post-processor "shell-local" {
    scripts = [
      "${path.root}/scripts/artifacts.sh",
    ]
    environment_vars = [
      "ARTIFACTS_DIR=${local.output_dir}/${var.artifacts_dir}",
      "ARTIFACTS_ARCH=${var.image_arch}",
    ]
  }

}
