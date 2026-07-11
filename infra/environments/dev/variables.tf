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

# GitHub repo (owner/name) allowed to federate into this project's CI via
# Workload Identity Federation. Only this repo's Actions can mint credentials.
variable "github_repository" {
  type    = string
  default = "elderithm/demomotion-ai"
}
