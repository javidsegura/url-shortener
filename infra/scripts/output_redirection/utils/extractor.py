
from typing import Dict, Any
from pydantic import BaseModel
import subprocess
import json

class Extractor:
      def __init__(self, environment, terraform_dir) -> None:
            self.environment = environment
            self.terraform_dir = terraform_dir
      def _extract_outputs(self):
                  output = subprocess.run(
                        ["terraform", "output",  "-json"],
                        cwd=self.terraform_dir,
                        check=True,
                        text=True,
                        capture_output=True
                  )
                  # raw_outputs = {
                  #       "S3_MAIN_BUCKET_NAME": 
                  #       {
                  #             "value": "A greate s3 bucket main name"
                  #       },
                  #       "RDS_MYSQL_HOST": 
                  #       {
                  #             "value": "Rds mysql hostttttt"
                  #       },
                  #       "ec2_app_server_private_ip".upper(): 
                  #       {
                  #             "value": "Ec2 app public ippppp"
                  #       },
                  #       "ec2_bastion_server_public_ip".upper(): 
                  #       {
                  #             "value": "Ec2 app public ippppp"
                  #       },
                  #       "ec2_app_server_ssh_user".upper(): 
                  #       {
                  #             "value": "EC2 app ssh userrrrr"
                  #       },
                  #       "ec2_app_bastion_ssh_user".upper(): 
                  #       {
                  #             "value": "EC2 app ssh userrrrr"
                  #       },
                  #       "ec2_app_servers_ssh_private_key_file_path".upper(): 
                  #       {
                  #             "value": "EC2 app server private key file paaath"
                  #       },
                  #       "rds_db_credentials_key".upper(): 
                  #       {
                  #             "value": "Rds db credentials keyyyy"
                  #       },
                  # }

                  raw_outputs =  json.loads(output.stdout)
                  flattened_outputs = {
                        key: value["value"]
                        for key, value in raw_outputs.items()
                  }
                  validated_outputs = self._filter_terraform_outputs(flattened_outputs)
                  return validated_outputs
      
      def _filter_terraform_outputs(self, outputs: Dict[str, Any]):
            frontend_model, backend_model, ansible_model = self._get_models_per_environment(self.environment)
            filtered_outputs = {
                  "frontend": self._filter_outputs_for_model(outputs, frontend_model),
                  "backend": self._filter_outputs_for_model(outputs, backend_model),
                  "ansible": self._filter_outputs_for_model(outputs, ansible_model),
            }
            return filtered_outputs
      


      def _get_models_per_environment(self, environment: str):
            from ..models.dev import DevBackendOutputs, DevFrontendOutputs, DevAnsibleOutputs
            from ..models.production import ProductionBackendOutputs, ProductionFrontendOutputs, ProductionAnsibleOutputs

            model_mapping = {
                  "dev": (DevFrontendOutputs, DevBackendOutputs, DevAnsibleOutputs),
                  "production": (ProductionFrontendOutputs, ProductionBackendOutputs, ProductionAnsibleOutputs),
            }

            model_class = model_mapping.get(environment)
            if not model_class:
                  raise ValueError(f"No validation model found for environment: {self.environment}")
            return model_class
      def _filter_outputs_for_model(self, outputs: Dict[str, Any], model_class: BaseModel):
            if not model_class:
                  return {}
            
            model_fields = set(model_class.__fields__.keys())
            filtered = {
                  key.upper(): value for key, value in outputs.items()
                  if key.upper() in model_fields
            }
            return filtered