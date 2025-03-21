"""
File type detection module for RepoMind.

This module provides functionality to detect file types based on extensions and content,
and provides icons and language names for different file types.
"""

import os
import pathlib
import re
from enum import Enum, auto

class FileType(Enum):
    """Enumeration of supported file types."""
    PYTHON = auto()
    JAVASCRIPT = auto()
    TYPESCRIPT = auto()
    HTML = auto()
    CSS = auto()
    MARKDOWN = auto()
    JSON = auto()
    YAML = auto()
    IMAGE = auto()
    SHELL = auto()
    UNKNOWN = auto()

class FileTypeDetector:
    """
    Detects file types based on file extensions and content analysis.
    
    This class provides methods to identify the type of a file, get 
    appropriate icons for file types, and return human-readable language names.
    """
    
    def __init__(self):
        """Initialize the file type detector with extension mappings."""
        self._extension_map = {
            # Python
            '.py': FileType.PYTHON,
            '.pyw': FileType.PYTHON,
            '.pyi': FileType.PYTHON,
            
            # JavaScript
            '.js': FileType.JAVASCRIPT,
            '.jsx': FileType.JAVASCRIPT,
            '.mjs': FileType.JAVASCRIPT,
            
            # TypeScript
            '.ts': FileType.TYPESCRIPT,
            '.tsx': FileType.TYPESCRIPT,
            
            # HTML
            '.html': FileType.HTML,
            '.htm': FileType.HTML,
            '.xhtml': FileType.HTML,
            
            # CSS
            '.css': FileType.CSS,
            '.scss': FileType.CSS,
            '.sass': FileType.CSS,
            
            # Markdown
            '.md': FileType.MARKDOWN,
            '.markdown': FileType.MARKDOWN,
            
            # JSON
            '.json': FileType.JSON,
            
            # YAML
            '.yml': FileType.YAML,
            '.yaml': FileType.YAML,
            
            # Image files
            '.png': FileType.IMAGE,
            '.jpg': FileType.IMAGE,
            '.jpeg': FileType.IMAGE,
            '.gif': FileType.IMAGE,
            '.svg': FileType.IMAGE,
            '.webp': FileType.IMAGE,
            
            # Shell scripts
            '.sh': FileType.SHELL,
            '.bash': FileType.SHELL,
            '.zsh': FileType.SHELL,
        }
        
        self._icon_map = {
            FileType.PYTHON: "python-icon",
            FileType.JAVASCRIPT: "javascript-icon",
            FileType.TYPESCRIPT: "typescript-icon",
            FileType.HTML: "html-icon",
            FileType.CSS: "css-icon",
            FileType.MARKDOWN: "markdown-icon",
            FileType.JSON: "json-icon",
            FileType.YAML: "yaml-icon",
            FileType.IMAGE: "image-icon",
            FileType.SHELL: "shell-icon",
            FileType.UNKNOWN: "file-icon",
        }
        
        self._language_map = {
            FileType.PYTHON: "Python",
            FileType.JAVASCRIPT: "JavaScript",
            FileType.TYPESCRIPT: "TypeScript",
            FileType.HTML: "HTML",
            FileType.CSS: "CSS",
            FileType.MARKDOWN: "Markdown",
            FileType.JSON: "JSON",
            FileType.YAML: "YAML",
            FileType.IMAGE: "Image",
            FileType.SHELL: "Shell",
            FileType.UNKNOWN: "Plain Text",
        }
    
    def detect_file_type(self, file_path):
        """
        Detect the type of a file based on its extension and content.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            FileType: The detected file type
            
        Raises:
            FileNotFoundError: If the file does not exist
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # First try to detect by extension
        ext = pathlib.Path(file_path).suffix.lower()
        if ext in self._extension_map:
            return self._extension_map[ext]
        
        # If no extension or unrecognized extension, try to detect by content
        return self._detect_by_content(file_path)
    
    def _detect_by_content(self, file_path):
        """
        Detect file type by examining its content.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            FileType: The detected file type
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(1024)  # Read first 1KB for detection
                
                # Check for Python shebang
                if re.search(r'^#!/usr/bin/env python|^#!/usr/bin/python', content):
                    return FileType.PYTHON
                
                # Check for Shell script shebang
                if re.search(r'^#!/bin/bash|^#!/bin/sh|^#!/usr/bin/env bash', content):
                    return FileType.SHELL
                
                # Check for HTML
                if re.search(r'<!DOCTYPE html>|<html', content, re.IGNORECASE):
                    return FileType.HTML
                
                # Check for JSON
                if content.strip().startswith('{') and content.strip().endswith('}'):
                    try:
                        import json
                        json.loads(content)
                        return FileType.JSON
                    except:
                        pass
                
                # Check for YAML
                if re.search(r'---\s*\n', content):
                    try:
                        import yaml
                        yaml.safe_load(content)
                        return FileType.YAML
                    except:
                        pass
        except:
            # If we can't read the file or there's an error, default to unknown
            pass
        
        return FileType.UNKNOWN
    
    def get_icon_for_file_type(self, file_type):
        """
        Get the icon identifier for a file type.
        
        Args:
            file_type (FileType): The file type
            
        Returns:
            str: Icon identifier for the file type
        """
        return self._icon_map.get(file_type, self._icon_map[FileType.UNKNOWN])
    
    def get_language_for_file_type(self, file_type):
        """
        Get the human-readable language name for a file type.
        
        Args:
            file_type (FileType): The file type
            
        Returns:
            str: Language name for the file type
        """
        return self._language_map.get(file_type, self._language_map[FileType.UNKNOWN]) 