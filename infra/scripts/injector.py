"""
Improvments for this script:
      - Add modularity by implementing a factory design pattern
"""

from multiprocessing import Value
import os 
import argparse
import subprocess
from tkinter import Variable
from typing import Any, Dict
import json 

from jinja2 import Template
from pydantic import BaseModel
from .templates import ENV_TEMPLATE
import shutil
from .extractor import Extractor

class VariableInjector():
      """
      This class provides the methods for injecting terraform outputs in the corresponding Jinja2 templates
      """

      def __init__(self, environment: str, terraform_dir: str) -> None:
            self.environment = environment
            self.terraform_dir = terraform_dir
            self.terraform_outputs : Dict = Extractor(environment=self.environment)._extract_outputs()


      def _write_injection(self, file_name: str, content: str, file_mode: str = "w"):
            """
            Args:
                  file_name (str):  top-level relative
            """
            if file_mode == "a":
                  if not os.path.exists(file_name):
                        raise ValueError(f"Path {file_name} doesnt exist. Cant append")
            with open(file=f"{file_name}", mode=file_mode) as f:
                  f.write(content)
      
      def _create_copy_of_base_file(self, base_env_path: str):
            if not os.path.exists(base_env_path):
                  raise Exception(f"base env path {base_env_path} doesnt exist")
            synced_file_path = base_env_path.replace("/base/", "/synced/")
            shutil.copy(base_env_path, synced_file_path)
            return synced_file_path

      def backend_dotenv_injection(self, base_env_path: str):
            """
            Algo: 
                  1) Inject template
                  2) Read base env, and append to template injection
                  3) Write file
            Parameters:
                  - env_output: str = the path for where to write the env 
            """

            template = Template(ENV_TEMPLATE)

            # Create copy of base file
            synced_file_path = self._create_copy_of_base_file(base_env_path=base_env_path)
            backend_outputs = self.terraform_outputs.get("backend")

            synced_content = template.render(outputs=backend_outputs)

            self._write_injection(
                                    file_name=synced_file_path, 
                                    content=synced_content, file_mode="a")
      
      def frontend_dotenv_injection(self, base_env_path: str):
            template = Template(ENV_TEMPLATE)

            if self.environment == "dev":
                  synced_file_path = self._create_copy_of_base_file(base_env_path=base_env_path)
                  sycned_content = template.render(outputs={"VITE_BASE_URL": 
                                                                              {"value":"http://localhost/api/"}})
                  self._write_injection(file_name=synced_file_path,
                                        content=sycned_content, 
                                        file_mode="a")
            elif self.environment == "production":
                  ...





            


if __name__ == "__main__":
      parser = argparse.ArgumentParser(description="Generate configuration files based on terraform outputs")
      parser.add_argument("--environment", help="Takes on [staging, dev, prod]")
      parser.add_argument("--terraform-dir", help="Directory of tf --where terraform output -json will be executed")
      parser.add_argument("--backend-dotenv-path", help="Type: str. Needs tp be the path to the base env. \
                                                Will be used to access the create a copy of base_env with appended template stuff ")
      parser.add_argument("--frontend-dotenv-path", help="Type: str. Path for where to write to the frontend. \
                                                Will be used to access the create a copy of base_env with appended template stuff ")

      args = parser.parse_args()
      injector = VariableInjector(environment=args.environment, terraform_dir=args.terraform_dir)

      if args.backend_dotenv_path:
            injector.backend_dotenv_injection(base_env_path=args.backend_dotenv_path)
      
      if args.frontend_dotenv_path:
            injector.frontend_dotenv_injection(base_env_path=args.frontend_dotenv_path)
            
