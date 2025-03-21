"""
Tests for repository directory structure scanning.
"""
import os
import tempfile
import unittest.mock as mock
import pytest
from app.structure.directory_scanner import scan_directory, FileNode, DirectoryNode


class TestDirectoryScanner:
    """Tests for directory structure scanning functionality."""

    def test_empty_directory_scan(self):
        """Test scanning an empty directory."""
        with mock.patch('os.walk') as mock_walk:
            mock_walk.return_value = [
                ('/root', [], [])
            ]
            
            result = scan_directory('/root')
            
            assert isinstance(result, DirectoryNode)
            assert result.name == 'root'
            assert len(result.children) == 0

    def test_directory_with_files_scan(self):
        """Test scanning a directory containing only files."""
        with mock.patch('os.walk') as mock_walk:
            mock_walk.return_value = [
                ('/root', [], ['file1.py', 'file2.js'])
            ]
            
            result = scan_directory('/root')
            
            assert isinstance(result, DirectoryNode)
            assert result.name == 'root'
            assert len(result.children) == 2
            
            # Check file nodes
            file_names = [node.name for node in result.children]
            assert 'file1.py' in file_names
            assert 'file2.js' in file_names

    def test_nested_directories_scan(self):
        """Test scanning directories with nested structure."""
        with mock.patch('os.walk') as mock_walk:
            mock_walk.return_value = [
                ('/root', ['dir1', 'dir2'], ['file1.py']),
                ('/root/dir1', [], ['file2.js']),
                ('/root/dir2', [], ['file3.py'])
            ]
            
            result = scan_directory('/root')
            
            assert isinstance(result, DirectoryNode)
            assert result.name == 'root'
            assert len(result.children) == 3
            
            # Check for directories and root file
            dir_nodes = [node for node in result.children if isinstance(node, DirectoryNode)]
            file_nodes = [node for node in result.children if isinstance(node, FileNode)]
            
            assert len(dir_nodes) == 2
            assert len(file_nodes) == 1
            
            dir_names = [node.name for node in dir_nodes]
            assert 'dir1' in dir_names
            assert 'dir2' in dir_names
            
            assert file_nodes[0].name == 'file1.py'
            
            # Check nested files
            dir1 = next(node for node in dir_nodes if node.name == 'dir1')
            dir2 = next(node for node in dir_nodes if node.name == 'dir2')
            
            assert len(dir1.children) == 1
            assert dir1.children[0].name == 'file2.js'
            
            assert len(dir2.children) == 1
            assert dir2.children[0].name == 'file3.py'

    def test_file_metadata_collection(self):
        """Test metadata is collected for files."""
        mock_stat = mock.Mock()
        mock_stat.st_size = 1024
        mock_stat.st_mtime = 1600000000
        
        with mock.patch('os.walk') as mock_walk, \
             mock.patch('os.stat', return_value=mock_stat):
            mock_walk.return_value = [
                ('/root', [], ['file1.py'])
            ]
            
            result = scan_directory('/root')
            
            assert len(result.children) == 1
            file_node = result.children[0]
            
            assert file_node.metadata['size'] == 1024
            assert file_node.metadata['modified'] == 1600000000

    def test_file_type_detection(self):
        """Test file type detection based on extensions."""
        with mock.patch('os.walk') as mock_walk:
            mock_walk.return_value = [
                ('/root', [], ['file1.py', 'file2.js', 'file3.ts', 'file4.jsx', 'file5.tsx', 'file6.txt'])
            ]
            
            result = scan_directory('/root')
            
            file_nodes = result.children
            assert len(file_nodes) == 6
            
            # Check extensions are correctly identified
            extensions = [node.get_extension() for node in file_nodes]
            assert '.py' in extensions
            assert '.js' in extensions
            assert '.ts' in extensions
            assert '.jsx' in extensions
            assert '.tsx' in extensions
            assert '.txt' in extensions
            
            # Check file types are correctly identified
            python_file = next(node for node in file_nodes if node.name == 'file1.py')
            js_file = next(node for node in file_nodes if node.name == 'file2.js')
            ts_file = next(node for node in file_nodes if node.name == 'file3.ts')
            
            assert python_file.get_type() == 'python'
            assert js_file.get_type() == 'javascript'
            assert ts_file.get_type() == 'typescript'

    def test_ignores_excluded_directories(self):
        """Test that excluded directories are ignored during scanning."""
        with mock.patch('os.walk') as mock_walk:
            mock_walk.return_value = [
                ('/root', ['node_modules', 'dir1', '.git'], ['file1.py']),
                ('/root/dir1', [], ['file2.js']),
                ('/root/node_modules', ['subdir'], ['package.json']),
                ('/root/.git', [], ['config'])
            ]
            
            result = scan_directory('/root', exclude_dirs=['node_modules', '.git'])
            
            # Should only have dir1 and file1.py
            assert len(result.children) == 2
            
            dir_names = [node.name for node in result.children if isinstance(node, DirectoryNode)]
            assert 'dir1' in dir_names
            assert 'node_modules' not in dir_names
            assert '.git' not in dir_names

    def test_real_directory_scanning(self):
        """Test scanning an actual temporary directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a simple directory structure
            os.makedirs(os.path.join(temp_dir, 'dir1'))
            os.makedirs(os.path.join(temp_dir, 'dir2'))
            
            with open(os.path.join(temp_dir, 'file1.py'), 'w') as f:
                f.write('print("Hello")')
                
            with open(os.path.join(temp_dir, 'dir1', 'file2.js'), 'w') as f:
                f.write('console.log("Hello")')
            
            # Scan the directory
            result = scan_directory(temp_dir)
            
            # Verify structure
            assert isinstance(result, DirectoryNode)
            assert len(result.children) == 3
            
            dir_names = [node.name for node in result.children if isinstance(node, DirectoryNode)]
            file_names = [node.name for node in result.children if isinstance(node, FileNode)]
            
            assert 'dir1' in dir_names
            assert 'dir2' in dir_names
            assert 'file1.py' in file_names
            
            dir1 = next(node for node in result.children 
                       if isinstance(node, DirectoryNode) and node.name == 'dir1')
            assert len(dir1.children) == 1
            assert dir1.children[0].name == 'file2.js' 