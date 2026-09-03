variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "GoodStock project name"
  type        = string
  default     = "devops-ecommerce"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

variable "root_volume_size_gb" {
  description = "Root EBS volume size in GB"
  type        = number
  default     = 30
}

variable "ssh_public_key_path" {
  description = "Path to the local SSH public key file"
  type        = string
  default     = "~/.ssh/devops-ecommerce-key.pub"
}

variable "my_ip_cidr" {
  description = "Your IP address in CIDR form allowed to SSH"
  type        = string
}

variable "service_nodes" {
  description = "Additional EC2 nodes for application services"

  type = map(object({
    role = string
  }))

  default = {
    frontend = {
      role = "frontend"
    }

    product = {
      role = "product"
    }

    order = {
      role = "order"
    }

    user = {
      role = "user"
    }
  }
}