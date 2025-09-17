import os 
import argparse
import subprocess
from tkinter import Variable
from typing import Dict
import json 

from jinja2 import Template
from .templates import ENV_TEMPLATE
import shutil


class VariableInjector():
      """
      This class provides the methods for injecting terraform outputs in the corresponding Jinja2 templates
      """

      def __init__(self, environment: str, terraform_dir: str) -> None:
            self.environment = environment
            self.terraform_dir = terraform_dir
            self.terraform_outputs : Dict = self._extract_outputs()

      def _extract_outputs(self):
            output = subprocess.run(
                  ["terraform", "output",  "-json"],
                  cwd=self.terraform_dir,
                  check=True,
                  text=True,
                  capture_output=True
            )
            return json.loads(output.stdout)
      
      def _write_injection(self, file_name: str, content: str, file_mode: str = "w"):
            """
            Args:
                  file_name (str):  top-level relative
            """
            with open(file=f"{file_name}", mode=file_mode) as f:
                  f.write(content)

      def dotenv_inejction(self, base_env_path: str):
            """
            Algo: 
                  1) Inject template
                  2) Read base env, and append to template injection
                  3) Write file
            Parameters:
                  - env_output: str = the path for where to write the env 
            """

            print(self.terraform_outputs)

            template = Template(ENV_TEMPLATE)
            # Create copy of base file
            synced_file_path = base_env_path.replace("base", "synced")
            shutil.copy(base_env_path, synced_file_path)

            synced_content = template.render(outputs=self.terraform_outputs)
            self._write_injection(
                                    file_name=synced_file_path, 
                                    content=synced_content, file_mode="a")


            


if __name__ == "__main__":
      parser = argparse.ArgumentParser(description="Generate configuration files based on terraform outputs")
      parser.add_argument("--environment", help="Takes on [staging, dev, prod]")
      parser.add_argument("--terraform-dir", help="Directory of tf --where terraform output -json will be executed")
      parser.add_argument("--base-dotenv-path", help="Type: str. Needs tp be the path to the base env. \
                                                Will be used to access the create a copy of base_env with appended template stuff ")

      args = parser.parse_args()
      injector = VariableInjector(environment=args.environment, terraform_dir=args.terraform_dir)

      if args.base_dotenv_path:
            injector.dotenv_inejction(base_env_path=args.base_dotenv_path )
            
