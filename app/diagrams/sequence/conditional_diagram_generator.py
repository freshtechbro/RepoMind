"""
Module for generating sequence diagrams with enhanced conditional flow visualization.

This module extends the base sequence diagram generator with specialized handling
for conditional logic patterns, including if statements, loops, ternary operators,
and try-except blocks.
"""

from typing import List, Dict, Any, Optional, Tuple, Set
from app.analysis.sequence_ordering import SequenceItem, extract_participants_from_sequence
from app.analysis.conditional_pattern_detector import detect_conditional_patterns
from app.analysis.typescript_conditional_detector import detect_conditional_patterns as detect_ts_conditional_patterns


def generate_conditional_enhanced_diagram(
    sequence: List[SequenceItem],
    source_code: str,
    language: str = 'python',
    include_returns: bool = True,
    title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a sequence diagram with enhanced conditional flow visualization.
    
    Args:
        sequence: List of SequenceItem objects representing method calls
        source_code: Source code to analyze for conditional patterns
        language: Programming language of the source code ('python' or 'typescript')
        include_returns: Whether to add return messages for each call
        title: Optional title for the diagram
        
    Returns:
        Dictionary containing the diagram data structure with conditional flow information
    """
    # Extract participants from the sequence
    participants = extract_participants_from_sequence(sequence)
    
    # Detect conditional patterns in the source code
    conditional_patterns = []
    if language.lower() == 'python':
        conditional_patterns = detect_conditional_patterns(source_code)
    elif language.lower() in ['typescript', 'javascript', 'js', 'ts']:
        conditional_patterns = detect_ts_conditional_patterns(source_code)
    
    # Create a lookup table to quickly find conditional patterns by line number
    conditional_lookup = {p['lineno']: p for p in conditional_patterns if 'lineno' in p}
    
    # Enrich sequence items with conditional pattern information
    enriched_sequence = _enrich_sequence_with_conditional_info(sequence, conditional_lookup, language)
    
    # Generate message data structures with conditional blocks
    messages, conditional_blocks = _generate_messages_with_conditional_blocks(
        enriched_sequence,
        participants,
        include_returns
    )
    
    # Create diagram data structure
    diagram_data = {
        "participants": participants,
        "messages": messages,
        "conditional_blocks": conditional_blocks
    }
    
    # Add title if provided
    if title:
        diagram_data["title"] = title
        
    return diagram_data


def _enrich_sequence_with_conditional_info(
    sequence: List[SequenceItem],
    conditional_lookup: Dict[int, Dict[str, Any]],
    language: str
) -> List[Dict[str, Any]]:
    """
    Enrich sequence items with conditional pattern information.
    
    Args:
        sequence: List of SequenceItem objects
        conditional_lookup: Dictionary mapping line numbers to conditional pattern information
        language: Programming language of the source code
        
    Returns:
        List of enriched sequence items
    """
    enriched_items = []
    
    # Track if statements that span multiple sequence items
    current_if_statement = None
    current_nesting_level = 0
    
    for idx, item in enumerate(sequence):
        enriched_item = item.__dict__.copy()  # Convert SequenceItem to dict
        
        # Check if this line has a conditional pattern
        if item.lineno in conditional_lookup:
            pattern = conditional_lookup[item.lineno]
            
            # Enrich the item based on the type of conditional pattern
            pattern_type = pattern.get('type', '')
            
            # Handle if statements
            if 'if_statement' in pattern_type or 'if_elif_chain' in pattern_type:
                enriched_item['is_conditional'] = True
                enriched_item['condition'] = pattern.get('condition', '')
                enriched_item['condition_type'] = pattern_type
                enriched_item['has_else'] = pattern.get('has_else', False)
                enriched_item['branches'] = pattern.get('branches', 1)
                enriched_item['nesting_level'] = pattern.get('nesting_level', 0)
                
                # Start tracking a new if statement
                current_if_statement = {
                    'start_idx': idx,
                    'condition': pattern.get('condition', ''),
                    'has_else': pattern.get('has_else', False),
                    'nesting_level': pattern.get('nesting_level', 0)
                }
                current_nesting_level = pattern.get('nesting_level', 0)
            
            # Handle ternary operators
            elif pattern_type == 'ternary':
                enriched_item['is_conditional'] = True
                enriched_item['condition'] = pattern.get('condition', '')
                enriched_item['condition_type'] = 'ternary'
                enriched_item['has_else'] = True  # Ternary always has an else part
                enriched_item['is_inline'] = True  # Ternary is an inline condition
            
            # Handle switch-case
            elif pattern_type == 'switch_case':
                enriched_item['is_conditional'] = True
                enriched_item['condition'] = f"switch({pattern.get('switch_expression', '')})"
                enriched_item['condition_type'] = 'switch_case'
                enriched_item['has_else'] = pattern.get('has_default', False)
                enriched_item['branches'] = pattern.get('cases', 1)
            
            # Handle try-except/try-catch
            elif pattern_type in ['try_except', 'try_catch']:
                enriched_item['is_conditional'] = True
                enriched_item['condition'] = 'try'
                enriched_item['condition_type'] = pattern_type
                enriched_item['has_handlers'] = pattern.get('has_handlers', False) or pattern.get('error_variable', '') != ''
                enriched_item['has_finally'] = pattern.get('has_finally', False)
            
            # Handle loops
            elif 'loop' in pattern_type:
                enriched_item['is_conditional'] = True
                enriched_item['condition'] = pattern.get('condition', '')
                enriched_item['condition_type'] = pattern_type
                enriched_item['is_loop'] = True
            
            # Handle break/continue
            elif pattern_type in ['if_break', 'if_continue']:
                enriched_item['is_conditional'] = True
                enriched_item['condition'] = pattern.get('condition', '')
                enriched_item['condition_type'] = pattern_type
                enriched_item['loop_control'] = pattern_type.split('_')[1]  # 'break' or 'continue'
        
        # Check if this item is part of an ongoing if statement based on nesting level
        elif current_if_statement is not None:
            # If the nesting level is the same or higher, it's likely part of the same conditional block
            if item.depth >= current_nesting_level:
                enriched_item['in_conditional_block'] = True
                enriched_item['parent_condition'] = current_if_statement['condition']
                enriched_item['parent_nesting_level'] = current_nesting_level
            else:
                # We've exited the conditional block
                current_if_statement = None
                current_nesting_level = 0
        
        enriched_items.append(enriched_item)
    
    return enriched_items


def _generate_messages_with_conditional_blocks(
    enriched_sequence: List[Dict[str, Any]],
    participants: List[str],
    include_returns: bool
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Generate message data structures with conditional blocks.
    
    Args:
        enriched_sequence: List of enriched sequence items
        participants: List of participant names
        include_returns: Whether to add return messages
        
    Returns:
        Tuple of (messages, conditional_blocks) where conditional_blocks describes
        the conditional regions in the diagram
    """
    messages = []
    conditional_blocks = []
    
    # Detect conditional blocks (sequences of messages under the same condition)
    # For each message that starts a condition, calculate end indices
    condition_stack = []
    conditional_regions = []
    
    # First pass: Create basic messages and identify the start and scope of conditional blocks
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
            "id": f"message_{idx}"  # Unique ID for referencing
        }
        
        # Add flags for special message types
        if item.get('is_conditional', False):
            message["is_conditional"] = True
            message["condition"] = item.get('condition', '')
            message["condition_type"] = item.get('condition_type', 'if')
            
            # Identify the start of a new conditional block
            condition_region = {
                'start_idx': idx,
                'condition': item.get('condition', ''),
                'type': item.get('condition_type', 'if'),
                'has_else': item.get('has_else', False),
                'nesting_level': item.get('nesting_level', 0),
                'is_loop': item.get('is_loop', False)
            }
            
            condition_stack.append(condition_region)
            conditional_regions.append(condition_region)
        
        # Check if we've exited a conditional block
        while condition_stack and idx > 0:
            # If the current message is at a lower nesting level, we've exited the block
            current_nesting = item.get('parent_nesting_level', 0)
            top_condition = condition_stack[-1]
            
            if not item.get('in_conditional_block', False) or current_nesting < top_condition['nesting_level']:
                # This message is outside the conditional block
                top_condition['end_idx'] = idx - 1
                condition_stack.pop()
            else:
                # Still in the same conditional block
                break
        
        # If it's an item within a conditional block, tag it
        if item.get('in_conditional_block', False):
            message["in_conditional_block"] = True
            message["parent_condition"] = item.get('parent_condition', '')
        
        # Handle loop control (break/continue)
        if item.get('loop_control'):
            message["loop_control"] = item.get('loop_control')
        
        if item.get('is_cycle_ref', False):
            message["is_cycle_ref"] = True
            
        messages.append(message)
    
    # Close any still-open conditional blocks
    for condition in condition_stack:
        condition['end_idx'] = len(messages) - 1
    
    # Format conditional blocks for visualization
    formatted_blocks = []
    for region in conditional_regions:
        # Only include complete regions
        if 'end_idx' not in region:
            region['end_idx'] = len(messages) - 1
        
        formatted_blocks.append({
            'start_message_id': messages[region['start_idx']]['id'],
            'end_message_id': messages[region['end_idx']]['id'],
            'condition': region['condition'],
            'type': region['type'],
            'has_else': region['has_else'],
            'nesting_level': region['nesting_level'],
            'is_loop': region['is_loop']
        })
    
    # Add return messages if requested
    if include_returns:
        return_messages = _generate_conditional_return_messages(messages, formatted_blocks)
        
        # Add return messages to the message list
        messages.extend(return_messages)
    
    return messages, formatted_blocks


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


def _generate_conditional_return_messages(
    messages: List[Dict[str, Any]],
    conditional_blocks: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Generate return messages for each call with conditional information preserved.
    
    Args:
        messages: List of message data structures
        conditional_blocks: List of conditional block definitions
        
    Returns:
        List of return message data structures
    """
    return_messages = []
    
    # Build a lookup of message IDs to blocks they belong to
    message_to_block = {}
    for block in conditional_blocks:
        # Find all message IDs between start and end message
        start_id = block['start_message_id']
        end_id = block['end_message_id']
        
        start_idx = next(i for i, m in enumerate(messages) if m['id'] == start_id)
        end_idx = next(i for i, m in enumerate(messages) if m['id'] == end_id)
        
        for i in range(start_idx, end_idx + 1):
            message_id = messages[i]['id']
            if message_id not in message_to_block:
                message_to_block[message_id] = []
            message_to_block[message_id].append(block)
    
    for i, msg in enumerate(messages):
        # Create return message
        return_msg = {
            "from": msg["to"],
            "to": msg["from"],
            "method": f"return from {msg['method']}",
            "is_return": True,
            "lineno": msg["lineno"],
            "id": f"return_{msg['id']}"
        }
        
        # Preserve conditional information
        if msg.get("is_conditional") == True:
            return_msg["is_conditional"] = True
            return_msg["condition"] = msg["condition"]
            return_msg["condition_type"] = msg["condition_type"]
        
        if msg.get("in_conditional_block") == True:
            return_msg["in_conditional_block"] = True
            return_msg["parent_condition"] = msg["parent_condition"]
        
        # Check if this message is part of any conditional blocks
        if msg["id"] in message_to_block:
            blocks = message_to_block[msg["id"]]
            # We're only interested in the innermost block
            innermost_block = max(blocks, key=lambda b: b['nesting_level'])
            
            if not msg.get("in_conditional_block"):
                return_msg["in_conditional_block"] = True
                return_msg["parent_condition"] = innermost_block["condition"]
        
        return_messages.append(return_msg)
    
    return return_messages 