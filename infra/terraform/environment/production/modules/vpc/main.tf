

# VPC
resource "aws_vpc" "main_vpc" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "public_subnet" {
  vpc_id = aws_vpc.main_vpc.id
  cidr_block = "10.0.1.0/24"
  availability_zone = "${var.main_region}a"
  map_public_ip_on_launch = true
}

resource "aws_internet_gateway" "IGW" {
  vpc_id = aws_vpc.main_vpc.id
}


resource "aws_route_table" "public_IGW_route_table" {
  vpc_id = aws_vpc.main_vpc.id
  route {
      cidr_block = "0.0.0.0/0"
      gateway_id = aws_internet_gateway.IGW.id
  }
}

resource "aws_route_table_association" "public_IGW_association" {
  subnet_id = aws_subnet.public_subnet.id
  route_table_id = aws_route_table.public_IGW_route_table.id
}

# SECURITY GROUPS
resource "aws_security_group" "web_app_sg" {
  vpc_id = aws_vpc.main_vpc.id

  name = "Public Web App SG"
  ingress {
    from_port = 80
    to_port = 80
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port = 0
    to_port = 0
    protocol = -1
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port = 0
    to_port = 0
    protocol = -1
    cidr_blocks = ["0.0.0.0/0"]
  }
}