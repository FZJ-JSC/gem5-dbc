# Debian variables

variable "debian_mirror" {
  type    = string
  default = "https://cdimage.debian.org/cdimage"
}

variable "debian_version" {
  type = string
  default = "testing"
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
  debian_versions = {
    "stable"  = "12.7.0"
    "testing" = "testing"
  }
  debian_url_prefixes = {
    "stable"  = "release/current"
    "testing" = "weekly-builds"
  }

  debian_arch = lookup(local.debian_archs,        var.build_arch,     "arm64")
  debian_boot = lookup(local.debian_boot_install, var.build_arch,     "install.a64")
  debian_ver  = lookup(local.debian_versions,     var.debian_version, "testing")
  url_prefix  = lookup(local.debian_url_prefixes, var.debian_version, "weekly-builds")

  debian_url  = "${var.debian_mirror}/${local.url_prefix}/${local.debian_arch}/iso-cd" 
  debian_iso  = "${local.debian_url}/debian-${local.debian_ver}-${local.debian_arch}-netinst.iso"
  debian_sum  = "file:${local.debian_url}/SHA512SUMS"
}
