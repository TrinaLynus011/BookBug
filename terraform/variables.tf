variable "kubeconfig_path" {
  type        = string
  description = "Absolute path to kubeconfig file"
  default     = "~/.kube/config"
}

variable "namespace" {
  type        = string
  description = "Namespace for BookBee resources"
  default     = "bookbee"
}

variable "dockerhub_username" {
  type        = string
  description = "Docker Hub username prefix for image pull"
}
