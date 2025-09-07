output "api_s3_bucket_name" {
  value = module.s3.s3_bucket_name
}
output "server_host_ip" {
  value = module.ec2.ec2_public_ip
}
output "ssh_user" {
  value = "ec2-user"
}
output "ssh_private_key_file" {
  value = var.ssh_key_local_path
}