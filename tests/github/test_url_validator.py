import pytest
from app.github.url_validator import validate_github_url, extract_repo_info

def test_valid_github_urls():
    """Test that valid GitHub URLs pass validation."""
    valid_urls = [
        "https://github.com/username/repo",
        "https://github.com/username/repo.git",
        "git@github.com:username/repo.git",
        "https://github.com/org-name/repo-name",
        "https://github.com/username/repo/tree/branch-name",
        "https://github.com/username/repo/blob/main/README.md"
    ]
    for url in valid_urls:
        assert validate_github_url(url) is True, f"URL should be valid: {url}"

def test_invalid_github_urls():
    """Test that invalid GitHub URLs fail validation."""
    invalid_urls = [
        "https://gitlab.com/username/repo",
        "https://github.com",
        "https://github.com/username",
        "invalid-url",
        "https://example.com/github.com/username/repo",
        "https://github.com/",
        "github.com/username/repo",
        "",
        None
    ]
    for url in invalid_urls:
        assert validate_github_url(url) is False, f"URL should be invalid: {url}"

def test_extract_repo_info_from_https_url():
    """Test extracting repository information from HTTPS URL."""
    url = "https://github.com/username/repo"
    owner, repo, branch = extract_repo_info(url)
    assert owner == "username"
    assert repo == "repo"
    assert branch is None

def test_extract_repo_info_from_ssh_url():
    """Test extracting repository information from SSH URL."""
    url = "git@github.com:username/repo.git"
    owner, repo, branch = extract_repo_info(url)
    assert owner == "username"
    assert repo == "repo"
    assert branch is None

def test_extract_repo_info_with_branch():
    """Test extracting repository information with branch."""
    url = "https://github.com/username/repo/tree/feature-branch"
    owner, repo, branch = extract_repo_info(url)
    assert owner == "username"
    assert repo == "repo"
    assert branch == "feature-branch"

def test_extract_repo_info_from_blob_url():
    """Test extracting repository information from a blob URL."""
    url = "https://github.com/username/repo/blob/main/README.md"
    owner, repo, branch = extract_repo_info(url)
    assert owner == "username"
    assert repo == "repo"
    assert branch == "main"
    
def test_extract_repo_info_with_dot_git():
    """Test extracting repository information from URL with .git suffix."""
    url = "https://github.com/username/repo.git"
    owner, repo, branch = extract_repo_info(url)
    assert owner == "username"
    assert repo == "repo"
    assert branch is None

def test_extract_repo_info_with_invalid_url():
    """Test extracting repository information from invalid URL raises error."""
    url = "https://gitlab.com/username/repo"
    with pytest.raises(ValueError):
        extract_repo_info(url) 