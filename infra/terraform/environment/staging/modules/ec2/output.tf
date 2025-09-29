output "ec2_app_server_instance_id" {
  value = aws_instance.web_app.id
}

output "ec2_app_server_private_ip" {
  value = aws_instance.web_app.private_ip
}