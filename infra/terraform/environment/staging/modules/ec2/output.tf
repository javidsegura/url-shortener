output "bastion_public_ip" {
  value = aws_instance.bastion_host.public_ip
}

output "web_app_private_ip" {
  value = aws_instance.web_app.private_ip
}