"""
Module for detecting conditional programming patterns in TypeScript/JavaScript code.

This module analyzes TypeScript/JavaScript code to identify various conditional programming
patterns, including if statements, ternary operators, switch-case, loops with conditions,
and try-catch blocks.
"""
import re
from typing import Dict, List, Any, Optional


def detect_conditional_patterns(source_code: str) -> List[Dict[str, Any]]:
    """
    Detect conditional programming patterns in TypeScript/JavaScript source code.
    
    This function uses regular expressions to identify conditional patterns
    in TypeScript/JavaScript code, including if statements, ternary operators,
    switch-case statements, and other conditional control flows.
    
    Args:
        source_code: TypeScript/JavaScript source code to analyze
    
    Returns:
        list: List of dictionaries with conditional pattern information
    """
    patterns = []
    
    # Find if statements with else
    if_else_pattern = r'if\s*\(([^)]+)\)(?:\s*{[^}]*}|\s*[^{};]+;)\s*else(?:\s*{[^}]*}|\s*[^{};]+;)'
    for match in re.finditer(if_else_pattern, source_code):
        condition = match.group(1).strip()
        patterns.append({
            'type': 'if_statement',
            'condition': condition,
            'has_else': True,
            'lineno': _get_line_number(source_code, match.start())
        })
    
    # Find if statements without else
    if_pattern = r'if\s*\(([^)]+)\)(?:\s*{[^}]*}|\s*[^{};]+;)(?!\s*else)'
    for match in re.finditer(if_pattern, source_code):
        condition = match.group(1).strip()
        patterns.append({
            'type': 'if_statement',
            'condition': condition,
            'has_else': False,
            'lineno': _get_line_number(source_code, match.start())
        })
    
    # Find if-else if-else chains
    # Look for patterns like: if (...) ... else if (...) ... else ...
    if_else_if_chain_pattern = r'if\s*\([^)]+\)(?:\s*{[^}]*}|\s*[^{};]+;)\s*else\s+if\s*\([^)]+\)'
    
    for match in re.finditer(if_else_if_chain_pattern, source_code):
        start_pos = match.start()
        # Find the start of this chain
        line_start = source_code[:start_pos].rfind('\n')
        if line_start == -1:
            line_start = 0
        
        # Extract the full chain text
        chain_text = _extract_full_if_chain(source_code, start_pos)
        
        # Count the number of else if branches
        else_if_count = chain_text.count('else if')
        has_else = 'else {' in chain_text or 'else ' in chain_text and 'else if' not in chain_text[chain_text.rfind('else '):]
        
        # Try to extract the first condition
        condition_match = re.search(r'if\s*\(([^)]+)\)', chain_text)
        condition = condition_match.group(1).strip() if condition_match else "complex_condition"
        
        patterns.append({
            'type': 'if_else_if_chain',
            'branches': else_if_count + 1,  # if + else if count
            'condition': condition,
            'has_else': has_else,
            'lineno': _get_line_number(source_code, start_pos)
        })
    
    # Find ternary operators
    ternary_pattern = r'([^?:]+)\s*\?\s*([^:]+)\s*:\s*([^;]+)'
    for match in re.finditer(ternary_pattern, source_code):
        condition = match.group(1).strip()
        if '?' in condition:  # Skip if this is likely part of another ternary or a complex expression
            continue
            
        patterns.append({
            'type': 'ternary',
            'condition': condition,
            'lineno': _get_line_number(source_code, match.start())
        })
    
    # Find switch-case statements
    switch_pattern = r'switch\s*\(([^)]+)\)\s*{([^}]*)}'
    for match in re.finditer(switch_pattern, source_code):
        switch_expr = match.group(1).strip()
        case_body = match.group(2)
        
        # Count case statements
        case_count = len(re.findall(r'case\s+', case_body))
        has_default = 'default:' in case_body or 'default :' in case_body
        
        patterns.append({
            'type': 'switch_case',
            'switch_expression': switch_expr,
            'cases': case_count,
            'has_default': has_default,
            'lineno': _get_line_number(source_code, match.start())
        })
    
    # Find for loops
    for_loop_pattern = r'for\s*\(([^)]+)\)\s*{'
    for match in re.finditer(for_loop_pattern, source_code):
        loop_condition = match.group(1).strip()
        
        if 'of ' in loop_condition:  # for...of loop
            patterns.append({
                'type': 'for_of_loop',
                'condition': loop_condition,
                'lineno': _get_line_number(source_code, match.start())
            })
        elif 'in ' in loop_condition:  # for...in loop
            patterns.append({
                'type': 'for_in_loop',
                'condition': loop_condition,
                'lineno': _get_line_number(source_code, match.start())
            })
        else:  # regular for loop
            patterns.append({
                'type': 'for_loop',
                'condition': loop_condition,
                'lineno': _get_line_number(source_code, match.start())
            })
    
    # Find while loops
    while_loop_pattern = r'while\s*\(([^)]+)\)\s*{'
    for match in re.finditer(while_loop_pattern, source_code):
        condition = match.group(1).strip()
        patterns.append({
            'type': 'while_loop',
            'condition': condition,
            'lineno': _get_line_number(source_code, match.start())
        })
    
    # Find do-while loops
    do_while_pattern = r'do\s*{[^}]*}\s*while\s*\(([^)]+)\)'
    for match in re.finditer(do_while_pattern, source_code):
        condition = match.group(1).strip()
        patterns.append({
            'type': 'do_while_loop',
            'condition': condition,
            'lineno': _get_line_number(source_code, match.start())
        })
    
    # Find conditional break statements
    if_break_pattern = r'if\s*\(([^)]+)\)\s*{[^}]*break;[^}]*}'
    for match in re.finditer(if_break_pattern, source_code):
        condition = match.group(1).strip()
        patterns.append({
            'type': 'if_break',
            'condition': condition,
            'lineno': _get_line_number(source_code, match.start())
        })
    
    # Find conditional continue statements
    if_continue_pattern = r'if\s*\(([^)]+)\)\s*{[^}]*continue;[^}]*}'
    for match in re.finditer(if_continue_pattern, source_code):
        condition = match.group(1).strip()
        patterns.append({
            'type': 'if_continue',
            'condition': condition,
            'lineno': _get_line_number(source_code, match.start())
        })
    
    # Find try-catch blocks
    try_catch_pattern = r'try\s*{[^}]*}\s*catch\s*\(([^)]*)\)\s*{'
    for match in re.finditer(try_catch_pattern, source_code):
        error_var = match.group(1).strip()
        
        # Check if there's also a finally block
        full_text = source_code[match.start():]
        has_finally = re.search(r'}\s*catch\s*\([^)]*\)\s*{[^}]*}\s*finally\s*{', full_text) is not None
        
        patterns.append({
            'type': 'try_catch',
            'error_variable': error_var,
            'has_finally': has_finally,
            'lineno': _get_line_number(source_code, match.start())
        })
    
    # Find nullish coalescing operators
    nullish_pattern = r'([^?]+?)\s*\?\?\s*([^;]+)'
    for match in re.finditer(nullish_pattern, source_code):
        left = match.group(1).strip()
        right = match.group(2).strip()
        
        patterns.append({
            'type': 'nullish_coalescing',
            'left': left,
            'right': right,
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


def _extract_full_if_chain(source_code: str, if_start_pos: int) -> str:
    """
    Extract the entire if-else if-else chain starting from an if statement.
    
    Args:
        source_code: The source code string
        if_start_pos: Starting position of the if statement
        
    Returns:
        str: The full if chain
    """
    # This is a simplified extraction that might not handle all edge cases
    # like nested braces correctly. A proper parser would be better.
    
    # Find the open brace of the if block
    rest_of_code = source_code[if_start_pos:]
    
    # Get a reasonable chunk of code that should contain the full chain
    # This is a simplification and might miss very long chains
    code_chunk = rest_of_code[:1000]
    
    # Find the matching closing brace for the first if
    # This is a simplified approach and might fail with complex nested structures
    brace_count = 0
    in_string = False
    string_char = None
    
    for i, char in enumerate(code_chunk):
        if char in '"\'`' and (i == 0 or code_chunk[i-1] != '\\'):
            if not in_string:
                in_string = True
                string_char = char
            elif char == string_char:
                in_string = False
        
        if not in_string:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    break
    
    # Return the if chain up to the point where we've closed all braces
    # or the whole chunk if we couldn't find a clear end
    return code_chunk[:i+1] if i < len(code_chunk) else code_chunk 