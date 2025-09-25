

from typing import Any, Dict

from pydantic import BaseModel
from ...templates import ENV_TEMPLATE
from jinja2 import Template

class FrontendInjector:
      def __init__(self, environment) -> None:
            self.environment = environment

      def _resolve_base_url(self, ansible_outputs: BaseModel):
            public_ip = ansible_outputs.get("EC2_APP_SERVER_PUBLIC_IP")
            if self.environment == "dev":
                  return {"VITE_BASE_URL": "http://localhost/api/"}
            elif self.environment == "production":
                  return {"VITE_BASE_URL": f"http://{public_ip}/api/"}

      def frontend_dotenv_injection(self, frontend_outputs: str):
            template = Template(ENV_TEMPLATE)
            vite_base_app_url = self._resolve_base_url(frontend_outputs)

            sycned_content = template.render(outputs=vite_base_app_url)
            return sycned_content
