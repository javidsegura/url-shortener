import os
import sys
from fastapi.testclient import TestClient
import pytest
import uuid
import subprocess
from pathlib import Path

import pytest
from dotenv import load_dotenv
import logging

logger =logging.getLogger(__name__)

ORIGINAL_ENV_KEYS = None

def pytest_configure(config):
    """Mock all required environment variables for tests."""
    global ORIGINAL_ENV_KEYS
    ORIGINAL_ENV_KEYS = set(os.environ.keys())
    if "ENVIRONMENT" in set(os.environ.keys()):
        del os.environ["ENVIRONMENT"]
    path_to_dotenv = "./env_config/synced/.env.test"
    if not os.path.exists(path_to_dotenv):
        raise FileNotFoundError(f"Could not find dotenv file at {path_to_dotenv}")
    else:
        logger.debug(f"Path found for {path_to_dotenv}")
    load_dotenv(path_to_dotenv)
    if "MYSQL_HOST" in set(os.environ.keys()): # DB migration container and test (usage needed now) use different vals for the same key
        os.environ["MYSQL_HOST"] = "localhost"
        logger.debug("Just modified MYSQL_HOST")
    if "MYSQL_PORT" in set(os.environ.keys()):
        os.environ["MYSQL_PORT"] = "3307"
        logger.debug("Just modified MYSQL_PORT")
    logger.debug(f"ENV FOR INITIALIZATION IS: {set(os.environ.keys())}")



def pytest_unconfigure(config):
    """
    This hook runs after the entire test session finishes,
    perfect for cleanup.
    """
    print("\nCleaning up environment variables...")
    CURRENT_ENV_KEYS = set(os.environ.keys())
    keys_to_del = ORIGINAL_ENV_KEYS - CURRENT_ENV_KEYS
    for key in keys_to_del:
        if key in os.environ:
                del os.environ[key]

@pytest.fixture(scope="session")
def fastapi_client():
      from url_shortener.main import app
      with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def start_docker_compose_services():

    # Start docker compose services
    try:
        subprocess.run(
            ["make", "test-docker-compose-start"],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print("❌ Failed to start docker-compose:")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        raise
    yield
    # Clean docker compose services
    subprocess.run(
        args=["make", "test-docker-compose-stop"],
        check=True
    )
