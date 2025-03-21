"""
Module for generating sequence diagram data structures.

This module transforms sequence data into diagram data structures
suitable for visualization with JointJS or other rendering libraries.
"""

from typing import List, Dict, Any, Optional
from app.analysis.sequence_ordering import SequenceItem, extract_participants_from_sequence


def generate_sequence_diagram_data(
    sequence: List[SequenceItem], 
    include_returns: bool = False,
    title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a sequence diagram data structure from a sequence of method calls.
    
    Args:
        sequence: List of SequenceItem objects representing method calls
        include_returns: Whether to add return messages for each call
        title: Optional title for the diagram
        
    Returns:
        Dictionary containing the diagram data structure with participants and messages
    """
    # Extract participants from the sequence
    participants = extract_participants_from_sequence(sequence)
    
    # Generate message data structures
    messages = []
    
    for item in sequence:
        # Determine the from and to objects
        from_obj = _extract_caller_object(item.caller)
        
        # For the 'to' object, we need to check the method signature
        # In simple cases, method calls on the same object use the same object as from/to
        to_obj = from_obj
        
        # For cross-object calls, the 'to' would be the first part of the method name
        # This is a simplified approach; in practice would need more complex logic
        caller_parts = item.caller.split('.')
        if len(caller_parts) > 1 and caller_parts[1] in participants:
            to_obj = caller_parts[1]
        
        # Create message data
        message = {
            "from": from_obj,
            "to": to_obj,
            "method": item.method,
            "args": item.args,
            "lineno": item.lineno,
            "depth": item.depth
        }
        
        # Add flags for special message types
        if item.is_async:
            message["is_async"] = True
        if item.is_conditional:
            message["is_conditional"] = True
            message["condition"] = item.condition
        if item.is_cycle_ref:
            message["is_cycle_ref"] = True
            
        messages.append(message)
    
    # Add return messages if requested
    if include_returns:
        return_messages = _generate_return_messages(messages)
        messages.extend(return_messages)
    
    # Create diagram data structure
    diagram_data = {
        "participants": participants,
        "messages": messages
    }
    
    # Add title if provided
    if title:
        diagram_data["title"] = title
        
    return diagram_data


def _extract_caller_object(caller: str) -> str:
    """
    Extract the base object name from a caller string.
    
    Args:
        caller: Caller string in the format "Object.method1.method2..."
        
    Returns:
        The base object name
    """
    # The base object is the first part of the caller string
    return caller.split('.')[0]


def _generate_return_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate return messages for each call.
    
    For each message in the input list, creates a corresponding return message
    going in the opposite direction.
    
    Args:
        messages: List of message data structures
        
    Returns:
        List of return message data structures
    """
    return_messages = []
    
    for i, msg in enumerate(messages):
        return_msg = {
            "from": msg["to"],
            "to": msg["from"],
            "method": f"return from {msg['method']}",
            "is_return": True,
            "lineno": msg["lineno"],
            "depth": msg["depth"]
        }
        
        # Preserve flags from original message
        if "is_async" in msg:
            return_msg["is_async"] = msg["is_async"]
        if "is_conditional" in msg:
            return_msg["is_conditional"] = msg["is_conditional"]
            return_msg["condition"] = msg["condition"]
            
        return_messages.append(return_msg)
    
    return return_messages


def enrich_diagram_with_code_snippets(
    diagram_data: Dict[str, Any], 
    code_snippets: Dict[int, str]
) -> Dict[str, Any]:
    """
    Enrich diagram data with code snippets for each message.
    
    Args:
        diagram_data: Sequence diagram data structure
        code_snippets: Dictionary mapping line numbers to code snippets
        
    Returns:
        Enriched diagram data with code snippets
    """
    enriched_data = diagram_data.copy()
    
    # Add code snippets to messages
    for msg in enriched_data["messages"]:
        lineno = msg.get("lineno")
        if lineno in code_snippets:
            msg["code_snippet"] = code_snippets[lineno]
    
    return enriched_data


def get_lifeline_activations(diagram_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Compute activation regions for each participant's lifeline.
    
    This determines when each participant is "active" based on method calls,
    for rendering activation boxes in the sequence diagram.
    
    Args:
        diagram_data: Sequence diagram data structure
        
    Returns:
        Dictionary mapping participant names to lists of activation periods
    """
    activations = {participant: [] for participant in diagram_data["participants"]}
    
    # Stack to track nested calls for each participant
    call_stack = {participant: [] for participant in diagram_data["participants"]}
    
    for i, msg in enumerate(diagram_data["messages"]):
        # Skip return messages (they don't create new activations)
        if msg.get("is_return", False):
            continue
            
        # Get sender and receiver
        from_obj = msg["from"]
        to_obj = msg["to"]
        
        # Record activation for the receiver
        activation = {
            "start_index": i,
            "end_index": None,  # Will be filled later
            "depth": len(call_stack[to_obj])  # Nesting level
        }
        
        call_stack[to_obj].append(activation)
        
        # If there's a return message, find it and close the activation
        # This is a simplified approach; in reality would need to match return messages
        # Return messages are typically right after the call or after all nested calls
        if i < len(diagram_data["messages"]) - 1:
            # Look for a return message from to_obj back to from_obj
            for j in range(i + 1, len(diagram_data["messages"])):
                next_msg = diagram_data["messages"][j]
                if (next_msg.get("is_return", False) and 
                    next_msg["from"] == to_obj and 
                    next_msg["to"] == from_obj):
                    # Found matching return message
                    activation["end_index"] = j
                    break
    
    # Handle any unclosed activations (e.g., if no return messages)
    for participant, stack in call_stack.items():
        for activation in stack:
            if activation["end_index"] is None:
                # If no explicit end, assume it ends at the last message
                activation["end_index"] = len(diagram_data["messages"]) - 1
                
        # Add activations to the result
        activations[participant].extend(stack)
    
    return activations 