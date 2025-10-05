import firebase_admin
from firebase_admin import credentials

def initialize_firebase():
	cred = credentials.Certificate(
		"./src/url_shortener/core/clients/secret.url-shortener-abadb-firebase-adminsdk-fbsvc-48d38c91f0.json"
	)
	try:
		firebase_admin.get_app()
	except ValueError:
		firebase_admin.initialize_app(cred)
	
