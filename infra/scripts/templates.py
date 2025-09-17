
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

# INJECT VARIABLES FROM TF
{% for key, output in outputs.items() %}
{{ key.upper() }}={{ output.value }}
{% endfor %}
""".strip()