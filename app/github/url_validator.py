"""
Module for GitHub URL validation and parsing.

This module provides utilities for validating GitHub repository URLs
and extracting repository information (owner, repo name, branch) from them.
"""

import re
from typing import Optional, Tuple


def validate_github_url(url: Optional[str]) -> bool:
    """
    Validate if the given URL is a valid GitHub repository URL.
    
    Args:
        url (str): The URL to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not url:
        return False
    
    # HTTPS GitHub URL pattern
    https_pattern = r'^https?://github\.com/[a-zA-Z0-9-]+/[a-zA-Z0-9._-]+(/.*)?$'
    
    # SSH GitHub URL pattern
    ssh_pattern = r'^git@github\.com:[a-zA-Z0-9-]+/[a-zA-Z0-9._-]+\.git$'
    
    # Check if the URL matches either pattern
    if re.match(https_pattern, url):
        # Additional validation for HTTPS URLs
        # Need at least owner and repo name
        try:
            parts = url.split('github.com/')[1].split('/')
            return bool(len(parts) >= 2 and parts[0] and parts[1])
        except IndexError:
            return False
    
    return bool(re.match(ssh_pattern, url))


def extract_repo_info(url: str) -> Tuple[str, str, Optional[str]]:
    """
    Extract owner name, repository name, and branch name from a GitHub URL.
    
    Args:
        url (str): The GitHub URL
        
    Returns:
        tuple: (owner, repo, branch) where branch may be None
    """
    if not validate_github_url(url):
        raise ValueError("Invalid GitHub URL")
    
    # Handle URL fragments and query parameters
    url = url.split('#')[0]  # Remove fragment
    url = url.split('?')[0]  # Remove query parameters
    
    # Extract from HTTPS URL
    if url.startswith("https://") or url.startswith("http://"):
        # Remove leading protocol and domain
        path = url.split("github.com/")[1]
        
        # Extract owner and repo
        parts = path.split('/')
        owner = parts[0]
        repo = parts[1]
        
        # Remove .git suffix if present
        if repo.endswith(".git"):
            repo = repo[:-4]
        
        # Check for branch or file path indicators
        branch = None
        branch_indicators = ["/tree/", "/blob/", "/commit/"]
        
        for indicator in branch_indicators:
            if indicator in path:
                # Get the path after the indicator
                branch_path = path.split(indicator)[1].split('/')[0]
                branch = branch_path
                break
        
        return owner, repo, branch
    
    # Extract from SSH URL
    elif url.startswith("git@"):
        # Format: git@github.com:owner/repo.git
        path = url.split("github.com:")[1]
        parts = path.split("/")
        owner = parts[0]
        repo = parts[1]
        
        # Remove .git suffix
        if repo.endswith(".git"):
            repo = repo[:-4]
            
        return owner, repo, None
    
    # Should not reach here due to validation check
    raise ValueError("Unknown URL format") 