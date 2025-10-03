import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate(
	"./src/core/auth/url-shortener-abadb-firebase-adminsdk-fbsvc-52980dc022.json"
)
try:
	firebase_admin.get_app()
except ValueError:
	firebase_admin.initialize_app(cred)
