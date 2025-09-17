output "env_backend_s3_bucket_name" {
  value = module.s3.s3_bucket_name
}
output "env_backend_mysql_host" {
  value = module.rds.rds_address
}
output "env_backend_db_credentials_key" {
  value = module.rds.db_crendentials_key
}
output "env_frontend_web_app_host_ip" {
  value = module.ec2.web_app_private_ip
}
output "ansible_bastion_host_ip" {
  value = module.ec2.bastion_public_ip
}
output "ansible_web_app_host_ip" {
  value = module.ec2.web_app_private_ip
}
output "ansible_bastion_ssh_user" {
  value = "ec2-user"
}
output "ansible_web_app_ssh_user" {
  value = "ec2-user"
}
output "ansible_ssh_private_key_file" {
  value = var.ssh_key_local_path
}

