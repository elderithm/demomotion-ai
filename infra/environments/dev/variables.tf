variable "project_id" {
  type = string
}

variable "region" {
  type    = string
  default = "asia-northeast1"
}

variable "name" {
  type    = string
  default = "demomotion-ai"
}

variable "basic_auth_user" {
  type    = string
  default = ""
}

variable "basic_auth_pass" {
  type      = string
  default   = ""
  sensitive = true
}
