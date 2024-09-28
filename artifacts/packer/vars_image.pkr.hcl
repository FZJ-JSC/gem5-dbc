# Debian variables

variable "debian_mirror" {
  type    = string
  default = "http://debian.netcologne.de"
}

variable "debian_version" {
  type    = string
  default = "12.7.0"
}

variable "debian_install_medium" {
  type    = list(string)
  default = ["iso-cd", "netinst"]
}

locals {
  debian_archs = {
    "arm64"   = "arm64"
    "x86_64"  = "amd64"
  }
  debian_boot_install = {
    "arm64"   = "install.a64"
    "x86_64"  = "install"
  }
  debian_arch = lookup(local.debian_archs,  var.build_arch, "arm64")
  debian_boot = lookup(local.debian_boot_install, var.build_arch, "install.a64")
  debian_url  = "${var.debian_mirror}/debian-cd/${var.debian_version}/${local.debian_arch}/${var.debian_install_medium[0]}"
  debian_iso  = "${local.debian_url}/debian-${var.debian_version}-${local.debian_arch}-${var.debian_install_medium[1]}.iso"
  debian_sum  = "file:${local.debian_url}/SHA512SUMS"
}
