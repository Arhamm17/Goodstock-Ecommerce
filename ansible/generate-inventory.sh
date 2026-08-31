#!/bin/bash
set -e
TERRAFORM_DIR="../terraform"
IP=$(terraform -chdir="$TERRAFORM_DIR" output -raw instance_public_ip)

cat > inventory/hosts.ini << EOF
[app_servers]
$IP ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/devops-ecommerce-key ansible_python_interpreter=/usr/bin/python3
EOF

echo "Inventory generated with IP: $IP"
cat inventory/hosts.ini