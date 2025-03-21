"""
Module for extracting method calls and other information from Python AST.
"""
import ast
from typing import Dict, List, Any, Optional


class MethodCallExtractor(ast.NodeVisitor):
    """
    Extract method calls from Python AST using the Visitor pattern.
    
    This extractor identifies method calls in Python code and collects
    information about the caller, method name, arguments, and source location.
    """
    
    def __init__(self):
        """Initialize the extractor with an empty call list."""
        self.calls = []
        
    def visit_Call(self, node):
        """
        Visit Call nodes in the AST to extract method calls.
        
        Args:
            node: The AST Call node to visit
        """
        # Extract method call information if it's a method call (obj.method())
        if isinstance(node.func, ast.Attribute):
            # This is a method call (e.g., obj.method())
            caller = self._extract_caller(node.func.value)
            method_name = node.func.attr
            args = self._extract_args(node.args)
            
            self.calls.append({
                'caller': caller,
                'method': method_name,
                'args': args,
                'lineno': node.lineno,
                'col_offset': node.col_offset
            })
        
        # Continue traversing the tree (for nested calls)
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
        elif isinstance(node, ast.Call):
            # This handles method chaining (obj.method1().method2())
            # In this case, we represent it as the result of the prior call
            return "chainedCall"
        # Handle other cases like calls, subscripts, etc.
        return "unknown"
    
    def _extract_args(self, arg_nodes):
        """
        Extract argument values or representations from AST nodes.
        
        Args:
            arg_nodes: List of AST nodes representing arguments
            
        Returns:
            list: The extracted arguments
        """
        args = []
        for arg in arg_nodes:
            if isinstance(arg, ast.Constant):
                args.append(repr(arg.value))
            elif isinstance(arg, ast.Name):
                args.append(arg.id)
            elif isinstance(arg, ast.Call):
                # For nested calls, we'll record a placeholder
                if isinstance(arg.func, ast.Attribute):
                    args.append(f"{self._extract_caller(arg.func.value)}.{arg.func.attr}()")
                else:
                    args.append("nested_call()")
            elif isinstance(arg, ast.List):
                args.append("list_literal")
            elif isinstance(arg, ast.Dict):
                args.append("dict_literal")
            else:
                args.append("complex_expression")
        return args


class ObjectCreationExtractor(ast.NodeVisitor):
    """
    Extract object creation instances (class instantiations) from Python AST.
    """
    
    def __init__(self):
        """Initialize the extractor with an empty creation list."""
        self.creations = []
        # Keep track of parent nodes to identify assignments
        self._parent_stack = []
        
    def generic_visit(self, node):
        """
        Override generic_visit to track parent nodes.
        
        Args:
            node: The AST node to visit
        """
        # Push current node onto the stack
        self._parent_stack.append(node)
        # Visit all children
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        self.visit(item)
            elif isinstance(value, ast.AST):
                self.visit(value)
        # Remove current node from the stack
        self._parent_stack.pop()
        
    def visit_Call(self, node):
        """
        Visit Call nodes to extract object creations.
        
        Args:
            node: The AST Call node to visit
        """
        # Check if it's a class instantiation (likely if it's a Name node and PascalCase)
        if isinstance(node.func, ast.Name) and node.func.id[0].isupper():
            class_name = node.func.id
            args = self._extract_args(node.args)
            
            # Extract target of the assignment if available
            target = self._find_assignment_target(node)
            
            self.creations.append({
                'class': class_name,
                'args': args,
                'target': target,
                'lineno': node.lineno,
                'col_offset': node.col_offset
            })
        
        # Continue traversing the tree
        self.generic_visit(node)
    
    def _extract_args(self, arg_nodes):
        """
        Extract argument values from AST nodes.
        
        Args:
            arg_nodes: List of AST nodes representing arguments
            
        Returns:
            list: The extracted arguments
        """
        args = []
        for arg in arg_nodes:
            if isinstance(arg, ast.Constant):
                args.append(repr(arg.value))
            elif isinstance(arg, ast.Name):
                args.append(arg.id)
            else:
                args.append("complex_expression")
        return args
    
    def _find_assignment_target(self, node):
        """
        Find the target of an assignment if this node is part of one.
        
        Args:
            node: The AST node for a class instantiation Call
            
        Returns:
            str: The assignment target name or None
        """
        # Look at the parent nodes to find an assignment
        # We need to traverse up the stack starting from the most recent parent
        for parent in reversed(self._parent_stack):
            # Case 1: Direct assignment - variable = MyClass()
            if isinstance(parent, ast.Assign) and parent.value is node:
                # For multiple assignments like a = b = MyClass()
                # we return the first target (leftmost)
                if parent.targets:
                    return self._extract_target_name(parent.targets[0])
                
            # Case 2: Attribute assignment - self.var = MyClass()
            elif isinstance(parent, ast.AnnAssign) and parent.value is node:
                return self._extract_target_name(parent.target)
                
            # Case 3: As part of a method call argument
            # Not an assignment target, so continue
                
            # Case 4: As part of a dictionary value
            # In this case, the key isn't a "target" in the traditional sense
            
        return None
        
    def _extract_target_name(self, node):
        """
        Extract the name from an assignment target node.
        
        Args:
            node: The AST node representing an assignment target
            
        Returns:
            str: The extracted name
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            # For attribute assignments like 'self.logger'
            # Extract the base object and attribute
            base = self._extract_target_name(node.value)
            return f"{base}.{node.attr}" if base else node.attr
        elif isinstance(node, ast.Tuple) or isinstance(node, ast.List):
            # For tuple unpacking, we just take the first element
            # This is a simplification, in reality we would need more context
            if node.elts:
                return self._extract_target_name(node.elts[0])
        elif isinstance(node, ast.Subscript):
            # For dictionary or list assignments like 'dict[key]'
            # We don't consider these as proper targets
            return None
        
        return None


def extract_method_calls(source_code: str) -> List[Dict[str, Any]]:
    """
    Extract method calls from Python source code.
    
    Args:
        source_code: Python source code to analyze
    
    Returns:
        list: List of dictionaries with method call information
    
    Raises:
        SyntaxError: If the provided source code has syntax errors
    """
    try:
        tree = ast.parse(source_code)
        extractor = MethodCallExtractor()
        extractor.visit(tree)
        return extractor.calls
    except SyntaxError as e:
        # Re-raise with more context
        raise SyntaxError(f"Failed to parse Python code: {e}")


def extract_object_creations(source_code: str) -> List[Dict[str, Any]]:
    """
    Extract object creation instances from Python source code.
    
    Args:
        source_code: Python source code to analyze
    
    Returns:
        list: List of dictionaries with object creation information
    
    Raises:
        SyntaxError: If the provided source code has syntax errors
    """
    try:
        tree = ast.parse(source_code)
        extractor = ObjectCreationExtractor()
        extractor.visit(tree)
        return extractor.creations
    except SyntaxError as e:
        # Re-raise with more context
        raise SyntaxError(f"Failed to parse Python code: {e}") 