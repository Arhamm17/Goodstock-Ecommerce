output "instance_public_ip" {
  description = "Elastic IP address of the API/K3s server node"
  value       = aws_eip.app_server_eip.public_ip
}

output "instance_public_dns" {
  description = "Public DNS name of the API/K3s server node"
  value       = aws_instance.app_server.public_dns
}

output "instance_id" {
  description = "EC2 instance ID of the API/K3s server node"
  value       = aws_instance.app_server.id
}

output "ssh_command" {
  description = "SSH command for the API/K3s server node"
  value       = "ssh -i ${var.ssh_public_key_path == "~/.ssh/devops-ecommerce-key.pub" ? "~/.ssh/devops-ecommerce-key" : "<your-private-key>"} ubuntu@${aws_eip.app_server_eip.public_ip}"
}

output "api_node" {
  description = "Existing API Gateway and K3s server node"

  value = {
    instance_id = aws_instance.app_server.id
    private_ip  = aws_instance.app_server.private_ip
    public_ip   = aws_eip.app_server_eip.public_ip
    subnet_id   = aws_instance.app_server.subnet_id
  }
}

output "service_nodes" {
  description = "Frontend, Product, Order and User EC2 nodes"

  value = {
    for name, instance in aws_instance.service_nodes :
    name => {
      instance_id = instance.id
      private_ip  = instance.private_ip
      public_ip   = instance.public_ip
      subnet_id   = instance.subnet_id
    }
  }
}

output "all_private_ips" {
  description = "Private IP addresses of all five application nodes"

  value = merge(
    {
      api = aws_instance.app_server.private_ip
    },
    {
      for name, instance in aws_instance.service_nodes :
      name => instance.private_ip
    }
  )
}