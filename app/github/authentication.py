"""
Module for GitHub authentication.

This module provides utilities for GitHub OAuth authentication flow,
including creating authorization URLs, exchanging codes for tokens,
and validating tokens.
"""

import secrets
import urllib.parse
from dataclasses import dataclass
from typing import Dict, Any

import requests


@dataclass
class OAuthConfig:
    """Configuration for GitHub OAuth authentication."""
    client_id: str
    client_secret: str
    redirect_uri: str
    scope: str


def create_oauth_url(config: OAuthConfig) -> str:
    """
    Create a GitHub OAuth authorization URL.
    
    Args:
        config: OAuth configuration
        
    Returns:
        Authorization URL for GitHub OAuth
    """
    # Generate a random state for CSRF protection
    state = secrets.token_hex(16)
    
    # Build the parameters for the OAuth URL
    params = {
        'client_id': config.client_id,
        'redirect_uri': config.redirect_uri,
        'scope': config.scope,
        'state': state
    }
    
    # Construct the URL with parameters
    base_url = "https://github.com/login/oauth/authorize"
    query_string = urllib.parse.urlencode(params)
    
    return f"{base_url}?{query_string}"


def exchange_code_for_token(code: str, config: OAuthConfig) -> Dict[str, Any]:
    """
    Exchange an authorization code for an access token.
    
    Args:
        code: The authorization code from GitHub callback
        config: OAuth configuration
        
    Returns:
        Dict containing access_token, token_type, and scope
        
    Raises:
        ValueError: If the code exchange fails
    """
    # Prepare the request to exchange code for token
    url = "https://github.com/login/oauth/access_token"
    headers = {
        'Accept': 'application/json'
    }
    data = {
        'client_id': config.client_id,
        'client_secret': config.client_secret,
        'code': code,
        'redirect_uri': config.redirect_uri
    }
    
    # Make the request to GitHub
    response = requests.post(url, json=data, headers=headers)
    
    # Check if the response was successful
    if response.status_code != 200:
        error_info = response.json()
        error_message = error_info.get('error_description', 'Unknown error')
        error_code = error_info.get('error', 'unknown_error')
        raise ValueError(f"Failed to exchange code for token: {error_code} - {error_message}")
    
    # Return the token information
    return response.json()


def validate_token(token: str) -> Dict[str, Any]:
    """
    Validate a GitHub access token and get user information.
    
    Args:
        token: GitHub access token
        
    Returns:
        Dict containing user information
        
    Raises:
        ValueError: If the token is invalid
    """
    # Prepare the request to the GitHub API
    url = "https://api.github.com/user"
    headers = {
        'Authorization': f"token {token}"
    }
    
    # Make the request to GitHub
    response = requests.get(url, headers=headers)
    
    # Check if the response was successful
    if response.status_code != 200:
        raise ValueError(f"Invalid token. Status code: {response.status_code}")
    
    # Return the user information
    return response.json() 