"""
Module for detecting asynchronous programming patterns in TypeScript code.

This module analyzes TypeScript code to identify various asynchronous programming
patterns, including async/await syntax, Promises, callbacks, and other async
control flow mechanisms in JavaScript/TypeScript.
"""
import ast
import re
from typing import Dict, List, Any, Optional


def detect_async_patterns(source_code: str) -> List[Dict[str, Any]]:
    """
    Detect asynchronous programming patterns in TypeScript source code.
    
    This function uses regular expressions to identify async patterns in
    TypeScript code, including async/await syntax, Promise usage, and
    other asynchronous patterns.
    
    Args:
        source_code: TypeScript source code to analyze
    
    Returns:
        list: List of dictionaries with async pattern information
    """
    patterns = []
    
    # Find async functions
    async_func_pattern = r'async\s+function\s+(\w+)'
    for match in re.finditer(async_func_pattern, source_code):
        patterns.append({
            'type': 'async_function',
            'name': match.group(1),
            'lineno': _get_line_number(source_code, match.start())
        })
    
    # Find async arrow functions
    async_arrow_pattern = r'const\s+(\w+)\s+=\s+async\s*\('
    for match in re.finditer(async_arrow_pattern, source_code):
        patterns.append({
            'type': 'async_arrow_function',
            'name': match.group(1),
            'lineno': _get_line_number(source_code, match.start())
        })
    
    # Find async class methods
    async_method_pattern = r'async\s+(\w+)\s*\('
    class_pattern = r'class\s+(\w+)'
    class_matches = list(re.finditer(class_pattern, source_code))
    
    for i, class_match in enumerate(class_matches):
        class_name = class_match.group(1)
        class_start = class_match.start()
        
        # Find the end of the class (either the next class or the end of the file)
        class_end = len(source_code)
        if i < len(class_matches) - 1:
            class_end = class_matches[i+1].start()
        
        class_body = source_code[class_start:class_end]
        
        for method_match in re.finditer(async_method_pattern, class_body):
            method_name = method_match.group(1)
            patterns.append({
                'type': 'async_method',
                'class': class_name,
                'method': method_name,
                'lineno': _get_line_number(source_code, class_start + method_match.start())
            })
    
    # Find await expressions
    await_pattern = r'await\s+(\w+)(?:\(|\.)'
    for match in re.finditer(await_pattern, source_code):
        # Try to determine the containing function
        containing_function = _find_containing_function(source_code, match.start())
        patterns.append({
            'type': 'await_expression',
            'function': containing_function,
            'awaited': match.group(1),
            'lineno': _get_line_number(source_code, match.start())
        })
    
    # Find Promise.then calls
    then_pattern = r'(\w+)\.then\s*\('
    for match in re.finditer(then_pattern, source_code):
        patterns.append({
            'type': 'promise_then',
            'caller': match.group(1),
            'lineno': _get_line_number(source_code, match.start())
        })
    
    # Find Promise.catch calls
    catch_pattern = r'(\w+)\.catch\s*\('
    for match in re.finditer(catch_pattern, source_code):
        patterns.append({
            'type': 'promise_catch',
            'caller': match.group(1),
            'lineno': _get_line_number(source_code, match.start())
        })
    
    # Find Promise constructor usage
    promise_constructor_pattern = r'new\s+Promise\s*\('
    for match in re.finditer(promise_constructor_pattern, source_code):
        containing_function = _find_containing_function(source_code, match.start())
        patterns.append({
            'type': 'promise_constructor',
            'function': containing_function,
            'lineno': _get_line_number(source_code, match.start())
        })
    
    # Find Promise.all
    promise_all_pattern = r'Promise\.all\s*\('
    for match in re.finditer(promise_all_pattern, source_code):
        patterns.append({
            'type': 'promise_all',
            'lineno': _get_line_number(source_code, match.start())
        })
    
    # Find Promise.race
    promise_race_pattern = r'Promise\.race\s*\('
    for match in re.finditer(promise_race_pattern, source_code):
        patterns.append({
            'type': 'promise_race',
            'lineno': _get_line_number(source_code, match.start())
        })
    
    # Sort patterns by line number
    patterns.sort(key=lambda p: p.get('lineno', 0))
    
    return patterns


def _get_line_number(source_code: str, position: int) -> int:
    """
    Get line number for a position in the source code.
    
    Args:
        source_code: The source code string
        position: Character position within the source code
        
    Returns:
        int: Line number (1-based)
    """
    return source_code[:position].count('\n') + 1


def _find_containing_function(source_code: str, position: int) -> Optional[str]:
    """
    Find the name of the function containing the given position.
    
    This is a simplified implementation that looks for function declarations
    before the position.
    
    Args:
        source_code: The source code string
        position: Character position within the source code
        
    Returns:
        str or None: The containing function name if found
    """
    # This is a simplified approach that looks for the closest function declaration above
    code_before = source_code[:position]
    
    # Try to find async function declarations
    func_matches = list(re.finditer(r'(async\s+)?function\s+(\w+)', code_before))
    
    # Try to find arrow function declarations
    arrow_matches = list(re.finditer(r'const\s+(\w+)\s+=\s+(async\s+)?\(\)', code_before))
    
    # Try to find method declarations within classes
    method_matches = list(re.finditer(r'(async\s+)?(\w+)\s*\([^)]*\)\s*{', code_before))
    
    # Combine all matches and find the closest one
    all_matches = []
    
    for match in func_matches:
        all_matches.append({
            'name': match.group(2),
            'position': match.start()
        })
    
    for match in arrow_matches:
        all_matches.append({
            'name': match.group(1),
            'position': match.start()
        })
    
    for match in method_matches:
        all_matches.append({
            'name': match.group(2),
            'position': match.start()
        })
    
    if not all_matches:
        return None
    
    # Find the closest declaration
    closest = max(all_matches, key=lambda m: m['position'])
    return closest['name'] 