"""
Module for ordering method calls into sequences for diagram generation.

This module provides functionality to transform hierarchical call graphs
into flat, ordered sequences suitable for sequence diagram generation.
"""

from typing import List, Dict, Any, Set, Optional
from app.analysis.call_graph_builder import CallGraphNode


class SequenceItem:
    """
    Represents an item in an ordered sequence diagram.
    
    This class contains the information needed to render a method call
    in a sequence diagram.
    """
    
    def __init__(self, caller: str, method: str, args: List[Any], lineno: int):
        """
        Initialize a sequence item.
        
        Args:
            caller: The name of the caller object/function
            method: The name of the method being called
            args: List of arguments passed to the method
            lineno: Line number where the call occurs
        """
        self.caller = caller
        self.method = method
        self.args = args
        self.lineno = lineno
        self.is_cycle_ref: bool = False
        self.is_async: bool = False
        self.is_conditional: bool = False
        self.condition: str = ""
        self.depth: int = 0  # Nesting depth in the sequence
        self.is_object_creation: bool = False
        self.target_object: Optional[str] = None
        
    def __repr__(self) -> str:
        """Return a string representation of the sequence item."""
        async_str = " async" if self.is_async else ""
        cycle_str = " cycle_ref" if self.is_cycle_ref else ""
        create_str = " creation" if self.is_object_creation else ""
        target_str = f" -> {self.target_object}" if self.target_object else ""
        cond_str = f" ({self.condition})" if self.is_conditional else ""
        return f"SequenceItem({self.caller}.{self.method}{async_str}{cycle_str}{create_str}{target_str}{cond_str})"


def order_sequence_from_call_graph(root_nodes: List[CallGraphNode]) -> List[SequenceItem]:
    """
    Transform a call graph into an ordered sequence for diagram generation.
    
    Args:
        root_nodes: List of root nodes in the call graph
        
    Returns:
        List of SequenceItem objects in execution order
    """
    sequence: List[SequenceItem] = []
    processed_nodes: Set[str] = set()  # Track processed nodes to prevent infinite recursion
    
    # Sort root nodes by line number to ensure consistent ordering
    sorted_roots = sorted(root_nodes, key=lambda node: node.lineno)
    
    def process_node(node: CallGraphNode, depth: int = 0) -> None:
        """
        Process a node and its children recursively to build the sequence.
        
        Args:
            node: The current CallGraphNode to process
            depth: The current nesting depth in the sequence
        """
        # Create a unique ID for this node
        node_id = f"{node.caller}.{node.method}"
        if node.is_object_creation:
            node_id = f"create.{node.method}.{node.lineno}"
        
        # Skip if we've already processed this node (cycle prevention)
        if node_id in processed_nodes and not node.is_cycle_ref:
            return
            
        # Mark this node as processed
        processed_nodes.add(node_id)
        
        # Create a sequence item for this node
        seq_item = SequenceItem(node.caller, node.method, node.args, node.lineno)
        seq_item.is_cycle_ref = node.is_cycle_ref
        seq_item.depth = depth
        
        # Copy all relevant properties
        seq_item.is_async = node.is_async
        seq_item.is_conditional = node.is_conditional
        seq_item.condition = node.condition
        seq_item.is_object_creation = node.is_object_creation
        seq_item.target_object = node.target_object
            
        # Add to the sequence
        sequence.append(seq_item)
        
        # If this is a cycle reference, don't process children
        if node.is_cycle_ref:
            return
            
        # Process children in order of line number
        sorted_children = sorted(node.children, key=lambda child: child.lineno)
        for child in sorted_children:
            process_node(child, depth + 1)
    
    # Process all root nodes in order
    for root in sorted_roots:
        process_node(root)
        
    return sequence


def enhance_sequence_with_object_creations(
    sequence: List[SequenceItem], 
    object_creations: List[Dict[str, Any]]
) -> List[SequenceItem]:
    """
    Enhance a sequence with object creation information.
    
    Args:
        sequence: List of SequenceItem objects
        object_creations: List of object creation dictionaries
        
    Returns:
        Enhanced list of SequenceItem objects with object creations
    """
    # First, build a map of objects that are used in the sequence
    used_objects = set()
    for item in sequence:
        # Extract the object from the caller
        parts = item.caller.split('.')
        obj = parts[0]
        used_objects.add(obj)
    
    # Create sequence items for object creations
    creation_items = []
    for creation in object_creations:
        target = creation.get('target')
        
        # Only add creations for objects that are used
        if target and target in used_objects:
            seq_item = SequenceItem(
                caller="Constructor",
                method=creation.get('class', 'UnknownClass'),
                args=creation.get('args', []),
                lineno=creation.get('lineno', 0)
            )
            seq_item.is_object_creation = True
            seq_item.target_object = target
            creation_items.append(seq_item)
    
    # Sort creation items by line number
    sorted_creations = sorted(creation_items, key=lambda item: item.lineno)
    
    # Merge creations with existing sequence
    # If creation line numbers are before the sequence, prepend them
    # Otherwise, insert them at the right position
    if not sorted_creations:
        return sequence
        
    result = []
    
    # Add creations that happen before the first sequence item
    first_seq_lineno = sequence[0].lineno if sequence else float('inf')
    prepend_creations = [c for c in sorted_creations if c.lineno < first_seq_lineno]
    result.extend(prepend_creations)
    
    # Process the rest of the items in order
    remaining_creations = [c for c in sorted_creations if c.lineno >= first_seq_lineno]
    creation_index = 0
    
    for seq_item in sequence:
        # Add any creations that should come before this item
        while (creation_index < len(remaining_creations) and 
               remaining_creations[creation_index].lineno <= seq_item.lineno):
            result.append(remaining_creations[creation_index])
            creation_index += 1
            
        # Add the sequence item
        result.append(seq_item)
    
    # Add any remaining creations
    while creation_index < len(remaining_creations):
        result.append(remaining_creations[creation_index])
        creation_index += 1
        
    return result


def extract_participants_from_sequence(sequence: List[SequenceItem]) -> List[str]:
    """
    Extract unique participants (objects) from a sequence.
    
    Args:
        sequence: List of SequenceItem objects
        
    Returns:
        List of unique participant names in order of first appearance
    """
    participants = []
    seen = set()
    
    # Process object creations first
    for item in sequence:
        if item.is_object_creation and item.target_object:
            if item.target_object not in seen:
                seen.add(item.target_object)
                participants.append(item.target_object)
    
    # Then process method calls
    for item in sequence:
        if not item.is_object_creation:
            # Split the caller to get the object part
            parts = item.caller.split('.')
            obj = parts[0]  # The first part is the object name
            
            if obj not in seen:
                seen.add(obj)
                participants.append(obj)
    
    return participants


def detect_conditional_blocks(sequence: List[SequenceItem]) -> List[SequenceItem]:
    """
    Detect and mark conditional blocks in the sequence.
    
    Groups related conditional items into logical blocks based on their conditionals.
    
    Args:
        sequence: List of SequenceItem objects
        
    Returns:
        Modified list with conditional blocks grouped and marked
    """
    # Copy the sequence to avoid modifying the original
    result = sequence.copy()
    
    # Find conditional items that share the same condition
    i = 0
    while i < len(result):
        if result[i].is_conditional:
            condition = result[i].condition
            block_start = i
            block_end = i
            
            # Find all consecutive items with the same condition
            j = i + 1
            while j < len(result) and result[j].is_conditional and result[j].condition == condition:
                block_end = j
                j += 1
                
            # Mark the first item as block start and last as block end
            if block_end > block_start:
                result[block_start].is_conditional_block_start = True
                result[block_end].is_conditional_block_end = True
                
            # Skip ahead past this block
            i = block_end + 1
        else:
            i += 1
    
    return result


def detect_async_blocks(sequence: List[SequenceItem]) -> List[SequenceItem]:
    """
    Detect and mark asynchronous execution blocks in the sequence.
    
    Groups related async items into logical blocks for parallel execution visualization.
    
    Args:
        sequence: List of SequenceItem objects
        
    Returns:
        Modified list with async blocks grouped and marked
    """
    # Copy the sequence to avoid modifying the original
    result = sequence.copy()
    
    # Find sequences of async operations initiated from the same parent
    i = 0
    while i < len(result):
        if result[i].is_async:
            caller = result[i].caller
            block_start = i
            block_end = i
            
            # Find all consecutive async items with the same caller
            j = i + 1
            while j < len(result) and result[j].is_async and result[j].caller == caller:
                block_end = j
                j += 1
                
            # Mark the first item as block start and last as block end
            if block_end > block_start:
                result[block_start].is_async_block_start = True
                result[block_end].is_async_block_end = True
                
            # Skip ahead past this block
            i = block_end + 1
        else:
            i += 1
    
    return result


def optimize_sequence_for_diagram(sequence: List[SequenceItem]) -> List[SequenceItem]:
    """
    Optimize the sequence for diagram rendering by applying various transformations.
    
    Args:
        sequence: List of SequenceItem objects
        
    Returns:
        Optimized sequence for diagram rendering
    """
    # Apply various sequence optimizations
    sequence = detect_conditional_blocks(sequence)
    sequence = detect_async_blocks(sequence)
    
    # Optimize sequence to collapse sequences of calls from the same object
    # to create more readable diagrams
    
    # Ensure all items have a unique display ID
    for i, item in enumerate(sequence):
        item.display_id = i
    
    return sequence 