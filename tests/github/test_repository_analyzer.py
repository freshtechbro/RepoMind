"""
Tests for the repository analyzer module.
"""

import os
import pytest
from unittest.mock import patch, MagicMock, mock_open
from app.github.repository_analyzer import (
    analyze_repository_structure,
    detect_repository_languages,
    get_file_language,
    RepositoryAnalysisResult,
    LanguageStats
)

@pytest.fixture
def mock_repo_path():
    """Fixture for a mock repository path."""
    return "/tmp/mock_repo"

@pytest.fixture
def mock_file_structure():
    """Fixture for a mock file structure."""
    return [
        # Python files
        "/tmp/mock_repo/main.py",
        "/tmp/mock_repo/utils/helpers.py",
        "/tmp/mock_repo/models/user.py",
        # JavaScript files
        "/tmp/mock_repo/static/js/app.js",
        "/tmp/mock_repo/static/js/utils.js",
        # TypeScript files
        "/tmp/mock_repo/src/components/Button.tsx",
        "/tmp/mock_repo/src/index.ts",
        # Other files
        "/tmp/mock_repo/README.md",
        "/tmp/mock_repo/.gitignore",
        "/tmp/mock_repo/requirements.txt"
    ]

@pytest.fixture
def mock_file_contents():
    """Fixture for mock file contents."""
    return {
        "/tmp/mock_repo/main.py": "import os\n\ndef main():\n    print('Hello World')\n\nif __name__ == '__main__':\n    main()",
        "/tmp/mock_repo/src/index.ts": "import { Button } from './components/Button';\n\nconst app = document.getElementById('app');\nconst button = new Button('Click me');"
    }

def test_get_file_language():
    """Test detection of a file's programming language based on extension."""
    # Test Python detection
    assert get_file_language("script.py") == "Python"
    assert get_file_language("/path/to/module.py") == "Python"
    
    # Test JavaScript detection
    assert get_file_language("app.js") == "JavaScript"
    assert get_file_language("/static/utils.js") == "JavaScript"
    
    # Test TypeScript detection
    assert get_file_language("component.ts") == "TypeScript"
    assert get_file_language("Component.tsx") == "TypeScript"
    
    # Test other languages
    assert get_file_language("style.css") == "CSS"
    assert get_file_language("index.html") == "HTML"
    assert get_file_language("Dockerfile") == "Dockerfile"
    
    # Test unknown extension
    assert get_file_language("unknown.xyz") == "Unknown"
    
    # Test files without extension
    assert get_file_language("README") == "Unknown"
    assert get_file_language("Makefile") == "Makefile"  # Special case

def test_detect_repository_languages(mock_repo_path, mock_file_structure):
    """Test detection of languages used in a repository."""
    with patch('os.walk') as mock_walk, \
         patch('os.path.join', os.path.join):  # Ensure os.path.join still works normally
        
        # Create a proper directory structure for os.walk to return
        root_dir = mock_repo_path
        dirs = ['utils', 'models', 'static', 'src']
        root_files = ['main.py', 'README.md', '.gitignore', 'requirements.txt']
        
        # Build walk_data more explicitly to match what os.walk would actually return
        walk_data = [
            # Root directory with subdirectories and files
            (root_dir, dirs, root_files),
            
            # utils directory with files
            (os.path.join(root_dir, 'utils'), [], ['helpers.py']),
            
            # models directory with files
            (os.path.join(root_dir, 'models'), [], ['user.py']),
            
            # static directory with subdirectories
            (os.path.join(root_dir, 'static'), ['js'], []),
            
            # static/js directory with files
            (os.path.join(root_dir, 'static', 'js'), [], ['app.js', 'utils.js']),
            
            # src directory with subdirectories
            (os.path.join(root_dir, 'src'), ['components'], ['index.ts']),
            
            # src/components directory with files
            (os.path.join(root_dir, 'src', 'components'), [], ['Button.tsx']),
        ]
        
        mock_walk.return_value = walk_data
        
        # Call the function under test
        result = detect_repository_languages(mock_repo_path)
        
        # Check the results
        assert isinstance(result, LanguageStats)
        assert "Python" in result.languages
        assert "JavaScript" in result.languages
        assert "TypeScript" in result.languages
        
        # Check counts
        assert result.languages["Python"] == 3
        assert result.languages["JavaScript"] == 2
        assert result.languages["TypeScript"] == 2
        
        # Check percentages
        total_files = 7  # Python + JS + TS files (not counting README, etc.)
        assert result.percentages["Python"] == pytest.approx(3 / total_files * 100)
        assert result.percentages["JavaScript"] == pytest.approx(2 / total_files * 100)
        assert result.percentages["TypeScript"] == pytest.approx(2 / total_files * 100)
        
        # Check primary language
        assert result.primary_language == "Python"

def test_analyze_repository_structure(mock_repo_path, mock_file_structure, mock_file_contents):
    """Test analysis of repository structure."""
    with patch('os.walk') as mock_walk, \
         patch('builtins.open', mock_open()) as mock_file, \
         patch('app.github.repository_analyzer.detect_repository_languages') as mock_detect_languages:
        
        # Setup mock file structure
        mock_dirs = set(os.path.dirname(f) for f in mock_file_structure if os.path.dirname(f) != mock_repo_path)
        
        # Prepare mock data for os.walk
        walk_data = [
            (mock_repo_path, 
             [d for d in mock_dirs if os.path.dirname(d) == mock_repo_path], 
             [os.path.basename(f) for f in mock_file_structure if os.path.dirname(f) == mock_repo_path]
            ),
        ]
        
        # Add subdirectories
        for subdir in mock_dirs:
            parent_dir = os.path.dirname(subdir)
            if parent_dir in mock_dirs:
                walk_data.append((
                    subdir, 
                    [], 
                    [os.path.basename(f) for f in mock_file_structure if os.path.dirname(f) == subdir]
                ))
        
        mock_walk.return_value = walk_data
        
        # Mock file reading
        def mock_file_read_effect(file_path, *args, **kwargs):
            mock = MagicMock()
            mock.__enter__.return_value.read.return_value = mock_file_contents.get(file_path, "")
            return mock
        
        mock_file.side_effect = mock_file_read_effect
        
        # Mock language detection
        mock_detect_languages.return_value = LanguageStats(
            languages={"Python": 3, "JavaScript": 2, "TypeScript": 2},
            percentages={"Python": 42.86, "JavaScript": 28.57, "TypeScript": 28.57},
            primary_language="Python"
        )
        
        # Call the function under test
        result = analyze_repository_structure(mock_repo_path)
        
        # Check the result structure
        assert isinstance(result, RepositoryAnalysisResult)
        assert result.repository_path == mock_repo_path
        assert isinstance(result.file_count, int)
        assert isinstance(result.directory_count, int)
        assert isinstance(result.language_stats, LanguageStats)
        assert isinstance(result.file_structure, dict)
        
        # Verify language stats were included
        assert result.language_stats.primary_language == "Python"
        assert "Python" in result.language_stats.languages
        assert "JavaScript" in result.language_stats.languages
        assert "TypeScript" in result.language_stats.languages

def test_analyze_repository_structure_with_empty_repo(mock_repo_path):
    """Test analysis of an empty repository."""
    with patch('os.walk') as mock_walk, \
         patch('app.github.repository_analyzer.detect_repository_languages') as mock_detect_languages:
        
        # Setup empty repository
        mock_walk.return_value = [(mock_repo_path, [], [])]
        
        # Mock language detection for empty repo
        mock_detect_languages.return_value = LanguageStats(
            languages={},
            percentages={},
            primary_language=None
        )
        
        # Call the function under test
        result = analyze_repository_structure(mock_repo_path)
        
        # Check the result for an empty repository
        assert isinstance(result, RepositoryAnalysisResult)
        assert result.repository_path == mock_repo_path
        assert result.file_count == 0
        assert result.directory_count == 0
        assert not result.language_stats.languages
        assert not result.language_stats.percentages
        assert result.language_stats.primary_language is None 