"""
Module for GitHub token storage.

This module provides utilities for storing, loading, and deleting 
GitHub access tokens securely.
"""

import os
import json
import logging
import time
from typing import Dict, Optional, Any


logger = logging.getLogger(__name__)


def save_token(token_data: Dict[str, Any], file_path: str) -> bool:
    """
    Save a GitHub token to a file.
    
    Args:
        token_data: Dictionary containing token information
        file_path: Path to the file where the token should be saved
        
    Returns:
        True if the token was saved successfully, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        # Write token data to file
        with open(file_path, 'w') as f:
            json.dump(token_data, f, indent=2)
        
        # Set file permissions to be readable only by the owner
        try:
            os.chmod(file_path, 0o600)
        except Exception as e:
            logger.warning(f"Failed to set permissions on token file: {e}")
        
        return True
    except Exception as e:
        logger.error(f"Failed to save token: {e}")
        return False


def load_token(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Load a GitHub token from a file.
    
    Args:
        file_path: Path to the file containing the token
        
    Returns:
        Dictionary containing token information, or None if token could not be loaded
    """
    try:
        # Check if the file exists
        if not os.path.exists(file_path):
            logger.warning(f"Token file not found: {file_path}")
            return None
        
        # Read token data from file
        with open(file_path, 'r') as f:
            token_data = json.load(f)
        
        return token_data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse token file: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to load token: {e}")
        return None


def delete_token(file_path: str) -> bool:
    """
    Delete a GitHub token file.
    
    Args:
        file_path: Path to the file containing the token
        
    Returns:
        True if the token was deleted successfully, False otherwise
    """
    # Check if the file exists
    if not os.path.exists(file_path):
        logger.warning(f"Token file not found for deletion: {file_path}")
        return True  # Consider it a success if the file is already gone
    
    # Try to delete the file with retries for Windows systems
    max_retries = 3
    retry_delay = 0.5  # seconds
    
    for attempt in range(max_retries):
        try:
            # Delete the file
            os.unlink(file_path)
            
            # Verify the file was deleted
            if not os.path.exists(file_path):
                return True
            
            # If we're here, the file wasn't deleted but no exception was raised
            if attempt < max_retries - 1:
                logger.warning(f"File still exists after deletion attempt {attempt+1}. Retrying...")
                time.sleep(retry_delay)
        except Exception as e:
            logger.error(f"Failed to delete token: {e}")
            if attempt < max_retries - 1:
                logger.warning(f"Retry attempt {attempt+1}/{max_retries}")
                time.sleep(retry_delay)
            else:
                return False
    
    # If we reach here, all retries failed
    return False 