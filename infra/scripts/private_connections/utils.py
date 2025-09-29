from pydantic import BaseModel


class ProdConnectionModel(BaseModel):
      EC2_APP_SERVER_SSH_USER : str
      EC2_APP_SERVER_PUBLIC_IP : str
      EC2_SERVERS_SSH_PRIVATE_KEY_FILE_PATH: str
      RDS_MYSQL_HOST : str

class StagingConnectionModel(BaseModel):
      EC2_APP_SERVER_SSH_USER : str
      EC2_APP_SERVER_PRIVATE_IP : str
      EC2_BASTION_SERVER_PUBLIC_IP : str
      EC2_BASTION_SERVER_SSH_USER : str
      EC2_SERVERS_SSH_PRIVATE_KEY_FILE_PATH: str
      RDS_MYSQL_HOST : str

      # ssh -i ssh_key.pem -o ProxyCommand="ssh -i ssh_key.pem -o StrictHostKeyChecking=no -o IdentitiesOnly=yes -W %h:%p -q ec2-user@18.215.124.7" ec2-user@10.0.2.113