import pytest

# Assuming your FastAPI app instance is in a file named `main.py`
# inside a `url_shortener` package.
# Adjust the import path if your file structure is different.
from url_shortener.main import app
from url_shortener.core.settings.app_settings import Settings

def test_app_startup_initializes_settings(fastapi_client):
      """
      Tests if the application's lifespan manager correctly initializes
      and attaches the settings object to the app's state.
      """

      assert hasattr(fastapi_client.app.state, 'settings'), "The 'settings' attribute was not found in app.state."
      assert isinstance(fastapi_client.app.state.settings, Settings), f"Expected an instance of Settings, but got {type(fastapi_client.app.state.settings)}."
