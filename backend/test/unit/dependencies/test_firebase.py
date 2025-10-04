import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from firebase_admin import auth

from url_shortener.dependencies import verify_user, is_user_admin 

def test_verify_user_success(mocker):
    # Mock the external dependencies
    mock_token = "valid_token"
    mock_decoded_token = {"uid": "user123"}
    mock_user_record = MagicMock()
    mock_user_record.email_verified = True
    mock_user_record.display_name = "John Doe"
    
    mocker.patch.object(auth, "verify_id_token", return_value=mock_decoded_token)
    mocker.patch.object(auth, "get_user", return_value=mock_user_record)
    
    # Create a mock Request object
    mock_request = MagicMock()
    mock_request.path_params = {}

    # Call the function with mocked dependencies
    dependency = verify_user()
    result = dependency(request=mock_request, token=mock_token)

    # Assert the expected output
    assert result["uid"] == "user123"
    assert result["email_verified"] is True
    assert result["display_name"] == "John Doe"

