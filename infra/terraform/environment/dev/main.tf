

terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket = "url-shortener-remote-state-bucket-sblyckh5"
    key = "remote-state/dev/terraform.tfstate"
    region = "us-east-1"
    encrypt = true
  }
}

provider "aws" {
  region = var.main_region
}

module "s3_services" {
  source = "../../modules/s3"

  environment = var.environment
  main_region = var.main_region
  
}