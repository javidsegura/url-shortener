import os
import subprocess

from dotenv import load_dotenv

load_dotenv(".env.dev")

if __name__ == "__main__":
      MYSQL_SYNC_DRIVER = os.getenv("MYSQL_SYNC_DRIVER")
      MYSQL_USER = os.getenv("MYSQL_USER")
      MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
      MYSQL_HOST = os.getenv("MYSQL_HOST")
      MYSQL_PORT = os.getenv("MYSQL_PORT")
      MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

      DATABASE_URL = (
            f"{MYSQL_SYNC_DRIVER}"
            f"://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}"
            f":{MYSQL_PORT}/{MYSQL_DATABASE}"
      )

      models_file_path = "src/database/generated_models.py"

      with open(models_file_path, "w") as f:
            subprocess.run(
                  ["sqlacodegen", DATABASE_URL],
                  stdout=f,
                  check=True # checks if sqlacodenge returned an error
            )      
