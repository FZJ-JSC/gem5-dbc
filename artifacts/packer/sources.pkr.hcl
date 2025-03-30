# Sources

packer {
  required_plugins {
    qemu = {
      source  = "github.com/hashicorp/qemu"
      version = "~> 1"
    }
  }
}

source "qemu" "linux_image" {
  vm_name = "disk.img-${var.distro_name}-${local.distro_ver}"
  format  = "raw"

  output_directory = "${local.output_dir}/${var.artifacts_dir}/${var.image_arch}/disks"

  disk_size    = var.image_size
  machine_type = local.qemu_machine
  cpu_model    = local.qemu_cpu_model
  cpus         = var.qemu_ncpus
  memory       = var.qemu_memory
  headless     = var.qemu_headless
  accelerator  = var.qemu_accelerator
  qemu_binary  = local.qemu_binary
  qemuargs     = local.qemu_args

  http_directory    = "${path.root}/provision/${var.distro_name}"
  boot_key_interval = "20ms"
  boot_wait         = "10s"

  boot_command = local.distro_boot_command
  iso_url      = local.distro_iso
  iso_checksum = local.distro_sum

  ssh_username = "root"
  ssh_password = "root"
  ssh_timeout  = "600m"
  shutdown_command = "/sbin/poweroff"  
}
