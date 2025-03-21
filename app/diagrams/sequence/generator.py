"""
Sequence diagram generator for visualizing method calls using Mermaid.js syntax.
"""
from typing import Dict, List, Any, Set, Optional


class SequenceDiagramGenerator:
    """
    Generator for creating sequence diagrams in Mermaid.js syntax
    from method call data.
    """
    
    def __init__(self):
        """Initialize the sequence diagram generator."""
        self.diagram_syntax = ""
        self.participants = set()
        self.conditional_blocks = []
        self.current_conditional = None
    
    def generate(self, method_calls: List[Dict[str, Any]]) -> str:
        """
        Generate a sequence diagram using the provided method calls.
        
        Args:
            method_calls: List of method call dictionaries 
            
        Returns:
            str: Mermaid.js syntax for the sequence diagram
        """
        # Start with the diagram header
        self.diagram_syntax = "sequenceDiagram\n"
        self.participants = set()
        
        # Sort method calls by line number for proper sequence
        sorted_calls = sorted(method_calls, key=lambda call: call.get('lineno', 0))
        
        # Extract all participants from method calls
        for call in sorted_calls:
            self.participants.add(call.get('caller', 'Unknown'))
            if 'callee' in call:
                self.participants.add(call['callee'])
        
        # Add participants to diagram
        for participant in self.participants:
            self.diagram_syntax += f"    participant {participant}\n"
        
        # Process method calls and generate diagram elements
        for call in sorted_calls:
            self._process_call(call)
            
        # Close any open conditional blocks
        if self.conditional_blocks:
            for _ in self.conditional_blocks:
                self.diagram_syntax += "    end\n"
                
        return self.diagram_syntax
    
    def _process_call(self, call: Dict[str, Any]):
        """
        Process a single method call and add it to the diagram.
        
        Args:
            call: Method call dictionary
        """
        # Handle conditional blocks
        if 'condition' in call:
            self._handle_conditional(call)
        
        caller = call.get('caller', 'Unknown')
        callee = call.get('callee', caller)
        method = call.get('method', '')
        args = call.get('args', [])
        
        # Format arguments
        args_str = ', '.join(str(arg) for arg in args)
        
        # Determine arrow type based on synchronicity
        arrow = '-)'  if call.get('is_async', False) else '->>'
        
        # Special handling for object creation
        if call.get('is_creation', False):
            message = f"new {callee}({args_str})"
            # Use activation notation for new objects
            self.diagram_syntax += f"    {caller}{arrow}+{callee}: {message}\n"
        else:
            message = f"{method}({args_str})"
            self.diagram_syntax += f"    {caller}{arrow}{callee}: {message}\n"
        
        # Add return arrow if return value exists
        if 'returns' in call:
            return_value = call['returns']
            self.diagram_syntax += f"    {callee}-->>{'same-' if callee == caller else ''}{caller}: return {return_value}\n"
    
    def _handle_conditional(self, call: Dict[str, Any]):
        """
        Handle conditional blocks in the sequence diagram.
        
        Args:
            call: Method call dictionary with a condition
        """
        condition = call['condition']
        
        # Only add the condition block if it's a new condition
        if not self.conditional_blocks or condition != self.conditional_blocks[-1]:
            # Close previous condition if there was one
            if self.conditional_blocks:
                self.diagram_syntax += "    end\n"
            
            # Add new condition
            self.diagram_syntax += f"    alt {condition}\n"
            self.conditional_blocks.append(condition)


def generate_sequence_diagram(method_calls: List[Dict[str, Any]]) -> str:
    """
    Generate a sequence diagram using Mermaid.js syntax from method calls.
    
    Args:
        method_calls: List of dictionaries containing method call information
        
    Returns:
        str: Mermaid.js syntax string for the sequence diagram
    """
    generator = SequenceDiagramGenerator()
    return generator.generate(method_calls)


def create_sequence_diagram_from_code(method_calls: List[Dict[str, Any]], 
                                     object_creations: List[Dict[str, Any]] = None) -> str:
    """
    Create a sequence diagram from a combination of method calls and object creations.
    
    Args:
        method_calls: List of method call dictionaries
        object_creations: List of object creation dictionaries
        
    Returns:
        str: Mermaid.js syntax for the sequence diagram
    """
    # Combine method calls and object creations into a single timeline
    combined_calls = list(method_calls)
    
    if object_creations:
        for creation in object_creations:
            # Transform object creation into a method call format
            call = {
                'caller': creation.get('target', 'Client'),
                'method': creation.get('class', 'Constructor'),
                'args': creation.get('args', []),
                'callee': creation.get('class', 'Unknown'),
                'is_creation': True,
                'lineno': creation.get('lineno', 0)
            }
            combined_calls.append(call)
    
    return generate_sequence_diagram(combined_calls) 