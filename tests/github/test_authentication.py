"""
Tests for the GitHub authentication module.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.github.authentication import (
    create_oauth_url, 
    exchange_code_for_token, 
    validate_token, 
    OAuthConfig
)


def test_oauth_config_initialization():
    """Test the OAuthConfig initialization."""
    config = OAuthConfig(
        client_id="test_client_id",
        client_secret="test_client_secret",
        redirect_uri="http://localhost:8000/auth/callback",
        scope="repo,user"
    )
    
    assert config.client_id == "test_client_id"
    assert config.client_secret == "test_client_secret"
    assert config.redirect_uri == "http://localhost:8000/auth/callback"
    assert config.scope == "repo,user"


def test_create_oauth_url():
    """Test creating GitHub OAuth URL."""
    config = OAuthConfig(
        client_id="test_client_id",
        client_secret="test_client_secret",
        redirect_uri="http://localhost:8000/auth/callback",
        scope="repo,user"
    )
    
    url = create_oauth_url(config)
    
    assert "https://github.com/login/oauth/authorize" in url
    assert "client_id=test_client_id" in url
    assert "redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fauth%2Fcallback" in url
    assert "scope=repo%2Cuser" in url
    assert "state=" in url  # State parameter should be included for CSRF protection


@patch('requests.post')
def test_exchange_code_for_token_success(mock_post):
    """Test successful exchange of code for token."""
    # Mock successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "access_token": "test_access_token",
        "token_type": "bearer",
        "scope": "repo,user"
    }
    mock_post.return_value = mock_response
    
    config = OAuthConfig(
        client_id="test_client_id",
        client_secret="test_client_secret",
        redirect_uri="http://localhost:8000/auth/callback",
        scope="repo,user"
    )
    
    token_info = exchange_code_for_token("test_code", config)
    
    assert token_info["access_token"] == "test_access_token"
    assert token_info["token_type"] == "bearer"
    assert token_info["scope"] == "repo,user"
    
    # Verify the correct request was made
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert "https://github.com/login/oauth/access_token" in call_args[0][0]
    assert call_args[1]["headers"]["Accept"] == "application/json"
    assert call_args[1]["json"]["client_id"] == "test_client_id"
    assert call_args[1]["json"]["client_secret"] == "test_client_secret"
    assert call_args[1]["json"]["code"] == "test_code"
    assert call_args[1]["json"]["redirect_uri"] == "http://localhost:8000/auth/callback"


@patch('requests.post')
def test_exchange_code_for_token_failure(mock_post):
    """Test handling of token exchange failure."""
    # Mock error response
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {
        "error": "bad_verification_code",
        "error_description": "The code passed is incorrect or expired."
    }
    mock_post.return_value = mock_response
    
    config = OAuthConfig(
        client_id="test_client_id",
        client_secret="test_client_secret",
        redirect_uri="http://localhost:8000/auth/callback",
        scope="repo,user"
    )
    
    with pytest.raises(ValueError) as exc_info:
        exchange_code_for_token("invalid_code", config)
    
    assert "Failed to exchange code for token" in str(exc_info.value)
    assert "bad_verification_code" in str(exc_info.value)


@patch('requests.get')
def test_validate_token_valid(mock_get):
    """Test validation of a valid token."""
    # Mock successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "login": "test_user",
        "id": 12345
    }
    mock_get.return_value = mock_response
    
    user_info = validate_token("valid_token")
    
    assert user_info["login"] == "test_user"
    assert user_info["id"] == 12345
    
    # Verify the correct request was made
    mock_get.assert_called_once()
    call_args = mock_get.call_args
    assert "https://api.github.com/user" in call_args[0][0]
    assert call_args[1]["headers"]["Authorization"] == "token valid_token"


@patch('requests.get')
def test_validate_token_invalid(mock_get):
    """Test validation of an invalid token."""
    # Mock error response
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_get.return_value = mock_response
    
    with pytest.raises(ValueError) as exc_info:
        validate_token("invalid_token")
    
    assert "Invalid token" in str(exc_info.value) 