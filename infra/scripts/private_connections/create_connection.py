import argparse
from typing import Any, Dict
import boto3
import json
import os
import subprocess

from .utils import ConnectionModel

class ConnectionEstabisher():
      """
      REFACTORING TO BE DONE: 
            - Create bridge between type of connection and environments 
      """
      def __init__(self, environment :str, terraform_dir :str) -> None:
            self.environment = environment
            self.terraform_dir = terraform_dir
            self.terraform_outputs = self.extract_terraform_outputs()

      def extract_terraform_outputs(self):
            try:
                  # Extract raw outputs
                  output = subprocess.run(
                        ["terraform", "output", "-json"],
                        cwd=self.terraform_dir,
                        check=True,
                        text=True,
                        capture_output=True
                  )
                  raw_outputs = json.loads(output.stdout)
                  # Filter outputs to pydantic model
                  return self._filter_outputs_for_model(raw_outputs)
            except:
                  raise 
      def _filter_outputs_for_model(self, raw_outputs: Dict[str, Any]):
            model_fields = set(ConnectionModel.model_fields.keys())
            filtered = {
                  key.upper(): value["value"] for key, value in raw_outputs.items()
                  if key.upper() in model_fields
            }
            return ConnectionModel(**filtered)
      def _handle_ssh_connection(self):
            if self.environment == "production":
                  EC2_APP_SERVER_SSH_USER = self.terraform_outputs.EC2_APP_SERVER_SSH_USER
                  EC2_APP_SERVER_PUBLIC_IP = self.terraform_outputs.EC2_APP_SERVER_PUBLIC_IP
                  credentials_path = f"{self.terraform_dir}/secrets/ssh_key.pem"

                  subprocess.call(
                        ["ssh", "-i", f"{credentials_path}", f"{EC2_APP_SERVER_SSH_USER}@{EC2_APP_SERVER_PUBLIC_IP}"]
                  )
            else:
                  raise ValueError("Environment must be production or staging")
      def _handle_web_serving_connection(self):
            if self.environment == "production":
                  raise ValueError("Web served for production is served by accessing the web server public ip. Theres no set-up to be done \
                        for the connection")
            else:
                  raise ValueError("Environment must be production or staging")
      def _handle_db_connection(self):
            if self.environment == "production":
                  print("TERRAFORM OUTPUTS:", self.terraform_outputs)
                  EC2_APP_SERVER_SSH_USER = self.terraform_outputs.EC2_APP_SERVER_SSH_USER
                  EC2_APP_SERVER_PUBLIC_IP = self.terraform_outputs.EC2_APP_SERVER_PUBLIC_IP
                  RDS_MYSQL_HOST = self.terraform_outputs.RDS_MYSQL_HOST
                  credentials_path = f"{self.terraform_dir}/secrets/ssh_key.pem"
                  local_port_to_send_from = 3307
                  local_port_to_receive_from = 3306

                  cmd = ["ssh", "-i", f"{credentials_path}", "-N", "-L",
                         f"{local_port_to_send_from}:{RDS_MYSQL_HOST}:{local_port_to_receive_from}",
                         f"{EC2_APP_SERVER_SSH_USER}@{EC2_APP_SERVER_PUBLIC_IP}"]

                  subprocess.call(
                        cmd
                  )
            else:
                  raise ValueError("Environment must be production or staging")
            
      def connect(self, type_of_connection: str):
            if type_of_connection == "ssh":
                  self._handle_ssh_connection()
            elif type_of_connection == "web-serving":
                  self._handle_web_serving_connection()
            elif type_of_connection == "db":
                  self._handle_db_connection()
            else:
                  raise ValueError(f"No type of connection registered for: {type_of_connection}")




if __name__ == "__main__":
      parser = argparse.ArgumentParser(description="Extract credentials from AWS secrets manager")
      parser.add_argument("--environment",
                         help="Determine environment of execution", 
                         required=True,
                         choices=["dev", "staging", "production"])
      parser.add_argument("--terraform-dir", help="Directory of tf --where terraform output -json will be executed", required=True)
      parser.add_argument("--type-of-connection",
                         help="AWS region name",
                         required=True, 
                         choices=["ssh", "db", "web-serving"])

      args = parser.parse_args()
      connector = ConnectionEstabisher(environment=args.environment,
                                       terraform_dir=args.terraform_dir)
      connector.connect(type_of_connection=args.type_of_connection)

