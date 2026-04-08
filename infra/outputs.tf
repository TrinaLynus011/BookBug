output "instance_public_ip" {
  description = "Public IP of the BookBug application host"
  value       = aws_instance.app_host.public_ip
}

output "instance_public_dns" {
  description = "Public DNS of the BookBug application host"
  value       = aws_instance.app_host.public_dns
}

output "backend_url" {
  description = "BookBug backend API URL"
  value       = "http://${aws_instance.app_host.public_ip}:8000"
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}
