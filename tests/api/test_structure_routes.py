"""
Tests for the structure API routes.
"""
import os
import pytest
from unittest import mock
from fastapi.testclient import TestClient

from app.main import app
from app.structure.directory_scanner import DirectoryNode, FileNode


client = TestClient(app)


@pytest.fixture
def mock_create_file_structure_tree():
    with mock.patch("app.api.routes.structure.create_file_structure_tree") as mock_create:
        # Create a mock tree structure
        mock_tree = {
            "id": "1",
            "name": "repo",
            "type": "directory",
            "path": "/repo",
            "children": [
                {
                    "id": "2",
                    "name": "src",
                    "type": "directory",
                    "path": "/repo/src",
                    "children": [
                        {
                            "id": "3",
                            "name": "file1.py",
                            "type": "file",
                            "path": "/repo/src/file1.py",
                            "extension": ".py",
                            "size": 1024,
                            "fileType": "python",
                            "icon": "python-icon"
                        },
                        {
                            "id": "4",
                            "name": "file2.py",
                            "type": "file",
                            "path": "/repo/src/file2.py",
                            "extension": ".py",
                            "size": 2048,
                            "fileType": "python",
                            "icon": "python-icon"
                        }
                    ]
                },
                {
                    "id": "5",
                    "name": "tests",
                    "type": "directory",
                    "path": "/repo/tests",
                    "children": [
                        {
                            "id": "6",
                            "name": "test_file.py",
                            "type": "file",
                            "path": "/repo/tests/test_file.py",
                            "extension": ".py",
                            "size": 512,
                            "fileType": "python",
                            "icon": "python-icon"
                        }
                    ]
                }
            ]
        }
        
        mock_create.return_value = mock_tree
        yield mock_create


@pytest.fixture
def mock_get_file_structure_stats():
    with mock.patch("app.api.routes.structure.get_file_structure_stats") as mock_stats:
        # Create mock stats
        mock_stats.return_value = {
            "total_files": 3,
            "total_size": 3584,  # 1024 + 2048 + 512
            "files_by_type": {
                "python": 3
            },
            "files_by_extension": {
                ".py": 3
            },
            "largest_files": [
                ("/repo/src/file2.py", 2048),
                ("/repo/src/file1.py", 1024),
                ("/repo/tests/test_file.py", 512)
            ],
            "directory_count": 2
        }
        yield mock_stats


@pytest.fixture
def mock_create_dependency_visualization():
    with mock.patch("app.api.routes.structure.create_dependency_visualization") as mock_deps:
        # Create mock dependency visualization
        mock_deps.return_value = {
            "nodes": [
                {
                    "id": "/repo/src/file1.py",
                    "name": "file1.py",
                    "path": "/repo/src/file1.py",
                    "type": "python"
                },
                {
                    "id": "/repo/src/file2.py",
                    "name": "file2.py",
                    "path": "/repo/src/file2.py",
                    "type": "python"
                },
                {
                    "id": "/repo/tests/test_file.py",
                    "name": "test_file.py",
                    "path": "/repo/tests/test_file.py",
                    "type": "python"
                }
            ],
            "edges": [
                {
                    "source": "/repo/src/file2.py",
                    "target": "/repo/src/file1.py",
                    "type": "dependency"
                },
                {
                    "source": "/repo/tests/test_file.py",
                    "target": "/repo/src/file1.py",
                    "type": "dependency"
                }
            ]
        }
        yield mock_deps


@pytest.fixture
def mock_analyze_dependencies():
    with mock.patch("app.api.routes.structure.analyze_dependencies") as mock_analyze:
        # Create a mock dependency graph
        mock_graph = mock.MagicMock()
        mock_graph.find_circular_dependencies.return_value = []
        
        mock_analyze.return_value = mock_graph
        yield mock_analyze


def test_get_repository_structure(mock_create_file_structure_tree, mock_get_file_structure_stats):
    """Test the repository structure endpoint."""
    response = client.get("/structure/tree/test-repo")
    assert response.status_code == 200
    
    data = response.json()
    assert "tree" in data
    assert "stats" in data
    
    # Check tree structure
    tree = data["tree"]
    assert tree["name"] == "repo"
    assert tree["type"] == "directory"
    
    # Check children
    assert len(tree["children"]) == 2
    
    # Check src directory
    src_dir = next(child for child in tree["children"] if child["name"] == "src")
    assert src_dir["type"] == "directory"
    assert len(src_dir["children"]) == 2
    
    # Check file properties
    file1 = next(child for child in src_dir["children"] if child["name"] == "file1.py")
    assert file1["type"] == "file"
    assert file1["extension"] == ".py"
    assert file1["size"] == 1024
    assert file1["fileType"] == "python"
    assert file1["icon"] == "python-icon"


def test_get_repository_structure_with_exclude_dirs(mock_create_file_structure_tree, mock_get_file_structure_stats):
    """Test the repository structure endpoint with exclude_dirs parameter."""
    response = client.get("/structure/tree/test-repo?exclude_dirs=tests&exclude_dirs=.git")
    assert response.status_code == 200
    
    # Verify that exclude_dirs was passed to create_file_structure_tree
    mock_create_file_structure_tree.assert_called_once()
    args, kwargs = mock_create_file_structure_tree.call_args
    assert kwargs.get("exclude_dirs") == ["tests", ".git"]


def test_get_repository_dependencies(mock_create_dependency_visualization, mock_analyze_dependencies):
    """Test the repository dependencies endpoint."""
    response = client.get("/structure/dependencies/test-repo")
    assert response.status_code == 200
    
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert "stats" in data
    
    # Check nodes
    assert len(data["nodes"]) == 3
    
    # Check edges
    assert len(data["edges"]) == 2
    
    # Check edge directions
    edges = data["edges"]
    # file2 -> file1
    assert any(edge["source"].endswith("file2.py") and edge["target"].endswith("file1.py") for edge in edges)
    # test_file -> file1
    assert any(edge["source"].endswith("test_file.py") and edge["target"].endswith("file1.py") for edge in edges)


def test_get_repository_dependencies_with_exclude_dirs(mock_create_dependency_visualization, mock_analyze_dependencies):
    """Test the repository dependencies endpoint with exclude_dirs parameter."""
    response = client.get("/structure/dependencies/test-repo?exclude_dirs=tests&exclude_dirs=.git")
    assert response.status_code == 200


def test_get_file_type_distribution(mock_get_file_structure_stats):
    """Test the file type distribution endpoint."""
    response = client.get("/structure/file-types/test-repo")
    assert response.status_code == 200
    
    data = response.json()
    assert "file_types" in data
    assert "extensions" in data
    assert "total_files" in data
    assert "total_size" in data
    assert "largest_files" in data
    
    # Check specific values
    assert data["total_files"] == 3
    assert data["total_size"] == 3584
    assert data["file_types"]["python"] == 3
    assert data["extensions"][".py"] == 3
    assert len(data["largest_files"]) == 3


def test_search_repository_files(mock_create_file_structure_tree):
    """Test the search repository files endpoint."""
    response = client.get("/structure/search/test-repo?query=file1")
    assert response.status_code == 200
    
    data = response.json()
    assert "results" in data
    assert "count" in data
    
    # Check that we got the correct file
    assert data["count"] == 1
    assert data["results"][0]["name"] == "file1.py"
    
    # Test with a query that matches multiple files
    response = client.get("/structure/search/test-repo?query=.py")
    data = response.json()
    assert data["count"] == 3  # All three Python files
    
    # Test with a query that matches no files
    response = client.get("/structure/search/test-repo?query=nonexistent")
    data = response.json()
    assert data["count"] == 0
    assert len(data["results"]) == 0 