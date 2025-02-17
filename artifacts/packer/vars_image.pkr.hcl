# Distro variables

variable "distro_name" {
  type    = string
  default = "debian"
}

variable "distro_version" {
  type = string
  default = "stable"
}

variable "debian_mirror" {
  type    = string
  default = "https://cdimage.debian.org/cdimage"
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
    "stable"  = "12.9.0"
    "testing" = "testing"
  }
  debian_url_prefixes = {
    "stable"  = "release/current"
    "testing" = "weekly-builds"
  }

  debian_media = "iso-cd"
  debian_image = "netinst"

  debian_arch = lookup(local.debian_archs,        var.image_arch,     "arm64")
  debian_boot = lookup(local.debian_boot_install, var.image_arch,     "install.a64")
  debian_ver  = lookup(local.debian_versions,     var.distro_version, "testing")
  url_prefix  = lookup(local.debian_url_prefixes, var.distro_version, "weekly-builds")

  debian_url  = "${var.debian_mirror}/${local.url_prefix}/${local.debian_arch}/${local.debian_media}" 
  debian_iso  = "${local.debian_url}/debian-${local.debian_ver}-${local.debian_arch}-${local.debian_image}.iso"
  debian_sum  = "file:${local.debian_url}/SHA512SUMS"

  distro_ver = local.debian_ver
  distro_iso = local.debian_iso
  distro_sum = local.debian_sum

  distro_boot_command  = [
        "<wait>c<wait>",
        "linux /${local.debian_boot}/vmlinuz",
        " auto=true",
        " url=http://{{ .HTTPIP }}:{{ .HTTPPort }}/preseed/${var.distro_version}.cfg",
        " hostname=${var.image_hostname}",
        " domain=local",
        " --- quiet",
        "<enter><wait>",
        "initrd /${local.debian_boot}/initrd.gz",
        "<enter><wait>",
        "boot<enter><wait>"
      ]
}
