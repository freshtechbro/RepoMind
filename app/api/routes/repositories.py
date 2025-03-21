"""
API routes for GitHub repositories.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, field_validator
import os
import uuid
from typing import Optional

from app.github.url_validator import validate_github_url, extract_repo_info
from app.github.repository_cloner import clone_repository, ProgressTracker

# Create a router instance
router = APIRouter(
    prefix="/repositories",
    tags=["repositories"],
    responses={404: {"description": "Not found"}},
)

# Define API models
class RepositoryURL(BaseModel):
    """Model for repository URL requests."""
    url: str
    
    @field_validator('url')
    @classmethod
    def url_must_be_valid(cls, v):
        """Validate that the URL is a valid GitHub repository URL."""
        if not validate_github_url(v):
            raise ValueError("Invalid GitHub repository URL")
        return v

class CloneRequest(RepositoryURL):
    """Model for repository clone requests."""
    branch: Optional[str] = None

class RepositoryInfo(BaseModel):
    """Model for repository information."""
    owner: str
    name: str
    branch: Optional[str] = None
    url: str

class CloneResponse(BaseModel):
    """Model for clone response."""
    task_id: str
    repository: RepositoryInfo

# Create a dictionary to store cloning tasks and their progress
clone_tasks = {}

@router.post("/validate", response_model=RepositoryInfo)
async def validate_repository(repo: RepositoryURL):
    """
    Validate a GitHub repository URL and return repository information.
    """
    try:
        owner, repo_name, branch = extract_repo_info(repo.url)
        return RepositoryInfo(
            owner=owner,
            name=repo_name,
            branch=branch,
            url=repo.url
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

def clone_repository_task(task_id: str, url: str, branch: Optional[str] = None):
    """
    Background task for cloning a repository.
    
    Args:
        task_id: The unique ID for this cloning task
        url: The GitHub repository URL
        branch: The branch to clone (optional)
    """
    # Create a progress tracker
    tracker = ProgressTracker()
    
    # Set up the clone directory (normally would come from config)
    clone_dir = os.path.join(os.getcwd(), "cloned_repos")
    os.makedirs(clone_dir, exist_ok=True)
    
    # Update task status
    clone_tasks[task_id] = {
        "status": "in_progress",
        "progress": 0,
        "operation": "Starting clone",
        "repository": {}
    }
    
    try:
        # Extract repository info
        owner, repo_name, url_branch = extract_repo_info(url)
        
        # Use branch from URL if not specified
        if not branch and url_branch:
            branch = url_branch
            
        # Update repository info
        clone_tasks[task_id]["repository"] = {
            "owner": owner,
            "name": repo_name,
            "branch": branch,
            "url": url
        }
        
        # Clone the repository
        repo_path = clone_repository(url, clone_dir, branch, tracker)
        
        # Update task status
        clone_tasks[task_id]["status"] = "completed"
        clone_tasks[task_id]["progress"] = 100
        clone_tasks[task_id]["operation"] = "Clone completed"
        clone_tasks[task_id]["path"] = repo_path
        
    except Exception as e:
        # Update task status with error
        clone_tasks[task_id]["status"] = "error"
        clone_tasks[task_id]["error"] = str(e)

@router.post("/clone", response_model=CloneResponse, status_code=202)
async def clone_repo(repo: CloneRequest, background_tasks: BackgroundTasks):
    """
    Clone a GitHub repository.
    
    This endpoint initiates a background task to clone the repository.
    """
    # Create a unique task ID
    task_id = str(uuid.uuid4())
    
    # Extract repository info for the response
    owner, repo_name, url_branch = extract_repo_info(repo.url)
    
    # Use branch from URL if not specified in request
    branch = repo.branch if repo.branch else url_branch
    
    # Add the cloning task to background tasks
    background_tasks.add_task(clone_repository_task, task_id, repo.url, branch)
    
    # Return the task ID and repository info
    return CloneResponse(
        task_id=task_id,
        repository=RepositoryInfo(
            owner=owner,
            name=repo_name,
            branch=branch,
            url=repo.url
        )
    )

@router.get("/clone/{task_id}")
async def get_clone_status(task_id: str):
    """
    Get the status of a repository cloning task.
    """
    if task_id not in clone_tasks:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
    return clone_tasks[task_id] 