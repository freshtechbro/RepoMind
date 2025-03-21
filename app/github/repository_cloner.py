"""
Module for cloning GitHub repositories.

This module provides functionality for cloning GitHub repositories
and tracking the cloning progress.
"""

import os
import shutil
from typing import Optional, Tuple, Callable

import git

from app.github.url_validator import extract_repo_info


class ProgressTracker:
    """
    Tracks progress of repository cloning.
    """
    def __init__(self):
        """Initialize the progress tracker."""
        self.current_operation = ""
        self.current_progress = 0
        self.total_progress = 100
        self.is_complete = False
    
    def update(self, op_code: int, cur_count: int, max_count: Optional[int] = None,
               message: str = '') -> Tuple[str, int]:
        """
        Update progress based on Git operation.
        
        Args:
            op_code: Git operation code
            cur_count: Current progress count
            max_count: Maximum progress count
            message: Progress message
            
        Returns:
            Tuple of (current_operation, percentage)
        """
        self.current_operation = message or "Processing git data"
        self.current_progress = cur_count
        
        if max_count:
            self.total_progress = max_count
            self.current_progress = min(cur_count, max_count)
        
        # Calculate percentage (0-100)
        if self.total_progress > 0:
            percentage = int((self.current_progress / self.total_progress) * 100)
        else:
            percentage = 0
            
        # Mark as complete when reaching 100%
        if percentage >= 100:
            self.is_complete = True
            
        return self.current_operation, percentage


def clone_repository(
    url: str,
    clone_dir: str,
    branch: Optional[str] = None,
    progress_tracker: Optional[ProgressTracker] = None
) -> str:
    """
    Clone a GitHub repository to a local directory.
    
    Args:
        url: The GitHub repository URL
        clone_dir: The directory to clone into
        branch: The branch to clone (optional)
        progress_tracker: Object to track progress (optional)
        
    Returns:
        Path to the cloned repository
        
    Raises:
        Exception: If the cloning fails
    """
    # Extract repository info from URL
    owner, repo, url_branch = extract_repo_info(url)
    
    # Use branch from URL if not explicitly specified
    if not branch and url_branch:
        branch = url_branch
    
    # Create target directory name
    repo_dir_name = f"{owner}_{repo}"
    repo_path = os.path.join(clone_dir, repo_dir_name)
    
    # Prepare clone options
    clone_opts = {}
    if branch:
        clone_opts['branch'] = branch
    
    if progress_tracker:
        clone_opts['progress'] = progress_tracker.update
    
    try:
        # Clone the repository
        git.Repo.clone_from(url, repo_path, **clone_opts)
        return repo_path
    except Exception as e:
        # Cleanup if directory was created
        if os.path.exists(repo_path):
            try:
                shutil.rmtree(repo_path)
            except:
                pass  # Ignore cleanup errors
        
        # Re-raise the exception with more context
        raise Exception(f"Failed to clone repository: {str(e)}") 