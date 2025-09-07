output "public_subnet_id" {
  value = aws_subnet.public_subnet.id
}
output "web_app_sg_id" {
  value = aws_security_group.web_app_sg.id
}