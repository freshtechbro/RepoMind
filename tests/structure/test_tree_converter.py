"""
Tests for tree structure conversion functionality.
"""
import unittest
from unittest.mock import MagicMock, patch
from app.structure.directory_scanner import DirectoryNode, FileNode
from app.structure.collapsible_tree import TreeNode
from app.structure.tree_converter import (
    convert_directory_to_collapsible_tree,
    convert_to_frontend_tree,
    create_dependency_visualization
)


class TestTreeConverter:
    """Tests for tree structure conversion functionality."""
    
    def setup_mock_directory_tree(self):
        """Create a mock directory tree for testing."""
        # Create a simple directory tree
        root = DirectoryNode("project", "/path/to/project")
        
        # Add first-level directories and files
        src_dir = DirectoryNode("src", "/path/to/project/src")
        docs_dir = DirectoryNode("docs", "/path/to/project/docs")
        readme_file = FileNode("README.md", "/path/to/project/README.md", {"size": 1024})
        
        root.add_child(src_dir)
        root.add_child(docs_dir)
        root.add_child(readme_file)
        
        # Add files to src directory
        main_py = FileNode("main.py", "/path/to/project/src/main.py", {"size": 2048})
        utils_py = FileNode("utils.py", "/path/to/project/src/utils.py", {"size": 3072})
        
        src_dir.add_child(main_py)
        src_dir.add_child(utils_py)
        
        # Add files to docs directory
        index_md = FileNode("index.md", "/path/to/project/docs/index.md", {"size": 512})
        
        docs_dir.add_child(index_md)
        
        return root
    
    def test_convert_directory_to_collapsible_tree(self):
        """Test conversion from DirectoryNode to CollapsibleTree."""
        # Setup
        dir_tree = self.setup_mock_directory_tree()
        
        # Execute
        collapsible_tree = convert_directory_to_collapsible_tree(dir_tree)
        
        # Verify
        assert collapsible_tree.root.name == "project"
        assert collapsible_tree.root.path == "/path/to/project"
        assert collapsible_tree.root.is_directory == True
        
        # Check children structure is preserved
        root_node = collapsible_tree.root
        assert len(root_node.children) == 3
        
        # Get children by name
        src_node = next((node for node in root_node.children if node.name == "src"), None)
        docs_node = next((node for node in root_node.children if node.name == "docs"), None)
        readme_node = next((node for node in root_node.children if node.name == "README.md"), None)
        
        assert src_node is not None
        assert docs_node is not None
        assert readme_node is not None
        
        # Check node types
        assert src_node.is_directory == True
        assert docs_node.is_directory == True
        assert readme_node.is_directory == False
        
        # Check src children
        assert len(src_node.children) == 2
        main_py_node = next((node for node in src_node.children if node.name == "main.py"), None)
        utils_py_node = next((node for node in src_node.children if node.name == "utils.py"), None)
        
        assert main_py_node is not None
        assert utils_py_node is not None
        
        # Check metadata is preserved
        assert readme_node.metadata["size"] == 1024
        assert main_py_node.metadata["size"] == 2048
    
    def test_convert_to_frontend_tree(self):
        """Test conversion from CollapsibleTree to frontend tree structure."""
        # Setup 
        dir_tree = self.setup_mock_directory_tree()
        collapsible_tree = convert_directory_to_collapsible_tree(dir_tree)
        
        # Mock file type detector
        mock_detector = MagicMock()
        mock_detector.detect_file_type.return_value = "python"
        mock_detector.get_icon_for_file_type.return_value = "python-icon"
        
        # Execute
        with patch("app.structure.tree_converter.FileTypeDetector", return_value=mock_detector):
            frontend_tree = convert_to_frontend_tree(collapsible_tree)
        
        # Verify
        assert frontend_tree["id"] is not None
        assert frontend_tree["name"] == "project"
        assert frontend_tree["type"] == "directory"
        assert frontend_tree["path"] == "/path/to/project"
        assert "children" in frontend_tree
        assert len(frontend_tree["children"]) == 3
        
        # Check src directory
        src_node = next((node for node in frontend_tree["children"] if node["name"] == "src"), None)
        assert src_node is not None
        assert src_node["type"] == "directory"
        assert len(src_node["children"]) == 2
        
        # Check README.md file
        readme_node = next((node for node in frontend_tree["children"] if node["name"] == "README.md"), None)
        assert readme_node is not None
        assert readme_node["type"] == "file"
        assert readme_node["size"] == 1024
        assert "children" not in readme_node
    
    def test_create_dependency_visualization(self):
        """Test creation of dependency visualization tree."""
        # Setup
        mock_dependency_graph = MagicMock()
        
        # Create mock nodes
        main_node = MagicMock()
        main_node.path = "src/main.py"
        main_node.name = "main.py"
        main_node.file_type = "python"
        main_node.dependencies = []
        
        utils_node = MagicMock()
        utils_node.path = "src/utils.py"
        utils_node.name = "utils.py"
        utils_node.file_type = "python"
        utils_node.dependencies = []
        
        # Create dependency relationship
        main_node.dependencies = [utils_node]
        
        # Setup mock graph
        mock_dependency_graph.nodes = {
            "src/main.py": main_node,
            "src/utils.py": utils_node
        }
        
        # Execute
        with patch("app.structure.tree_converter.analyze_dependencies", 
                  return_value=mock_dependency_graph):
            dep_tree = create_dependency_visualization("/path/to/repo")
        
        # Verify
        assert dep_tree is not None
        assert "nodes" in dep_tree
        assert "edges" in dep_tree
        assert len(dep_tree["nodes"]) == 2
        assert len(dep_tree["edges"]) == 1
        
        # Verify nodes have correct format
        node_ids = [node["id"] for node in dep_tree["nodes"]]
        assert "src/main.py" in node_ids
        assert "src/utils.py" in node_ids
        
        # Verify edge exists from main to utils
        edge = dep_tree["edges"][0]
        assert edge["source"] == "src/main.py"
        assert edge["target"] == "src/utils.py" 