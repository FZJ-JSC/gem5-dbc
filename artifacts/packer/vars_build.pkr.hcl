# Build variables

variable "artifacts_dir" {
  type    = string
  default = "artifacts"
}

variable "image_arch" {
  type    = string
  default = "arm64"
}

variable "image_hostname" {
  type    = string
  default = "gem5"
}

variable "image_size" {
  type    = number
  default = 10000
}

variable "packages" {
  type    = list(string)
  default = [
    "gem5",
    "mini_stream",
    "linux",
  ]
}

locals {
  artifacts_dir = abspath(var.artifacts_dir)
  package_list = join(" ", var.packages)  
  package_source_dir="/root/sources"
  package_build_dir="/root/build"
  binaries_output="/root/binaries"
  ssh_keys_output="/root/keys"
  provision_dir="/tmp/provision"
  package_install_dir="/benchmarks"
}
