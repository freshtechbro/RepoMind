"""
GitHub integration package for RepoMind.

This package provides integration with GitHub repositories,
including URL validation, repository cloning, authentication,
token management, and repository analysis.
"""

from app.github.url_validator import validate_github_url, extract_repo_info
from app.github.repository_cloner import clone_repository, ProgressTracker
from app.github.authentication import create_oauth_url, exchange_code_for_token, validate_token, OAuthConfig
from app.github.token_storage import save_token, load_token, delete_token
from app.github.repository_analyzer import (
    analyze_repository_structure,
    detect_repository_languages,
    get_file_language,
    RepositoryAnalysisResult,
    LanguageStats
)

__all__ = [
    'validate_github_url',
    'extract_repo_info',
    'clone_repository',
    'ProgressTracker',
    'create_oauth_url',
    'exchange_code_for_token',
    'validate_token',
    'OAuthConfig',
    'save_token',
    'load_token',
    'delete_token',
    'analyze_repository_structure',
    'detect_repository_languages',
    'get_file_language',
    'RepositoryAnalysisResult',
    'LanguageStats'
] 