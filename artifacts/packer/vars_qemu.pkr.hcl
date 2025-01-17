# QEMU variables

variable "qemu_ncpus" {
  type    = number
  default = 8
}

variable "qemu_memory" {
  type    = number
  default = 16384
}

variable "qemu_accelerator" {
  type    = string
  default = "none"
}

variable "qemu_headless" {
  type    = bool
  default = true
}

variable "qemu_efi_arm64" {
  type    = string
  default = "/usr/share/AAVMF/AAVMF_CODE.fd"
}

variable "qemu_cpu_arm64" {
  type    = string
  default = "neoverse-v1"
}

variable "qemu_cpu_x86_64" {
  type    = string
  default = "qemu64"
}

locals {
  qemu_archs = {
    "arm64"   = "aarch64"
    "x86_64"  = "x86_64"
  }
  qemu_machines = {
    "arm64"   = "virt"
    "x86_64"  = "q35"
  }
  qemu_cpus = {
    "arm64"   = "${var.qemu_cpu_arm64}"
    "x86_64"  = "${var.qemu_cpu_x86_64}"
  }
  qemu_arch      = lookup(local.qemu_archs,    var.build_arch, "aarch64")
  qemu_machine   = lookup(local.qemu_machines, var.build_arch, "virt")
  qemu_cpu_model = lookup(local.qemu_cpus,     var.build_arch, "max")
  qemu_binary    = "qemu-system-${local.qemu_arch}"
  qemu_args      = var.build_arch == "arm64" ?  [
    ["-device", "virtio-gpu-pci"],
    ["-device", "qemu-xhci"],
    ["-device", "usb-kbd"],
    ["-boot",   "order=dc"],
    ["-bios",   "${var.qemu_efi_arm64}"]
  ] : null
}
