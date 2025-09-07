

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
  instance_type = "t3.small"
  subnet_id = var.public_subnet_id
  vpc_security_group_ids = [var.web_app_sg_id]
  key_name = aws_key_pair.key_pair_ssh.key_name

  iam_instance_profile = aws_iam_instance_profile.web_app_profile.name
  
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


# IAM ROLES
# IAM ROLES
# Policy allowing EC2 to assume this role (Trust Policy)
data "aws_iam_policy_document" "assume_role" {
  statement {
    sid = "AllowEC2ToAssumeRole"
    principals {
      type = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

# IAM Role for EC2 instance
resource "aws_iam_role" "app_server_s3_permissions" {
  name = "app_server_s3_permissions"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

# IAM Instance Profile to attach the role to the EC2 instance
resource "aws_iam_instance_profile" "web_app_profile" {
  name = "web_app_profile"
  role = aws_iam_role.app_server_s3_permissions.name
}

# Policy defining S3 permissions
data "aws_iam_policy_document" "s3_access_policy" {
  statement {
    sid = "S3ReadAndPut"
    actions = [
      "s3:GetObject",
      "s3:PutObject"
    ]
    resources = ["${var.aws_s3_web_arn}/*"]
  }
}

# IAM Policy for S3 access
resource "aws_iam_policy" "s3_read_put_policy" {
  name        = "S3_Read_Put_Policy"
  description = "A policy that allows S3 read and put access."
  policy      = data.aws_iam_policy_document.s3_access_policy.json
}

# Attaching the S3 policy to the IAM Role
resource "aws_iam_role_policy_attachment" "s3_attachment" {
  role       = aws_iam_role.app_server_s3_permissions.name
  policy_arn = aws_iam_policy.s3_read_put_policy.arn
}