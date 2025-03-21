"""
Module for generating sequence diagrams with enhanced asynchronous pattern support.

This module extends the base sequence diagram generator with specialized handling
for asynchronous patterns, including async/await, Promises, callbacks, and threading.
"""

from typing import List, Dict, Any, Optional, Tuple
from app.analysis.sequence_ordering import SequenceItem, extract_participants_from_sequence
from app.analysis.async_pattern_detector import detect_async_patterns
from app.analysis.typescript_async_detector import detect_async_patterns as detect_ts_async_patterns


def generate_async_enhanced_diagram(
    sequence: List[SequenceItem],
    source_code: str,
    language: str = 'python',
    include_returns: bool = True,
    title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a sequence diagram with enhanced asynchronous pattern support.
    
    Args:
        sequence: List of SequenceItem objects representing method calls
        source_code: Source code to analyze for async patterns
        language: Programming language of the source code ('python' or 'typescript')
        include_returns: Whether to add return messages for each call
        title: Optional title for the diagram
        
    Returns:
        Dictionary containing the diagram data structure with async pattern information
    """
    # Extract participants from the sequence
    participants = extract_participants_from_sequence(sequence)
    
    # Detect async patterns in the source code
    async_patterns = []
    if language.lower() == 'python':
        async_patterns = detect_async_patterns(source_code)
    elif language.lower() in ['typescript', 'javascript', 'js', 'ts']:
        async_patterns = detect_ts_async_patterns(source_code)
    
    # Create a lookup table to quickly find async patterns by line number
    async_lookup = {p['lineno']: p for p in async_patterns if 'lineno' in p}
    
    # Process the sequence and enhance with async information
    messages = []
    
    # Process sequence items and track calls currently in progress
    threads = {'main': []}  # Maps thread/task names to lists of active calls
    active_thread = 'main'  # Track the currently active thread
    
    # Enrich sequence items with async pattern information and thread handling
    enriched_sequence = _enrich_sequence_with_async_info(sequence, async_lookup, language)
    
    # Generate message data structures with tracking of parallel execution
    messages, execution_tracks = _generate_messages_with_tracks(
        enriched_sequence,
        participants,
        include_returns
    )
    
    # Create diagram data structure
    diagram_data = {
        "participants": participants,
        "messages": messages,
        "execution_tracks": execution_tracks
    }
    
    # Add title if provided
    if title:
        diagram_data["title"] = title
        
    return diagram_data


def _enrich_sequence_with_async_info(
    sequence: List[SequenceItem],
    async_lookup: Dict[int, Dict[str, Any]],
    language: str
) -> List[Dict[str, Any]]:
    """
    Enrich sequence items with asynchronous pattern information.
    
    Args:
        sequence: List of SequenceItem objects
        async_lookup: Dictionary mapping line numbers to async pattern information
        language: Programming language of the source code
        
    Returns:
        List of enriched sequence items
    """
    enriched_items = []
    
    for item in sequence:
        enriched_item = item.__dict__.copy()  # Convert SequenceItem to dict
        
        # Check if this line has an async pattern
        if item.lineno in async_lookup:
            pattern = async_lookup[item.lineno]
            
            # Enrich the item based on the type of async pattern
            pattern_type = pattern.get('type', '')
            
            # Handle async/await patterns
            if 'async_function' in pattern_type or 'async_method' in pattern_type:
                enriched_item['execution_context'] = 'async'
                enriched_item['is_async'] = True
            
            # Handle promise-based patterns
            elif 'promise' in pattern_type:
                enriched_item['execution_context'] = 'promise'
                enriched_item['is_async'] = True
                
                if pattern_type == 'promise_then':
                    enriched_item['callback_type'] = 'then'
                elif pattern_type == 'promise_catch':
                    enriched_item['callback_type'] = 'catch'
            
            # Handle threading/task-based patterns
            elif pattern_type == 'threading' or pattern_type == 'create_task':
                enriched_item['execution_context'] = 'parallel'
                enriched_item['is_async'] = True
                enriched_item['thread_name'] = pattern.get('target', 'thread')
                
            # Handle await expressions
            elif pattern_type == 'await_expression':
                enriched_item['is_awaited'] = True
                enriched_item['suspend_point'] = True
            
            # Handle callback patterns
            elif pattern_type == 'callback_pattern':
                enriched_item['execution_context'] = 'callback'
                enriched_item['is_async'] = True
        
        enriched_items.append(enriched_item)
    
    return enriched_items


def _generate_messages_with_tracks(
    enriched_sequence: List[Dict[str, Any]],
    participants: List[str],
    include_returns: bool
) -> Tuple[List[Dict[str, Any]], Dict[str, List[int]]]:
    """
    Generate message data structures with tracking of parallel execution tracks.
    
    Args:
        enriched_sequence: List of enriched sequence items
        participants: List of participant names
        include_returns: Whether to add return messages
        
    Returns:
        Tuple of (messages, execution_tracks) where execution_tracks is a mapping
        of track names to lists of message indices that belong to each track
    """
    messages = []
    execution_tracks = {'main': []}
    current_track = 'main'
    track_stack = ['main']
    
    for idx, item in enumerate(enriched_sequence):
        # Determine the from and to objects
        from_obj = _extract_caller_object(item['caller'])
        
        # For the 'to' object, check if method call is to another object
        caller_parts = item['caller'].split('.')
        if len(caller_parts) > 1 and caller_parts[0] in participants:
            to_obj = caller_parts[0]
        else:
            # Default to self-call
            to_obj = from_obj
        
        # Create message data
        message = {
            "from": from_obj,
            "to": to_obj,
            "method": item['method'],
            "args": item.get('args', []),
            "lineno": item['lineno'],
            "depth": item['depth'],
            "track": current_track
        }
        
        # Add flags for special message types
        if item.get('is_async', False):
            message["is_async"] = True
            
            # Handle track changes for async execution
            if item.get('execution_context') == 'parallel':
                # Create a new track for parallel execution
                new_track = item.get('thread_name', f"thread_{len(execution_tracks)}")
                execution_tracks[new_track] = []
                track_stack.append(new_track)
                message["creates_track"] = new_track
                
            elif item.get('execution_context') == 'async':
                # Create a new track for async execution
                new_track = f"async_{len(execution_tracks)}"
                execution_tracks[new_track] = []
                track_stack.append(new_track)
                message["creates_track"] = new_track
                
            elif item.get('execution_context') == 'promise':
                # Create a new track for promise-based execution
                new_track = f"promise_{len(execution_tracks)}"
                execution_tracks[new_track] = []
                track_stack.append(new_track)
                message["creates_track"] = new_track
                
            elif item.get('execution_context') == 'callback':
                # Create a new track for callback execution
                new_track = f"callback_{len(execution_tracks)}"
                execution_tracks[new_track] = []
                track_stack.append(new_track)
                message["creates_track"] = new_track
        
        if item.get('is_conditional', False):
            message["is_conditional"] = True
            message["condition"] = item.get('condition', '')
            
        if item.get('is_cycle_ref', False):
            message["is_cycle_ref"] = True
            
        if item.get('is_awaited', False):
            message["is_awaited"] = True
            
        if item.get('suspend_point', False):
            message["suspend_point"] = True
            
            # Pop the track if this is a suspend point
            if len(track_stack) > 1:
                track_stack.pop()
                current_track = track_stack[-1]
                message["returns_to_track"] = current_track
        
        messages.append(message)
        execution_tracks[current_track].append(len(messages) - 1)
        
        # Switch to new track if created
        if "creates_track" in message:
            current_track = message["creates_track"]
    
    # Add return messages if requested
    if include_returns:
        return_messages = _generate_async_return_messages(messages, execution_tracks)
        
        # Add return messages to the message list and track
        for msg in return_messages:
            messages.append(msg)
            track = msg.get("track", "main")
            if track in execution_tracks:
                execution_tracks[track].append(len(messages) - 1)
    
    return messages, execution_tracks


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


def _generate_async_return_messages(
    messages: List[Dict[str, Any]],
    execution_tracks: Dict[str, List[int]]
) -> List[Dict[str, Any]]:
    """
    Generate return messages for each call with proper async handling.
    
    Args:
        messages: List of message data structures
        execution_tracks: Mapping of track names to message indices
        
    Returns:
        List of return message data structures
    """
    return_messages = []
    
    for i, msg in enumerate(messages):
        # Skip creating return messages for messages that already have suspend points
        if msg.get("suspend_point", False):
            continue
            
        # Create return message
        return_msg = {
            "from": msg["to"],
            "to": msg["from"],
            "method": f"return from {msg['method']}",
            "is_return": True,
            "lineno": msg["lineno"],
            "track": msg["track"]
        }
        
        # Preserve flags from original message
        if "is_async" in msg:
            return_msg["is_async"] = msg["is_async"]
            
        if "is_conditional" in msg:
            return_msg["is_conditional"] = msg["is_conditional"]
            return_msg["condition"] = msg.get("condition", "")
            
        if "creates_track" in msg:
            return_msg["returns_to_track"] = track_stack[0] if track_stack else "main"
            
        return_messages.append(return_msg)
    
    return return_messages 