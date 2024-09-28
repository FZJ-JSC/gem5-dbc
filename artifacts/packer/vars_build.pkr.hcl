# Build variables

variable "build_arch" {
  type    = string
  default = "arm64"
}

variable "build_dir" {
  type    = string
  default = "artifacts"
}

variable "image_hostname" {
  type    = string
  default = "gem5"
}

variable "image_size" {
  type    = number
  default = 6500
}
