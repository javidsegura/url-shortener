from pydantic import BaseModel


class ConnectionModel(BaseModel):
      EC2_APP_SERVER_SSH_USER : str
      EC2_APP_SERVER_PUBLIC_IP : str
      RDS_MYSQL_HOST : str