"""
API routes for diagram generation from code analysis.
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field

from app.diagrams.sequence.analyzer import analyze_python_code
from app.diagrams.sequence.typescript_analyzer import analyze_typescript_code

router = APIRouter(
    prefix="/diagrams",
    tags=["diagrams"],
    responses={404: {"description": "Not found"}},
)


class DiagramRequest(BaseModel):
    """Request model for diagram generation."""
    code: str = Field(..., description="Source code to analyze")
    language: str = Field("python", description="Programming language of the source code")
    diagram_type: str = Field("sequence", description="Type of diagram to generate")


class DiagramResponse(BaseModel):
    """Response model for diagram generation."""
    diagram: str = Field(..., description="Generated diagram in Mermaid.js syntax")
    diagram_type: str = Field(..., description="Type of the generated diagram")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the diagram")


@router.post("/sequence", response_model=DiagramResponse)
async def generate_sequence_diagram(request: DiagramRequest = Body(...)):
    """
    Generate a sequence diagram from source code.
    
    Supports Python and TypeScript/JavaScript code analysis.
    """
    language = request.language.lower()
    
    try:
        # Generate the sequence diagram based on language
        if language == "python":
            mermaid_syntax = analyze_python_code(request.code)
        elif language in ["typescript", "javascript", "ts", "js"]:
            mermaid_syntax = analyze_typescript_code(request.code)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported language: {request.language}. Currently supporting Python, TypeScript, and JavaScript."
            )
        
        return DiagramResponse(
            diagram=mermaid_syntax,
            diagram_type="sequence",
            metadata={
                "language": request.language,
                "syntax": "mermaid"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to generate sequence diagram: {str(e)}"
        )


@router.post("/analyze", response_model=DiagramResponse)
async def analyze_code(request: DiagramRequest = Body(...)):
    """
    Analyze code and generate an appropriate diagram.
    
    This endpoint automatically selects the appropriate diagram type
    based on the content of the code.
    """
    language = request.language.lower()
    
    try:
        # For now, we only support sequence diagrams
        if language == "python":
            mermaid_syntax = analyze_python_code(request.code)
        elif language in ["typescript", "javascript", "ts", "js"]:
            mermaid_syntax = analyze_typescript_code(request.code)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported language: {request.language}. Currently supporting Python, TypeScript, and JavaScript."
            )
        
        return DiagramResponse(
            diagram=mermaid_syntax,
            diagram_type="sequence",
            metadata={
                "language": request.language,
                "syntax": "mermaid"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to analyze code: {str(e)}"
        ) 