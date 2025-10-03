from typing import Annotated, Dict

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from firebase_admin import auth

oauth2scheme = OAuth2PasswordBearer(tokenUrl="token")

# The following depenencies restricts access if token_id is not enabled


def get_current_user(
	email_needs_verification: bool = False, user_specific_route: bool = False
) -> callable:
	"""
	Args:
		Note => user_id is for the the path dynamic part
	"""

	def get_token_dependency(
		request: Request, token: str = Depends(oauth2scheme)
	) -> Dict[str, any]:
		try:
			decoded_token = auth.verify_id_token(token)
			user_record = auth.get_user(decoded_token["uid"])
			user_id_path = request.path_params.get("user_id")

			if (email_needs_verification) and (not user_record.email_verified):
				raise Exception("Email not verified")
			if user_specific_route:
				if not user_id_path:
					raise HTTPException(
						status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
						detail="Need to pass user id route",
					)
				else:
					if decoded_token["uid"] != user_id_path:
						raise HTTPException(
							status_code=status.HTTP_401_UNAUTHORIZED,
							detail="Access denied: You can only access your own \
								resources",
						)

			return {
				**decoded_token,
				"email_verified": user_record.email_verified,
				"display_name": user_record.display_name,
			}

		except Exception as e:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"{e}")

	return get_token_dependency

def is_user_admin(token : Annotated[str, Depends(oauth2scheme)]):
	decoded_token = auth.verify_id_token(token)
	uid = decoded_token["uid"]