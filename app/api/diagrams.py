"""
API endpoints for diagram generation.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, Dict, Any

from app.diagrams.sequence.diagram_generator import generate_sequence_diagram_data
from app.diagrams.sequence.async_diagram_generator import generate_async_enhanced_diagram
from app.diagrams.sequence.conditional_diagram_generator import generate_conditional_enhanced_diagram
from app.services.repository_service import RepositoryService
from app.models.diagrams import DiagramRequest, DiagramResponse

router = APIRouter(prefix="/diagrams", tags=["diagrams"])


@router.post("/sequence", response_model=DiagramResponse)
async def create_sequence_diagram(
    request: DiagramRequest,
    repository_service: RepositoryService = Depends()
):
    """
    Generate a sequence diagram for the specified file or function.
    """
    try:
        # Get repository data
        repository = await repository_service.get_repository(request.repository_id)
        if not repository:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        # Get file content if specific file is requested
        file_content = None
        if request.file_path:
            file_content = await repository_service.get_file_content(
                request.repository_id, 
                request.file_path
            )
            if not file_content:
                raise HTTPException(status_code=404, detail="File not found")
        
        # Generate diagram data
        sequence_data = await repository_service.analyze_method_calls(
            request.repository_id,
            request.file_path,
            request.function_name
        )
        
        # Generate diagram with proper settings
        include_returns = request.options.get("include_returns", True)
        diagram_data = generate_sequence_diagram_data(
            sequence_data,
            include_returns=include_returns,
            title=f"Sequence Diagram: {request.function_name or request.file_path}"
        )
        
        return {"diagram_data": diagram_data, "type": "sequence"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sequence-async", response_model=DiagramResponse)
async def create_async_sequence_diagram(
    request: DiagramRequest,
    repository_service: RepositoryService = Depends()
):
    """
    Generate an asynchronous pattern-enhanced sequence diagram.
    
    This endpoint analyzes source code for asynchronous patterns and visualizes
    them in the sequence diagram, including async/await, promises, threads,
    callbacks, and other asynchronous execution flows.
    """
    try:
        # Get repository data
        repository = await repository_service.get_repository(request.repository_id)
        if not repository:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        # Get file content - required for async pattern detection
        file_content = await repository_service.get_file_content(
            request.repository_id, 
            request.file_path
        )
        if not file_content:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Get language from file extension or options
        language = request.options.get("language")
        if not language:
            # Try to determine language from file extension
            if request.file_path.endswith((".py")):
                language = "python"
            elif request.file_path.endswith((".js", ".jsx")):
                language = "javascript"
            elif request.file_path.endswith((".ts", ".tsx")):
                language = "typescript"
            else:
                language = "unknown"
        
        # Generate sequence data
        sequence_data = await repository_service.analyze_method_calls(
            request.repository_id,
            request.file_path,
            request.function_name
        )
        
        # Generate async-enhanced diagram
        include_returns = request.options.get("include_returns", True)
        diagram_data = generate_async_enhanced_diagram(
            sequence_data,
            file_content,
            language=language,
            include_returns=include_returns,
            title=f"Async Sequence Diagram: {request.function_name or request.file_path}"
        )
        
        return {"diagram_data": diagram_data, "type": "sequence-async"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sequence-conditional", response_model=DiagramResponse)
async def create_conditional_sequence_diagram(
    request: DiagramRequest,
    repository_service: RepositoryService = Depends()
):
    """
    Generate a conditional flow-enhanced sequence diagram.
    
    This endpoint analyzes source code for conditional patterns and visualizes
    them in the sequence diagram, including if statements, loops, try-except blocks,
    and other conditional control flow structures.
    """
    try:
        # Get repository data
        repository = await repository_service.get_repository(request.repository_id)
        if not repository:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        # Get file content - required for conditional pattern detection
        file_content = await repository_service.get_file_content(
            request.repository_id, 
            request.file_path
        )
        if not file_content:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Get language from file extension or options
        language = request.options.get("language")
        if not language:
            # Try to determine language from file extension
            if request.file_path.endswith((".py")):
                language = "python"
            elif request.file_path.endswith((".js", ".jsx")):
                language = "javascript"
            elif request.file_path.endswith((".ts", ".tsx")):
                language = "typescript"
            else:
                language = "unknown"
        
        # Generate sequence data
        sequence_data = await repository_service.analyze_method_calls(
            request.repository_id,
            request.file_path,
            request.function_name
        )
        
        # Generate conditional-enhanced diagram
        include_returns = request.options.get("include_returns", True)
        diagram_data = generate_conditional_enhanced_diagram(
            sequence_data,
            file_content,
            language=language,
            include_returns=include_returns,
            title=f"Conditional Sequence Diagram: {request.function_name or request.file_path}"
        )
        
        return {"diagram_data": diagram_data, "type": "sequence-conditional"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 