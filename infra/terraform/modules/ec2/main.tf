

/*

THINGS TO DO:
1. Create VPC 
2. Create security group
3. Create EC2
4. Create SSH key pair
5. Crete ansible playbook
6. Bind public IP

*/

resource "aws_instance" "web_app" {
  ami = "ami-00ca32bbc84273381"
  instance_type = "t2.micro"
  subnet_id = var.public_subnet_id
  vpc_security_group_ids = [var.web_app_sg_id]
  key_name = aws_key_pair.key_pair_ssh.key_name
  
  root_block_device {
    volume_size = 8
  }
}

# Creating SSH key pair
resource "tls_private_key" "priv_key" {
  algorithm = "RSA"
  rsa_bits = 4096
}
resource "aws_key_pair" "key_pair_ssh" {
  key_name = "ssh_key"
  public_key = tls_private_key.priv_key.public_key_openssh  
}

resource "local_file" "private_key" {
  content = tls_private_key.priv_key.private_key_pem
  filename = var.ssh_key_local_path
  file_permission = "0400"
}

