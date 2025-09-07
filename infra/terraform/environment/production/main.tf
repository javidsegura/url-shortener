

terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.main_region

  default_tags {
    tags = {
      Environment = var.environment
    }
  }
}

module "s3" {
  source = "../../modules/s3"

  environment = var.environment
  main_region = var.main_region
  
}

module "vpc" {
  source = "./modules/vpc"

  main_region = var.main_region
}

module "ec2" {
  source = "../../modules/ec2"

  public_subnet_id = module.vpc.public_subnet_id
  web_app_sg_id = module.vpc.web_app_sg_id
  ssh_key_local_path = var.ssh_key_local_path

}



