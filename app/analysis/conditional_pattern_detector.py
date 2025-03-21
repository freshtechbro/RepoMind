"""
Module for detecting conditional programming patterns in Python code.

This module analyzes Python AST to identify various conditional programming patterns,
including if statements, ternary operators, loops with conditions, and try-except blocks.
"""
import ast
from typing import Dict, List, Any, Optional


class ConditionalPatternDetector(ast.NodeVisitor):
    """
    Detect conditional programming patterns using the Visitor pattern.
    
    This detector identifies various conditional patterns in Python code and collects
    information about them, including if statements, ternary operators, loops with
    conditional branches, and try-except blocks.
    """
    
    def __init__(self):
        """Initialize the detector with empty patterns list."""
        self.patterns = []
        self.current_function = None
        self.nesting_level = 0
        
    def visit_FunctionDef(self, node):
        """
        Visit FunctionDef nodes to track current function.
        
        Args:
            node: The AST FunctionDef node to visit
        """
        prev_function = self.current_function
        self.current_function = node.name
        
        # Visit function body
        self.generic_visit(node)
        self.current_function = prev_function
        
    def visit_If(self, node):
        """
        Visit If nodes to detect if statements and if-elif chains.
        
        Args:
            node: The AST If node to visit
        """
        # Increment nesting level for nested conditions
        self.nesting_level += 1
        
        # Check if this is part of an if-elif chain
        is_elif = _is_part_of_elif_chain(node)
        
        # If this is the start of an if-elif chain, process the entire chain
        if not is_elif:
            # Check if this is the start of an if-elif chain
            elif_count, has_else = _count_elif_branches(node)
            
            if elif_count > 0:
                # This is an if-elif chain
                condition_text = _extract_condition_text(node.test)
                
                self.patterns.append({
                    'type': 'if_elif_chain',
                    'branches': elif_count + 1,  # if + elif count
                    'condition': condition_text,
                    'has_else': has_else,
                    'function': self.current_function,
                    'lineno': node.lineno,
                    'col_offset': node.col_offset,
                    'nesting_level': self.nesting_level - 1  # Adjust for the increment
                })
            else:
                # This is a simple if statement
                condition_text = _extract_condition_text(node.test)
                has_else = len(node.orelse) > 0
                
                self.patterns.append({
                    'type': 'if_statement',
                    'condition': condition_text,
                    'has_else': has_else,
                    'function': self.current_function,
                    'lineno': node.lineno,
                    'col_offset': node.col_offset,
                    'nesting_level': self.nesting_level - 1  # Adjust for the increment
                })
                
                # Check if this is a conditional break or continue
                if _contains_break(node.body):
                    self.patterns.append({
                        'type': 'if_break',
                        'condition': condition_text,
                        'function': self.current_function,
                        'lineno': node.lineno,
                        'col_offset': node.col_offset,
                        'nesting_level': self.nesting_level - 1
                    })
                
                if _contains_continue(node.body):
                    self.patterns.append({
                        'type': 'if_continue',
                        'condition': condition_text,
                        'function': self.current_function,
                        'lineno': node.lineno,
                        'col_offset': node.col_offset,
                        'nesting_level': self.nesting_level - 1
                    })
        
        # Visit the body and else clause
        self.generic_visit(node)
        
        # Decrement nesting level
        self.nesting_level -= 1
        
    def visit_IfExp(self, node):
        """
        Visit IfExp nodes to detect ternary operators.
        
        Args:
            node: The AST IfExp node to visit
        """
        condition_text = _extract_condition_text(node.test)
        
        self.patterns.append({
            'type': 'ternary',
            'condition': condition_text,
            'function': self.current_function,
            'lineno': node.lineno,
            'col_offset': node.col_offset
        })
        
        # Continue visiting for nested patterns
        self.generic_visit(node)
        
    def visit_For(self, node):
        """
        Visit For nodes to detect for loops.
        
        Args:
            node: The AST For node to visit
        """
        target_text = _extract_name(node.target)
        iter_text = _extract_name(node.iter)
        
        self.patterns.append({
            'type': 'for_loop',
            'target': target_text,
            'iterable': iter_text,
            'has_else': len(node.orelse) > 0,
            'function': self.current_function,
            'lineno': node.lineno,
            'col_offset': node.col_offset
        })
        
        # Continue visiting for nested patterns
        self.generic_visit(node)
        
    def visit_While(self, node):
        """
        Visit While nodes to detect while loops.
        
        Args:
            node: The AST While node to visit
        """
        condition_text = _extract_condition_text(node.test)
        
        self.patterns.append({
            'type': 'while_loop',
            'condition': condition_text,
            'has_else': len(node.orelse) > 0,
            'function': self.current_function,
            'lineno': node.lineno,
            'col_offset': node.col_offset
        })
        
        # Continue visiting for nested patterns
        self.generic_visit(node)
        
    def visit_Try(self, node):
        """
        Visit Try nodes to detect try-except blocks.
        
        Args:
            node: The AST Try node to visit
        """
        self.patterns.append({
            'type': 'try_except',
            'has_handlers': len(node.handlers) > 0,
            'has_else': len(node.orelse) > 0,
            'has_finally': len(node.finalbody) > 0,
            'function': self.current_function,
            'lineno': node.lineno,
            'col_offset': node.col_offset
        })
        
        # Continue visiting for nested patterns
        self.generic_visit(node)


def _is_part_of_elif_chain(node):
    """
    Check if this If node is part of an if-elif chain.
    
    Args:
        node: The AST If node to check
        
    Returns:
        bool: True if this is part of an elif chain (not the start)
    """
    # In the AST, elif clauses are represented as If nodes in the orelse of the parent If
    # We can't easily determine this from the node itself without context
    return False  # This is a simplification


def _count_elif_branches(node):
    """
    Count the number of elif branches in an if-elif chain.
    
    Args:
        node: The AST If node that starts the chain
        
    Returns:
        tuple: (number of elif branches, whether there's a final else clause)
    """
    elif_count = 0
    has_else = False
    
    # Check orelse for elif branches
    current = node
    while len(current.orelse) == 1 and isinstance(current.orelse[0], ast.If):
        elif_count += 1
        current = current.orelse[0]
    
    # Check for final else clause
    has_else = len(current.orelse) > 0
    
    return elif_count, has_else


def _extract_condition_text(node):
    """
    Extract a readable representation of a condition expression.
    
    Args:
        node: The AST node representing the condition
        
    Returns:
        str: A readable representation of the condition
    """
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        return f"{_extract_condition_text(node.value)}.{node.attr}"
    elif isinstance(node, ast.Compare):
        left = _extract_condition_text(node.left)
        ops = []
        for i, op in enumerate(node.ops):
            op_str = _get_compare_op_symbol(op)
            right = _extract_condition_text(node.comparators[i])
            ops.append(f"{op_str} {right}")
        return f"{left} {' '.join(ops)}"
    elif isinstance(node, ast.BoolOp):
        op_str = "and" if isinstance(node.op, ast.And) else "or"
        values = [_extract_condition_text(val) for val in node.values]
        return f" {op_str} ".join(values)
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return f"not {_extract_condition_text(node.operand)}"
    elif isinstance(node, ast.Call):
        func = _extract_condition_text(node.func)
        return f"{func}(...)"
    elif isinstance(node, ast.Constant):
        return repr(node.value)
    
    # Fallback
    return "complex_condition"


def _get_compare_op_symbol(op):
    """
    Get the string representation of a comparison operator.
    
    Args:
        op: The AST comparison operator
        
    Returns:
        str: String representation of the operator
    """
    if isinstance(op, ast.Eq):
        return "=="
    elif isinstance(op, ast.NotEq):
        return "!="
    elif isinstance(op, ast.Lt):
        return "<"
    elif isinstance(op, ast.LtE):
        return "<="
    elif isinstance(op, ast.Gt):
        return ">"
    elif isinstance(op, ast.GtE):
        return ">="
    elif isinstance(op, ast.Is):
        return "is"
    elif isinstance(op, ast.IsNot):
        return "is not"
    elif isinstance(op, ast.In):
        return "in"
    elif isinstance(op, ast.NotIn):
        return "not in"
    
    return "op"


def _extract_name(node):
    """
    Extract a readable name from an AST node.
    
    Args:
        node: The AST node
        
    Returns:
        str: A readable name
    """
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        return f"{_extract_name(node.value)}.{node.attr}"
    elif isinstance(node, ast.Tuple):
        elements = [_extract_name(elt) for elt in node.elts]
        return f"({', '.join(elements)})"
    elif isinstance(node, ast.Call):
        func = _extract_name(node.func)
        return f"{func}(...)"
    
    return "complex_expression"


def _contains_break(body):
    """
    Check if a body contains a break statement.
    
    Args:
        body: List of AST nodes
        
    Returns:
        bool: True if the body contains a break statement
    """
    for node in body:
        if isinstance(node, ast.Break):
            return True
        elif isinstance(node, ast.If):
            if _contains_break(node.body) or _contains_break(node.orelse):
                return True
    
    return False


def _contains_continue(body):
    """
    Check if a body contains a continue statement.
    
    Args:
        body: List of AST nodes
        
    Returns:
        bool: True if the body contains a continue statement
    """
    for node in body:
        if isinstance(node, ast.Continue):
            return True
        elif isinstance(node, ast.If):
            if _contains_continue(node.body) or _contains_continue(node.orelse):
                return True
    
    return False


def detect_conditional_patterns(source_code: str) -> List[Dict[str, Any]]:
    """
    Detect conditional programming patterns in Python source code.
    
    Args:
        source_code: Python source code to analyze
    
    Returns:
        list: List of dictionaries with conditional pattern information
    
    Raises:
        SyntaxError: If the provided source code has syntax errors
    """
    try:
        tree = ast.parse(source_code)
        detector = ConditionalPatternDetector()
        detector.visit(tree)
        return detector.patterns
    except SyntaxError as e:
        # Re-raise with more context
        raise SyntaxError(f"Failed to parse Python code: {e}") 