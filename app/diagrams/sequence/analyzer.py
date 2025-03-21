"""
Integration module for Python code analysis and sequence diagram generation.
"""
from typing import Dict, List, Any, Optional

from app.analysis.python_extractor import extract_method_calls, extract_object_creations
from app.diagrams.sequence.generator import generate_sequence_diagram, create_sequence_diagram_from_code


def extract_callee_from_method_calls(method_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enhance method calls by inferring the callee from method names if not present.
    
    Args:
        method_calls: List of method call dictionaries
        
    Returns:
        List[Dict[str, Any]]: Enhanced method calls with callee information
    """
    enhanced_calls = []
    
    for call in method_calls:
        enhanced_call = call.copy()
        
        # Skip if callee is already present
        if 'callee' in enhanced_call:
            enhanced_calls.append(enhanced_call)
            continue
        
        # Try to infer callee from method name (e.g., database.query -> Database)
        method = enhanced_call.get('method', '')
        if '.' in method:
            parts = method.split('.')
            if len(parts) >= 2:
                # Capitalize the first part to make it look like a class/component
                callee = parts[0].capitalize()
                # Update method name to be just the last part
                enhanced_call['method'] = parts[-1]
                enhanced_call['callee'] = callee
        else:
            # Default to using a target derived from method name
            enhanced_call['callee'] = _infer_target_from_method(method)
            
        enhanced_calls.append(enhanced_call)
    
    return enhanced_calls


def _infer_target_from_method(method_name: str) -> str:
    """
    Infer a target/callee from a method name based on common naming patterns.
    
    Args:
        method_name: Name of the method
        
    Returns:
        str: Inferred target name
    """
    # These are just heuristics that work for common method naming conventions
    
    # For "getData", "saveFile", etc., use the noun part
    if len(method_name) > 4:
        for verb in ['get', 'set', 'fetch', 'load', 'save', 'update', 'delete', 'create', 'find']:
            if method_name.lower().startswith(verb) and len(method_name) > len(verb):
                # Capitalize the object part (e.g., "Data" from "getData")
                object_part = method_name[len(verb):]
                return object_part
    
    # For "queryDatabase", "validateInput", etc., use the last word
    for noun in ['database', 'service', 'repository', 'manager', 'controller', 'validator']:
        if method_name.lower().endswith(noun):
            return noun.capitalize()
    
    # Default to a generic service name
    return "Service"


def analyze_python_file(file_path: str) -> str:
    """
    Analyze a Python file and generate a sequence diagram.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        str: Mermaid.js syntax for a sequence diagram
    """
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    return analyze_python_code(code)


def analyze_python_code(code: str) -> str:
    """
    Analyze Python code and generate a sequence diagram.
    
    Args:
        code: Python source code
        
    Returns:
        str: Mermaid.js syntax for a sequence diagram
    """
    # Extract method calls and object creations
    method_calls = extract_method_calls(code)
    object_creations = extract_object_creations(code)
    
    # Enhance method calls with inferred callee information
    enhanced_calls = extract_callee_from_method_calls(method_calls)
    
    # Generate the sequence diagram
    return create_sequence_diagram_from_code(enhanced_calls, object_creations) 