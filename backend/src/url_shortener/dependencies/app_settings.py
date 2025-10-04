from fastapi import Request
from url_shortener.core.settings.app_settings import Settings

def get_settings(request: Request) -> Settings:
      return request.app.state.settings