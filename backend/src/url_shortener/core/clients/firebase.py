import logging
import os
import firebase_admin
from firebase_admin import credentials

logger = logging.getLogger(__name__)


def initialize_firebase():
	logger.debug("Initializing firebase...")

	# 1. Check if we are in test mode or explicitly asking for the emulator
	env_is_test = os.getenv("ENVIRONMENT") == "test"
	using_emulator = os.getenv("USING_FIREBASE_EMULATOR", "").lower() == "true"

	if env_is_test or using_emulator:
		logger.info(f"Using Firebase Auth Emulator (Env: {os.getenv('ENVIRONMENT')})")

		# Check if app is already initialized to avoid "App already exists" errors
		try:
			firebase_admin.get_app()
		except ValueError:
			# Initialize with a dummy project ID.
			# No credential file is needed here!
			firebase_admin.initialize_app(
				options={"projectId": os.getenv("FB_PROJECT_ID", "test-project")}
			)
	else:
		logger.info("Using Real Firebase Auth")

		# This block ONLY runs in Production/Dev (Local), never in CI
		cert_path = "./src/url_shortener/core/clients/secret.url-shortener-abadb-firebase-adminsdk-fbsvc-48d38c91f0.json"

		if not os.path.exists(cert_path):
			# Extra safety: Log a helpful error if the file is missing in Dev
			logger.error(f"Firebase credential file not found at: {cert_path}")
			raise FileNotFoundError(f"Missing Firebase credentials: {cert_path}")

		cred = credentials.Certificate(cert_path)

		try:
			firebase_admin.get_app()
		except ValueError:
			firebase_admin.initialize_app(cred)
