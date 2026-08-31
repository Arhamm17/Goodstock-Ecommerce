output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.app_server.public_ip
}

output "instance_public_dns" {
  description = "Public DNS name of the EC2 instance"
  value       = aws_instance.app_server.public_dns
}

output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.app_server.id
}

output "ssh_command" {
  description = "Ready-to-use SSH command"
  value       = "ssh -i ${var.ssh_public_key_path == "~/.ssh/devops-ecommerce-key.pub" ? "~/.ssh/devops-ecommerce-key" : "<your-private-key>"} ubuntu@${aws_instance.app_server.public_ip}"
}