data "aws_ami" "ubuntu_2404" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_key_pair" "deployer" {
  key_name   = "${var.project_name}-key"
  public_key = file(var.ssh_public_key_path)
}

resource "aws_eip" "app_server_eip" {
  domain = "vpc"

  tags = {
    Name = "devops_ecommerce"
  }
}

resource "aws_eip" "service_eips" {
  for_each = var.service_nodes

  domain = "vpc"

  tags = {
    Name = "${var.project_name}-${each.key}-eip"
  }
}

resource "aws_security_group" "k3s_cluster" {
  name        = "${var.project_name}-k3s-cluster-sg"
  description = "K3s node-to-node communication"

  ingress {
    description = "Allow all K3s node communication"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    self        = true
  }

  egress {
    description = "Allow outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-k3s-cluster-sg"
  }
}


resource "aws_security_group" "public_access" {
  name        = "${var.project_name}-public-sg"
  description = "Public access for frontend and API"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.my_ip_cidr]
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Application NodePort"
    from_port   = 30080
    to_port     = 30080
    protocol    = "tcp"
    cidr_blocks = [var.my_ip_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-public-sg"
  }
}


resource "aws_security_group" "private_services" {
  name        = "${var.project_name}-private-services-sg"
  description = "Private application service communication"

  ingress {
    description = "Internal VPC traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["172.31.0.0/16"]
  }

  egress {
    description = "Allow outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-private-services-sg"
  }
}

resource "aws_instance" "app_server" {
  ami           = data.aws_ami.ubuntu_2404.id
  instance_type = var.instance_type
  key_name      = aws_key_pair.deployer.key_name
  vpc_security_group_ids = [
    aws_security_group.public_access.id,
    aws_security_group.k3s_cluster.id
  ]

  root_block_device {
    volume_size           = var.root_volume_size_gb
    volume_type           = "gp3"
    delete_on_termination = true
  }

  tags = {
    Name     = "${var.project_name}-api-node"
    Workload = "api"
    K3sRole  = "server"
  }
}

resource "aws_instance" "service_nodes" {
  for_each = var.service_nodes

  ami           = data.aws_ami.ubuntu_2404.id
  instance_type = var.instance_type
  key_name      = aws_key_pair.deployer.key_name
  vpc_security_group_ids = each.key == "frontend" ? [
    aws_security_group.public_access.id,
    aws_security_group.k3s_cluster.id
    ] : [
    aws_security_group.private_services.id,
    aws_security_group.k3s_cluster.id
  ]

  subnet_id = aws_instance.app_server.subnet_id

  root_block_device {
    volume_size           = var.root_volume_size_gb
    volume_type           = "gp3"
    delete_on_termination = true
  }

  tags = {
    Name     = "${var.project_name}-${each.key}-node"
    Workload = each.key
    K3sRole  = "agent"
  }
}

resource "aws_eip_association" "service_eip_associations" {
  for_each = var.service_nodes

  instance_id   = aws_instance.service_nodes[each.key].id
  allocation_id = aws_eip.service_eips[each.key].id
}