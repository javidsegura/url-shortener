

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
}

module "s3_services" {
  source = "../../modules/s3"

  environment = var.environment
  main_region = var.main_region
  
}