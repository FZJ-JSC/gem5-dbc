# Sources

packer {
  required_plugins {
    qemu = {
      source  = "github.com/hashicorp/qemu"
      version = "~> 1"
    }
  }
}

source "qemu" "debian" {
  vm_name          = "debian.img"
  output_directory = "${path.cwd}/${var.build_dir}/${var.build_arch}/disks"

  machine_type = local.qemu_machine
  cpu_model    = local.qemu_cpu_model
  cpus         = var.qemu_ncpus
  memory       = var.qemu_memory
  disk_size    = var.image_size
  headless     = var.qemu_headless
  accelerator  = var.qemu_accelerator
  format       = "raw"

  boot_command  = [
        "<wait>c<wait>",
        "linux /${local.debian_boot}/vmlinuz",
        " auto=true",
        " url=http://{{ .HTTPIP }}:{{ .HTTPPort }}/preseed.cfg",
        " hostname=${var.image_hostname}",
        " domain=local",
        " --- quiet",
        "<enter><wait>",
        "initrd /${local.debian_boot}/initrd.gz",
        "<enter><wait>",
        "boot<enter><wait>"
      ]
  http_directory    = "${path.root}/config/debian"
  boot_key_interval = "20ms"
  boot_wait         = "10s"

  iso_url      = local.debian_iso
  iso_checksum = local.debian_sum

  qemu_binary = local.qemu_binary
  qemuargs    = local.qemu_args

  ssh_username = "root"
  ssh_password = "root"
  ssh_timeout  = "150m"
  shutdown_command = "/sbin/poweroff"  
}
