"""
Module for detecting asynchronous programming patterns in Python code.

This module analyzes Python AST to identify various asynchronous programming
patterns, including async/await syntax, promise-like patterns, callbacks,
threading, and asyncio usage.
"""
import ast
from typing import Dict, List, Any, Optional


class AsyncPatternDetector(ast.NodeVisitor):
    """
    Detect asynchronous programming patterns using the Visitor pattern.
    
    This detector identifies various async patterns in Python code and collects
    information about them, including async functions, await expressions,
    callbacks, threading, and asyncio usage.
    """
    
    def __init__(self):
        """Initialize the detector with empty patterns list."""
        self.patterns = []
        self.current_class = None
        self.current_function = None
        
    def visit_AsyncFunctionDef(self, node):
        """
        Visit AsyncFunctionDef nodes to detect async functions.
        
        Args:
            node: The AST AsyncFunctionDef node to visit
        """
        prev_function = self.current_function
        self.current_function = node.name
        
        if self.current_class:
            self.patterns.append({
                'type': 'async_method',
                'class': self.current_class,
                'method': node.name,
                'lineno': node.lineno,
                'col_offset': node.col_offset
            })
        else:
            self.patterns.append({
                'type': 'async_function',
                'name': node.name,
                'lineno': node.lineno,
                'col_offset': node.col_offset
            })
        
        # Visit the body to find await expressions and other patterns
        self.generic_visit(node)
        self.current_function = prev_function
        
    def visit_Await(self, node):
        """
        Visit Await nodes to detect await expressions.
        
        Args:
            node: The AST Await node to visit
        """
        self.patterns.append({
            'type': 'await_expression',
            'function': self.current_function,
            'lineno': node.lineno,
            'col_offset': node.col_offset
        })
        
        # Continue visiting to detect awaited function
        self.generic_visit(node)
        
    def visit_ClassDef(self, node):
        """
        Visit ClassDef nodes to track current class for method context.
        
        Args:
            node: The AST ClassDef node to visit
        """
        prev_class = self.current_class
        self.current_class = node.name
        
        # Visit class body
        self.generic_visit(node)
        self.current_class = prev_class
        
    def visit_FunctionDef(self, node):
        """
        Visit FunctionDef nodes to track current function and detect callbacks.
        
        Args:
            node: The AST FunctionDef node to visit
        """
        prev_function = self.current_function
        self.current_function = node.name
        
        # Check for callback pattern (function with callback argument)
        for arg in node.args.args:
            if arg.arg == 'callback' or 'callback' in arg.arg.lower():
                self.patterns.append({
                    'type': 'callback_pattern',
                    'function': node.name,
                    'callback_arg': arg.arg,
                    'lineno': node.lineno,
                    'col_offset': node.col_offset
                })
        
        # Visit function body
        self.generic_visit(node)
        self.current_function = prev_function
        
    def visit_Call(self, node):
        """
        Visit Call nodes to detect various async patterns in function calls.
        
        Args:
            node: The AST Call node to visit
        """
        # Check for promise-like patterns (.then and .catch method calls)
        if isinstance(node.func, ast.Attribute) and node.func.attr in ['then', 'catch']:
            caller = self._extract_caller(node.func.value)
            self.patterns.append({
                'type': f'promise_{node.func.attr}',
                'caller': caller,
                'lineno': node.lineno,
                'col_offset': node.col_offset
            })
        
        # Check for threading patterns
        elif (isinstance(node.func, ast.Attribute) and 
              isinstance(node.func.value, ast.Name) and 
              node.func.value.id == 'threading' and
              node.func.attr == 'Thread'):
            
            # Look for target keyword argument
            for keyword in node.keywords:
                if keyword.arg == 'target':
                    if isinstance(keyword.value, ast.Name):
                        target_func = keyword.value.id
                        self.patterns.append({
                            'type': 'threading',
                            'target': target_func,
                            'lineno': node.lineno,
                            'col_offset': node.col_offset
                        })
        
        # Check for asyncio patterns
        elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            if node.func.value.id == 'asyncio':
                if node.func.attr == 'create_task':
                    self.patterns.append({
                        'type': 'create_task',
                        'function': self.current_function,
                        'lineno': node.lineno,
                        'col_offset': node.col_offset
                    })
                elif node.func.attr == 'gather':
                    self.patterns.append({
                        'type': 'asyncio_gather',
                        'function': self.current_function,
                        'lineno': node.lineno,
                        'col_offset': node.col_offset
                    })
                elif node.func.attr == 'run':
                    self.patterns.append({
                        'type': 'asyncio_run',
                        'function': self.current_function,
                        'lineno': node.lineno,
                        'col_offset': node.col_offset
                    })
                # Add other asyncio patterns here
        
        # Continue visiting for nested patterns
        self.generic_visit(node)
    
    def _extract_caller(self, node):
        """
        Extract the name of the caller object from an AST node.
        
        Args:
            node: The AST node representing the caller object
            
        Returns:
            str: The extracted caller name
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            base = self._extract_caller(node.value)
            return f"{base}.{node.attr}"
        # Handle other cases
        return "unknown"


def detect_async_patterns(source_code: str) -> List[Dict[str, Any]]:
    """
    Detect asynchronous programming patterns in Python source code.
    
    Args:
        source_code: Python source code to analyze
    
    Returns:
        list: List of dictionaries with async pattern information
    
    Raises:
        SyntaxError: If the provided source code has syntax errors
    """
    try:
        tree = ast.parse(source_code)
        detector = AsyncPatternDetector()
        detector.visit(tree)
        return detector.patterns
    except SyntaxError as e:
        # Re-raise with more context
        raise SyntaxError(f"Failed to parse Python code: {e}") 