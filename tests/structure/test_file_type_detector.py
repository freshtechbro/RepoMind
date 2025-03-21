import unittest
from unittest.mock import patch, MagicMock
import os
import pathlib
from app.structure.file_type_detector import FileTypeDetector, FileType

class TestFileTypeDetector(unittest.TestCase):
    """Tests for the FileTypeDetector class."""
    
    def setUp(self):
        self.detector = FileTypeDetector()
    
    def test_detect_file_type_by_extension(self):
        """Test detection of file types based on file extensions."""
        # Test Python files
        self.assertEqual(self.detector.detect_file_type("example.py"), FileType.PYTHON)
        self.assertEqual(self.detector.detect_file_type("/path/to/script.py"), FileType.PYTHON)
        
        # Test JavaScript files
        self.assertEqual(self.detector.detect_file_type("example.js"), FileType.JAVASCRIPT)
        self.assertEqual(self.detector.detect_file_type("/path/to/script.js"), FileType.JAVASCRIPT)
        
        # Test TypeScript files
        self.assertEqual(self.detector.detect_file_type("example.ts"), FileType.TYPESCRIPT)
        self.assertEqual(self.detector.detect_file_type("component.tsx"), FileType.TYPESCRIPT)
        
        # Test HTML files
        self.assertEqual(self.detector.detect_file_type("index.html"), FileType.HTML)
        
        # Test CSS files
        self.assertEqual(self.detector.detect_file_type("styles.css"), FileType.CSS)
        
        # Test Markdown files
        self.assertEqual(self.detector.detect_file_type("README.md"), FileType.MARKDOWN)
        
        # Test JSON files
        self.assertEqual(self.detector.detect_file_type("config.json"), FileType.JSON)
        
        # Test YAML files
        self.assertEqual(self.detector.detect_file_type("docker-compose.yml"), FileType.YAML)
        self.assertEqual(self.detector.detect_file_type("config.yaml"), FileType.YAML)
        
        # Test image files
        self.assertEqual(self.detector.detect_file_type("image.png"), FileType.IMAGE)
        self.assertEqual(self.detector.detect_file_type("photo.jpg"), FileType.IMAGE)
        self.assertEqual(self.detector.detect_file_type("icon.svg"), FileType.IMAGE)
        
        # Test unknown file type
        self.assertEqual(self.detector.detect_file_type("unknown.xyz"), FileType.UNKNOWN)
    
    def test_detect_file_type_by_content(self):
        """Test detection of file types based on file content when extension is ambiguous."""
        # Create a mock file with Python shebang
        with patch("builtins.open", mock_open(read_data="#!/usr/bin/env python\n# Python script")) as mock_file:
            self.assertEqual(self.detector.detect_file_type("script"), FileType.PYTHON)
        
        # Create a mock file with bash shebang
        with patch("builtins.open", mock_open(read_data="#!/bin/bash\n# Bash script")) as mock_file:
            self.assertEqual(self.detector.detect_file_type("script"), FileType.SHELL)
        
        # Create a mock file with HTML content
        with patch("builtins.open", mock_open(read_data="<!DOCTYPE html><html><body></body></html>")) as mock_file:
            self.assertEqual(self.detector.detect_file_type("file"), FileType.HTML)
        
        # Create a mock file with JSON content
        with patch("builtins.open", mock_open(read_data='{"key": "value"}')) as mock_file:
            self.assertEqual(self.detector.detect_file_type("data"), FileType.JSON)
    
    def test_detect_file_type_nonexistent_file(self):
        """Test handling of nonexistent files."""
        with patch("os.path.isfile", return_value=False):
            with self.assertRaises(FileNotFoundError):
                self.detector.detect_file_type("nonexistent.txt")
    
    def test_get_icon_for_file_type(self):
        """Test getting icons for different file types."""
        self.assertEqual(self.detector.get_icon_for_file_type(FileType.PYTHON), "python-icon")
        self.assertEqual(self.detector.get_icon_for_file_type(FileType.JAVASCRIPT), "javascript-icon")
        self.assertEqual(self.detector.get_icon_for_file_type(FileType.TYPESCRIPT), "typescript-icon")
        self.assertEqual(self.detector.get_icon_for_file_type(FileType.HTML), "html-icon")
        self.assertEqual(self.detector.get_icon_for_file_type(FileType.CSS), "css-icon")
        self.assertEqual(self.detector.get_icon_for_file_type(FileType.MARKDOWN), "markdown-icon")
        self.assertEqual(self.detector.get_icon_for_file_type(FileType.JSON), "json-icon")
        self.assertEqual(self.detector.get_icon_for_file_type(FileType.YAML), "yaml-icon")
        self.assertEqual(self.detector.get_icon_for_file_type(FileType.IMAGE), "image-icon")
        self.assertEqual(self.detector.get_icon_for_file_type(FileType.SHELL), "shell-icon")
        self.assertEqual(self.detector.get_icon_for_file_type(FileType.UNKNOWN), "file-icon")
    
    def test_get_language_for_file_type(self):
        """Test getting language names for different file types."""
        self.assertEqual(self.detector.get_language_for_file_type(FileType.PYTHON), "Python")
        self.assertEqual(self.detector.get_language_for_file_type(FileType.JAVASCRIPT), "JavaScript")
        self.assertEqual(self.detector.get_language_for_file_type(FileType.TYPESCRIPT), "TypeScript")
        self.assertEqual(self.detector.get_language_for_file_type(FileType.HTML), "HTML")
        self.assertEqual(self.detector.get_language_for_file_type(FileType.CSS), "CSS")
        self.assertEqual(self.detector.get_language_for_file_type(FileType.MARKDOWN), "Markdown")
        self.assertEqual(self.detector.get_language_for_file_type(FileType.JSON), "JSON")
        self.assertEqual(self.detector.get_language_for_file_type(FileType.YAML), "YAML")
        self.assertEqual(self.detector.get_language_for_file_type(FileType.SHELL), "Shell")
        self.assertEqual(self.detector.get_language_for_file_type(FileType.UNKNOWN), "Plain Text")

def mock_open(read_data=""):
    """Helper function to create a mock file object."""
    mock = MagicMock(name="open")
    mock.return_value.__enter__.return_value.read.return_value = read_data
    return mock


if __name__ == "__main__":
    unittest.main() 