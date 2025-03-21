"""
Tests for the repositories API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "name" in response.json()
    assert "version" in response.json()
    assert "documentation" in response.json()

def test_validate_repository_valid_url():
    """Test repository URL validation with a valid URL."""
    response = client.post(
        "/repositories/validate",
        json={"url": "https://github.com/username/repo"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["owner"] == "username"
    assert data["name"] == "repo"
    assert data["url"] == "https://github.com/username/repo"

def test_validate_repository_invalid_url():
    """Test repository URL validation with an invalid URL."""
    response = client.post(
        "/repositories/validate",
        json={"url": "https://example.com/not-github"}
    )
    assert response.status_code == 422  # Validation error

def test_clone_repository():
    """Test repository cloning endpoint."""
    # Mock extract_repo_info to avoid actual validation
    with patch('app.github.url_validator.extract_repo_info') as mock_extract_info:
        mock_extract_info.return_value = ("username", "repo", None)
        
        # Mock the background task
        with patch('app.api.routes.repositories.BackgroundTasks.add_task') as mock_add_task:
            response = client.post(
                "/repositories/clone",
                json={"url": "https://github.com/username/repo"}
            )
            
            # Verify response
            assert response.status_code == 202
            data = response.json()
            assert "task_id" in data
            assert data["repository"]["owner"] == "username"
            assert data["repository"]["name"] == "repo"
            
            # Verify background task was added
            mock_add_task.assert_called_once()

def test_clone_repository_with_branch():
    """Test repository cloning with a specified branch."""
    # Mock extract_repo_info to avoid actual validation
    with patch('app.github.url_validator.extract_repo_info') as mock_extract_info:
        mock_extract_info.return_value = ("username", "repo", None)
        
        # Mock the background task
        with patch('app.api.routes.repositories.BackgroundTasks.add_task') as mock_add_task:
            response = client.post(
                "/repositories/clone",
                json={"url": "https://github.com/username/repo", "branch": "feature-branch"}
            )
            
            # Verify response
            assert response.status_code == 202
            data = response.json()
            assert data["repository"]["branch"] == "feature-branch"
            
            # Verify background task was added
            mock_add_task.assert_called_once()
            
            # Get call arguments and check that branch is included
            call_args = mock_add_task.call_args[0]
            # First parameter should be the task function
            # Second parameter should be task_id
            # Third parameter should be URL
            # Fourth parameter should be branch
            assert len(call_args) >= 4  # Make sure we have enough parameters
            assert call_args[3] == "feature-branch"  # Branch should be the fourth parameter

def test_get_clone_status_not_found():
    """Test getting clone status for a non-existent task."""
    response = client.get("/repositories/clone/non-existent-task")
    assert response.status_code == 404

def test_get_clone_status_found():
    """Test getting clone status for an existing task."""
    # Add a mock task to the clone_tasks dictionary
    test_task_id = "test-task-id"
    with patch('app.api.routes.repositories.clone_tasks', {
        test_task_id: {
            "status": "in_progress",
            "progress": 50,
            "operation": "Downloading objects"
        }
    }):
        response = client.get(f"/repositories/clone/{test_task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"
        assert data["progress"] == 50 