"""
Module for scanning and analyzing repository directory structures.

Provides functionality to scan directories recursively, collect file metadata,
and build a hierarchical representation of the repository structure.
"""
import os
import pathlib
from typing import Dict, List, Any, Optional, Set


class FileNode:
    """
    Represents a file in the repository structure.
    
    Attributes:
        name: Name of the file
        path: Absolute path to the file
        metadata: Dictionary of file metadata (size, modified time, etc.)
    """
    
    def __init__(self, name: str, path: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a FileNode.
        
        Args:
            name: Name of the file
            path: Absolute path to the file
            metadata: Optional dictionary of file metadata
        """
        self.name = name
        self.path = path
        self.metadata = metadata or {}
        self.node_type = 'file'
        
    def get_extension(self) -> str:
        """
        Get the file extension.
        
        Returns:
            File extension with leading dot (e.g., '.py')
        """
        return pathlib.Path(self.name).suffix
        
    def get_type(self) -> str:
        """
        Get the file type based on extension.
        
        Returns:
            File type as a string (e.g., 'python', 'javascript', etc.)
        """
        extension = self.get_extension()
        
        # Map extensions to file types
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.json': 'json',
            '.md': 'markdown',
            '.yml': 'yaml',
            '.yaml': 'yaml',
            '.xml': 'xml',
            '.sql': 'sql',
            '.java': 'java',
            '.c': 'c',
            '.cpp': 'cpp',
            '.h': 'c-header',
            '.hpp': 'cpp-header',
            '.go': 'go',
            '.rb': 'ruby',
            '.php': 'php',
        }
        
        return extension_map.get(extension.lower(), 'text')


class DirectoryNode:
    """
    Represents a directory in the repository structure.
    
    Attributes:
        name: Name of the directory
        path: Absolute path to the directory
        children: List of child nodes (files and directories)
    """
    
    def __init__(self, name: str, path: str):
        """
        Initialize a DirectoryNode.
        
        Args:
            name: Name of the directory
            path: Absolute path to the directory
        """
        self.name = name
        self.path = path
        self.children = []
        self.node_type = 'directory'
        
    def add_child(self, node: Any) -> None:
        """
        Add a child node (file or directory) to this directory.
        
        Args:
            node: FileNode or DirectoryNode to add as a child
        """
        self.children.append(node)
        
    def get_files(self) -> List[FileNode]:
        """
        Get all file nodes in this directory (not recursive).
        
        Returns:
            List of FileNode objects
        """
        return [child for child in self.children if isinstance(child, FileNode)]
        
    def get_directories(self) -> List['DirectoryNode']:
        """
        Get all directory nodes in this directory (not recursive).
        
        Returns:
            List of DirectoryNode objects
        """
        return [child for child in self.children if isinstance(child, DirectoryNode)]
        
    def get_all_files_recursive(self) -> List[FileNode]:
        """
        Get all file nodes in this directory and its subdirectories.
        
        Returns:
            List of FileNode objects
        """
        files = self.get_files()
        
        for directory in self.get_directories():
            files.extend(directory.get_all_files_recursive())
            
        return files


def scan_directory(root_path: str, exclude_dirs: Optional[List[str]] = None) -> DirectoryNode:
    """
    Scan a directory recursively and build a tree structure.
    
    Args:
        root_path: Path to the root directory to scan
        exclude_dirs: List of directory names to exclude (e.g., 'node_modules', '.git')
        
    Returns:
        DirectoryNode: Root node of the directory tree
    """
    if exclude_dirs is None:
        exclude_dirs = ['node_modules', '.git', '__pycache__', '.next', 'dist', 'build']
    
    # Normalize the root path
    root_path = os.path.abspath(root_path)
    
    # Create the root directory node
    root_name = os.path.basename(root_path)
    root_node = DirectoryNode(root_name, root_path)
    
    # Dictionary to keep track of directory nodes by path
    dir_nodes = {root_path: root_node}
    
    # Walk the directory tree
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Get the current directory node
        current_dir_node = dir_nodes[dirpath]
        
        # Filter out excluded directories
        dirnames_filtered = [d for d in dirnames if d not in exclude_dirs]
        # This modifies dirnames in-place to prevent os.walk from traversing excluded dirs
        dirnames[:] = dirnames_filtered
        
        # Add subdirectories
        for dirname in dirnames:
            dir_full_path = os.path.join(dirpath, dirname)
            dir_node = DirectoryNode(dirname, dir_full_path)
            current_dir_node.add_child(dir_node)
            dir_nodes[dir_full_path] = dir_node
        
        # Add files
        for filename in filenames:
            file_full_path = os.path.join(dirpath, filename)
            
            # Collect file metadata
            metadata = {}
            try:
                file_stat = os.stat(file_full_path)
                metadata['size'] = file_stat.st_size
                metadata['modified'] = file_stat.st_mtime
                metadata['created'] = file_stat.st_ctime
            except (FileNotFoundError, PermissionError):
                # Skip files that can't be accessed
                continue
                
            # Create and add the file node
            file_node = FileNode(filename, file_full_path, metadata)
            current_dir_node.add_child(file_node)
    
    return root_node


def get_file_stats(directory_node: DirectoryNode) -> Dict[str, Any]:
    """
    Get statistics about the files in a directory tree.
    
    Args:
        directory_node: Root of the directory tree
        
    Returns:
        Dict with statistics (file count by type, total size, etc.)
    """
    stats = {
        'total_files': 0,
        'total_size': 0,
        'files_by_type': {},
        'files_by_extension': {},
        'largest_files': []
    }
    
    # Process all files recursively
    all_files = directory_node.get_all_files_recursive()
    stats['total_files'] = len(all_files)
    
    for file_node in all_files:
        # Accumulate size
        file_size = file_node.metadata.get('size', 0)
        stats['total_size'] += file_size
        
        # Count by type
        file_type = file_node.get_type()
        stats['files_by_type'][file_type] = stats['files_by_type'].get(file_type, 0) + 1
        
        # Count by extension
        extension = file_node.get_extension()
        stats['files_by_extension'][extension] = stats['files_by_extension'].get(extension, 0) + 1
        
        # Track largest files
        if len(stats['largest_files']) < 10:
            stats['largest_files'].append((file_node.path, file_size))
            # Sort by size (largest first)
            stats['largest_files'].sort(key=lambda x: x[1], reverse=True)
        elif file_size > stats['largest_files'][-1][1]:
            stats['largest_files'].pop()
            stats['largest_files'].append((file_node.path, file_size))
            stats['largest_files'].sort(key=lambda x: x[1], reverse=True)
    
    return stats 