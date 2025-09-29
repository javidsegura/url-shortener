output "ec2_app_server_instance_id" {
  value = module.ec2.ec2_app_server_instance_id
}
output "ec2_app_server_private_ip" {
  value = module.ec2.ec2_app_server_private_ip
}
output "s3_main_bucket_name" {
  value = module.s3.s3_bucket_name
}
output "rds_db_credentials_key" {
  value = module.rds.db_crendentials_key
}

output "rds_mysql_host" {
  value = module.rds.rds_address
}

output "aws_main_region" {
  value = var.main_region
}