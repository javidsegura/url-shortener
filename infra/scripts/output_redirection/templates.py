
"""

TEMPLATES INJECTED EXAMPLES:

- SSH:
      Host bastion
      HostName 44.200.5.230
      User ec2-user
      IdentityFile /Users/javierdominguezsegura/Programming/S25/full-stack/url-shortener/infra/terraform/environment/staging/secrets/ssh_key.pem

      Host staging_web_server
      HostName 10.0.2.226
      User ec2-user
      IdentityFile /Users/javierdominguezsegura/Programming/S25/full-stack/url-shortener/infra/terraform/environment/staging/secrets/ssh_key.pem
      ProxyJump bastion
- Environmental variables:
      KEY:VALUE [map]
- Ansible inventory
      [all:vars]
      ansible_ssh_private_key_file = ./terraform/environment/production/secrets/ssh_key.pem

      [web_servers]
      3.237.195.233 ansible_user=ec2-user

"""
"""
ORGANIZATION PROCESS:
      1. Test in dev with environment only 
"""


ENV_TEMPLATE = """
{% for key, output in outputs.items() %}
{{ key.upper() }}={{ output }}
{% endfor %}
""".strip()


ANSIBLE_TEMPLATE_PRODUCTION = """
[web_servers]
{{ outputs.EC2_APP_SERVER_PUBLIC_IP }} ansible_user={{ outputs.EC2_APP_SERVER_SSH_USER }}

[all:vars]
ansible_ssh_private_key_file={{ outputs.EC2_APP_SERVER_SSH_PRIVATE_KEY_FILE_PATH }} 


"""

ANSIBLE_TEMPLATE_STAGING = """
[web_servers]
{{ outputs.EC2_APP_SERVER_INSTANCE_ID }} ansible_host={{ outputs.EC2_APP_SERVER_INSTANCE_ID }}

[web_servers:vars]
ansible_connection=aws_ssm
ansible_aws_ssm_region={{ outputs.AWS_MAIN_REGION }}
ansible_aws_ssm_s3_addressing_style=virtual
ansible_aws_ssm_s3_key_prefix=ssm/staging/
"""