"""
API routes for file/module structure visualization.
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Body, Query
from pydantic import BaseModel, Field

from app.structure.directory_scanner import scan_directory, get_file_stats
from app.structure.dependency_analyzer import analyze_dependencies
from app.structure.tree_converter import (
    create_file_structure_tree,
    create_dependency_visualization,
    get_file_structure_stats
)

router = APIRouter(
    prefix="/structure",
    tags=["structure"],
    responses={404: {"description": "Not found"}},
)


class StructureNodeBase(BaseModel):
    """Base model for structure tree nodes."""
    id: str
    name: str
    type: str  # 'file' or 'directory'
    path: str


class FileStructureNode(StructureNodeBase):
    """Model for file nodes in the structure tree."""
    type: str = "file"
    extension: Optional[str] = None
    size: Optional[int] = None
    fileType: Optional[str] = None
    icon: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DirectoryStructureNode(StructureNodeBase):
    """Model for directory nodes in the structure tree."""
    type: str = "directory"
    children: List[Any] = Field(default_factory=list)


DirectoryStructureNode.update_forward_refs()


class StructureTreeResponse(BaseModel):
    """Response model for repository structure."""
    tree: Dict[str, Any]
    stats: Dict[str, Any]


class DependencyNode(BaseModel):
    """Model for a node in the dependency graph."""
    id: str
    name: str
    path: str
    type: str


class DependencyEdge(BaseModel):
    """Model for an edge in the dependency graph."""
    source: str
    target: str
    type: str = "dependency"


class DependencyGraphResponse(BaseModel):
    """Response model for dependency graph."""
    nodes: List[DependencyNode]
    edges: List[DependencyEdge]
    stats: Dict[str, Any]


@router.get("/tree/{repository_id}", response_model=StructureTreeResponse)
async def get_repository_structure(
    repository_id: str,
    exclude_dirs: Optional[List[str]] = Query(None, description="Directories to exclude"),
):
    """
    Get the file/directory structure for a repository.
    
    Returns a hierarchical tree representation of files and directories,
    along with statistics about file types, sizes, etc.
    """
    # TODO: Replace with actual repository path lookup
    repository_path = f"./data/repositories/{repository_id}"
    
    try:
        # Create the file structure tree using the new converter
        tree = create_file_structure_tree(repository_path, exclude_dirs)
        
        # Get statistics about the repository
        stats = get_file_structure_stats(repository_path)
        
        return StructureTreeResponse(
            tree=tree,
            stats=stats
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get repository structure: {str(e)}"
        )


@router.get("/dependencies/{repository_id}", response_model=DependencyGraphResponse)
async def get_repository_dependencies(
    repository_id: str,
    exclude_dirs: Optional[List[str]] = Query(None, description="Directories to exclude"),
):
    """
    Get the dependency graph for a repository.
    
    Returns a graph representation of file dependencies based on import statements,
    along with statistics about dependencies.
    """
    # TODO: Replace with actual repository path lookup
    repository_path = f"./data/repositories/{repository_id}"
    
    try:
        # Create dependency visualization using the new converter
        dependency_data = create_dependency_visualization(repository_path)
        
        # Get additional statistics for the dependency graph
        graph = analyze_dependencies(repository_path)
        stats = {
            "total_files": len(dependency_data["nodes"]),
            "total_dependencies": len(dependency_data["edges"]),
            "circular_dependencies": graph.find_circular_dependencies()
        }
        
        return DependencyGraphResponse(
            nodes=dependency_data["nodes"],
            edges=dependency_data["edges"],
            stats=stats
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get repository dependencies: {str(e)}"
        )


@router.get("/file-types/{repository_id}")
async def get_file_type_distribution(
    repository_id: str,
    exclude_dirs: Optional[List[str]] = Query(None, description="Directories to exclude"),
):
    """
    Get the distribution of file types in a repository.
    
    Returns statistics about file types, extensions, and sizes.
    """
    # TODO: Replace with actual repository path lookup
    repository_path = f"./data/repositories/{repository_id}"
    
    try:
        # Get statistics about the repository
        stats = get_file_structure_stats(repository_path)
        
        return {
            "file_types": stats["files_by_type"],
            "extensions": stats["files_by_extension"],
            "total_files": stats["total_files"],
            "total_size": stats["total_size"],
            "largest_files": stats["largest_files"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get file type distribution: {str(e)}"
        )


@router.get("/search/{repository_id}")
async def search_repository_files(
    repository_id: str,
    query: str = Query(..., description="Search query"),
    exclude_dirs: Optional[List[str]] = Query(None, description="Directories to exclude"),
):
    """
    Search for files in a repository by name, path, or content.
    
    Returns a list of files that match the search criteria.
    """
    # TODO: Replace with actual repository path lookup
    repository_path = f"./data/repositories/{repository_id}"
    
    try:
        import os
        import re
        
        # Create the file structure tree
        tree = create_file_structure_tree(repository_path, exclude_dirs)
        
        # Flatten the tree to get all files
        all_files = []
        
        def collect_files(node):
            if node["type"] == "file":
                all_files.append(node)
            elif "children" in node:
                for child in node["children"]:
                    collect_files(child)
        
        collect_files(tree)
        
        # Filter files based on the search query
        query_lower = query.lower()
        matching_files = [
            file for file in all_files
            if query_lower in file["name"].lower() or query_lower in file["path"].lower()
        ]
        
        return {
            "results": matching_files,
            "count": len(matching_files)
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to search repository files: {str(e)}"
        ) 