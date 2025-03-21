"""
Integration module for TypeScript/JavaScript code analysis and sequence diagram generation.
"""
from typing import Dict, List, Any, Optional

from app.analysis.typescript_extractor import extract_method_calls
from app.diagrams.sequence.generator import generate_sequence_diagram, create_sequence_diagram_from_code


def extract_callee_from_ts_method_calls(method_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enhance TypeScript method calls by inferring the callee from method names if not present.
    
    Args:
        method_calls: List of method call dictionaries
        
    Returns:
        List[Dict[str, Any]]: Enhanced method calls with callee information
    """
    enhanced_calls = []
    
    for call in method_calls:
        enhanced_call = call.copy()
        
        # Skip constructor calls, they're already properly structured
        if enhanced_call.get('is_constructor', False):
            # Convert constructor calls to a method call format for the diagram
            if 'class' in enhanced_call:
                enhanced_call['callee'] = enhanced_call['class']
                enhanced_call['method'] = 'constructor'
            enhanced_calls.append(enhanced_call)
            continue
        
        # Skip if callee is already present
        if 'callee' in enhanced_call:
            enhanced_calls.append(enhanced_call)
            continue
        
        # Try to infer callee from caller (this.httpClient -> HttpClient)
        caller = enhanced_call.get('caller', '')
        
        if '.' in caller:
            parts = caller.split('.')
            if parts[0] == 'this':
                # For 'this.property', use the property name capitalized as the callee
                callee = parts[1].capitalize()
                enhanced_call['callee'] = callee
            else:
                # For other cases like 'service.submodule', use the first part capitalized
                callee = parts[0].capitalize()
                enhanced_call['callee'] = callee
        else:
            # For simple callers, use the caller name as callee or guess from method name
            if caller in ['this', 'self', 'window', 'global', 'document']:
                # For special objects, infer from method
                enhanced_call['callee'] = _infer_target_from_method(enhanced_call.get('method', ''))
            else:
                enhanced_call['callee'] = caller.capitalize()
            
        enhanced_calls.append(enhanced_call)
    
    return enhanced_calls


def _infer_target_from_method(method_name: str) -> str:
    """
    Infer a target/callee from a method name based on common JavaScript naming patterns.
    
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
    
    # Check for common async methods that imply a specific target
    if method_name in ['fetch', 'request', 'axios', 'ajax']:
        return 'ApiService'
    
    if method_name in ['subscribe', 'unsubscribe', 'publish']:
        return 'EventSystem'
    
    if method_name in ['log', 'warn', 'error', 'info', 'debug']:
        return 'Logger'
    
    # Default to a generic service name
    return "Service"


def analyze_typescript_file(file_path: str) -> str:
    """
    Analyze a TypeScript/JavaScript file and generate a sequence diagram.
    
    Args:
        file_path: Path to the TypeScript/JavaScript file
        
    Returns:
        str: Mermaid.js syntax for a sequence diagram
    """
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    return analyze_typescript_code(code)


def analyze_typescript_code(code: str) -> str:
    """
    Analyze TypeScript/JavaScript code and generate a sequence diagram.
    
    Args:
        code: TypeScript/JavaScript source code
        
    Returns:
        str: Mermaid.js syntax for a sequence diagram
    """
    # Extract method calls
    method_calls = extract_method_calls(code)
    
    # Enhance method calls with inferred callee information
    enhanced_calls = extract_callee_from_ts_method_calls(method_calls)
    
    # Generate the sequence diagram
    return generate_sequence_diagram(enhanced_calls) 