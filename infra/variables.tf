variable "aws_region" {
  type        = string
  description = "AWS region to deploy resources"
  default     = "us-east-1"
}

variable "project_name" {
  type        = string
  description = "Project tag applied to all resources"
  default     = "bookbug"
}

variable "instance_type" {
  type        = string
  description = "EC2 instance type for the application host"
  default     = "t3.micro"
}

variable "dockerhub_username" {
  type        = string
  description = "Docker Hub username used to pull the BookBug image"
}

variable "secret_key" {
  type        = string
  description = "JWT secret key injected into the container"
  sensitive   = true
}
