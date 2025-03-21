"""
Tests for the repository cloner module.
"""

import os
import shutil
import pytest
from unittest.mock import patch, MagicMock

from app.github.repository_cloner import clone_repository, ProgressTracker


@pytest.fixture
def temp_clone_dir(tmp_path):
    """
    Fixture to create a temporary directory for cloning repositories.
    """
    clone_dir = tmp_path / "test_clone_dir"
    clone_dir.mkdir()
    yield str(clone_dir)
    shutil.rmtree(str(clone_dir), ignore_errors=True)


def test_progress_tracker_update():
    """Test the ProgressTracker update method."""
    tracker = ProgressTracker()
    
    # Test with count and max_count
    operation, percentage = tracker.update(1, 50, 100, "Downloading")
    assert operation == "Downloading"
    assert percentage == 50
    assert tracker.current_progress == 50
    assert tracker.total_progress == 100
    assert not tracker.is_complete
    
    # Test completion
    operation, percentage = tracker.update(1, 100, 100, "Finalizing")
    assert operation == "Finalizing"
    assert percentage == 100
    assert tracker.is_complete


def test_clone_repository_success(temp_clone_dir):
    """Test successful repository cloning."""
    url = "https://github.com/username/repo"
    
    # Mock git.Repo.clone_from to avoid actual cloning
    with patch('git.Repo.clone_from') as mock_clone_from:
        mock_repo = MagicMock()
        mock_clone_from.return_value = mock_repo
        
        # Call the function
        result = clone_repository(url, temp_clone_dir)
        
        # Verify clone was called with correct parameters
        mock_clone_from.assert_called_once()
        call_args = mock_clone_from.call_args[0]
        assert call_args[0] == url
        assert os.path.join(temp_clone_dir, "username_repo") in call_args[1]
        
        # Verify result is the path to the cloned repository
        assert os.path.join(temp_clone_dir, "username_repo") in result


def test_clone_repository_with_branch(temp_clone_dir):
    """Test repository cloning with a specific branch."""
    url = "https://github.com/username/repo"
    branch = "feature-branch"
    
    with patch('git.Repo.clone_from') as mock_clone_from:
        mock_repo = MagicMock()
        mock_clone_from.return_value = mock_repo
        
        # Call the function with branch
        result = clone_repository(url, temp_clone_dir, branch=branch)
        
        # Verify clone was called with correct branch
        mock_clone_from.assert_called_once()
        call_kwargs = mock_clone_from.call_args[1]
        assert call_kwargs.get('branch') == branch


def test_clone_repository_with_progress_tracker(temp_clone_dir):
    """Test repository cloning with progress tracking."""
    url = "https://github.com/username/repo"
    tracker = ProgressTracker()
    
    with patch('git.Repo.clone_from') as mock_clone_from:
        mock_repo = MagicMock()
        mock_clone_from.return_value = mock_repo
        
        # Call the function with progress tracker
        result = clone_repository(url, temp_clone_dir, progress_tracker=tracker)
        
        # Verify progress tracker was used
        mock_clone_from.assert_called_once()
        call_kwargs = mock_clone_from.call_args[1]
        assert 'progress' in call_kwargs


def test_clone_repository_failure(temp_clone_dir):
    """Test handling of repository cloning failure."""
    url = "https://github.com/username/repo"
    
    with patch('git.Repo.clone_from') as mock_clone_from:
        # Set up the mock to raise an exception
        mock_clone_from.side_effect = Exception("Clone failed")
        
        # Test that the exception is properly handled and re-raised
        with pytest.raises(Exception) as exc_info:
            clone_repository(url, temp_clone_dir)
        
        assert "Failed to clone repository" in str(exc_info.value) 