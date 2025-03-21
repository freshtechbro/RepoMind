"""
Tree structure conversion module for RepoMind.

This module provides functions to convert between different tree representation formats:
- DirectoryNode (from directory_scanner) to CollapsibleTree
- CollapsibleTree to frontend-compatible JSON format
- Dependency graph to visualization-compatible format
"""

import os
import uuid
from typing import Dict, List, Any, Optional

from app.structure.directory_scanner import DirectoryNode, FileNode, scan_directory
from app.structure.collapsible_tree import TreeNode, CollapsibleTree, build_tree_from_directory_node
from app.structure.dependency_analyzer import analyze_dependencies
from app.structure.file_type_detector import FileTypeDetector, FileType


def convert_directory_to_collapsible_tree(directory_node: DirectoryNode) -> CollapsibleTree:
    """
    Convert a DirectoryNode tree to a CollapsibleTree.
    
    Args:
        directory_node: The root DirectoryNode
        
    Returns:
        CollapsibleTree: A collapsible tree representation
    """
    return build_tree_from_directory_node(directory_node)


def convert_to_frontend_tree(collapsible_tree: CollapsibleTree) -> Dict[str, Any]:
    """
    Convert a CollapsibleTree to a frontend-compatible tree structure.
    
    Args:
        collapsible_tree: The CollapsibleTree to convert
        
    Returns:
        Dict: A JSON-serializable tree structure for the frontend
    """
    file_detector = FileTypeDetector()
    return _convert_node_to_frontend_format(collapsible_tree.root, file_detector)


def _convert_node_to_frontend_format(node: TreeNode, file_detector: FileTypeDetector) -> Dict[str, Any]:
    """
    Convert a TreeNode to frontend-compatible format recursively.
    
    Args:
        node: The TreeNode to convert
        file_detector: FileTypeDetector instance for file type information
        
    Returns:
        Dict: A JSON-serializable node representation
    """
    # Generate a unique ID for the node
    node_id = str(uuid.uuid4())
    
    # Create base node representation
    frontend_node = {
        "id": node_id,
        "name": node.name,
        "path": node.path,
        "type": "directory" if node.is_directory else "file"
    }
    
    # Add file-specific properties
    if not node.is_directory:
        # Get file extension
        extension = os.path.splitext(node.name)[1]
        frontend_node["extension"] = extension
        
        # Add file size if available
        if "size" in node.metadata:
            frontend_node["size"] = node.metadata["size"]
        
        try:
            # Detect file type and add icon information
            file_type = file_detector.detect_file_type(node.path)
            frontend_node["fileType"] = file_type.name.lower()
            frontend_node["icon"] = file_detector.get_icon_for_file_type(file_type)
        except:
            # If file doesn't exist or can't be accessed
            frontend_node["fileType"] = "unknown"
            frontend_node["icon"] = "file-icon"
    
    # Add children for directories
    if node.is_directory and node.children:
        frontend_node["children"] = [
            _convert_node_to_frontend_format(child, file_detector) 
            for child in node.children
        ]
    
    return frontend_node


def create_file_structure_tree(repo_path: str, exclude_dirs: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Create a complete file structure tree for a repository path.
    
    Args:
        repo_path: Path to the repository root
        exclude_dirs: List of directories to exclude
        
    Returns:
        Dict: A JSON-serializable tree structure for the frontend
    """
    # Scan the directory
    directory_tree = scan_directory(repo_path, exclude_dirs)
    
    # Convert to collapsible tree
    collapsible_tree = convert_directory_to_collapsible_tree(directory_tree)
    
    # Convert to frontend format
    return convert_to_frontend_tree(collapsible_tree)


def create_dependency_visualization(repo_path: str) -> Dict[str, Any]:
    """
    Create a dependency visualization data structure for a repository.
    
    Args:
        repo_path: Path to the repository root
        
    Returns:
        Dict: A JSON-serializable graph structure for visualization
    """
    # Analyze dependencies
    dependency_graph = analyze_dependencies(repo_path)
    
    # Create nodes list
    nodes = []
    for path, dep_node in dependency_graph.nodes.items():
        node = {
            "id": path,
            "name": dep_node.name,
            "path": path,
            "type": dep_node.file_type
        }
        nodes.append(node)
    
    # Create edges list
    edges = []
    for path, dep_node in dependency_graph.nodes.items():
        for dependency in dep_node.dependencies:
            edge = {
                "source": path,
                "target": dependency.path,
                "type": "dependency"
            }
            edges.append(edge)
    
    # Return the visualization data
    return {
        "nodes": nodes,
        "edges": edges
    }


def get_file_structure_stats(repo_path: str) -> Dict[str, Any]:
    """
    Get statistics about the file structure of a repository.
    
    Args:
        repo_path: Path to the repository root
        
    Returns:
        Dict: Statistics about the repository file structure
    """
    from app.structure.directory_scanner import get_file_stats
    
    # Scan the directory
    directory_tree = scan_directory(repo_path)
    
    # Get statistics
    stats = get_file_stats(directory_tree)
    
    # Add some additional insights
    stats["directory_count"] = len([
        node for node in directory_tree.get_all_files_recursive()
        if hasattr(node, "node_type") and node.node_type == "directory"
    ])
    
    # Return the statistics
    return stats 