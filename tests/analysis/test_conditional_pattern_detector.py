import pytest
import ast
from app.analysis.conditional_pattern_detector import detect_conditional_patterns, ConditionalPatternDetector

def test_detect_if_statement():
    """Test detection of simple if statements."""
    code = """
    def process_data(data):
        if data.is_valid:
            result = data.process()
            return result
        else:
            return None
    """
    
    patterns = detect_conditional_patterns(code)
    
    assert len(patterns) == 1
    assert patterns[0]['type'] == 'if_statement'
    assert 'data.is_valid' in patterns[0]['condition']
    assert patterns[0]['has_else'] == True

def test_detect_if_elif_else():
    """Test detection of if-elif-else chains."""
    code = """
    def check_status(status_code):
        if status_code >= 200 and status_code < 300:
            return "Success"
        elif status_code >= 400 and status_code < 500:
            return "Client Error"
        elif status_code >= 500:
            return "Server Error"
        else:
            return "Unknown Status"
    """
    
    patterns = detect_conditional_patterns(code)
    
    assert len(patterns) == 1  # One if-elif-else chain
    assert patterns[0]['type'] == 'if_elif_chain'
    assert patterns[0]['branches'] == 3  # if + 2 elif
    assert patterns[0]['has_else'] == True

def test_detect_ternary_operator():
    """Test detection of ternary operators."""
    code = """
    def get_display_name(user):
        return user.name if user.name else "Anonymous"
    """
    
    patterns = detect_conditional_patterns(code)
    
    assert len(patterns) == 1
    assert patterns[0]['type'] == 'ternary'
    assert 'user.name' in patterns[0]['condition']

def test_detect_loop_with_condition():
    """Test detection of loops with conditional breaks or continues."""
    code = """
    def process_items(items):
        results = []
        for item in items:
            if item is None:
                continue
                
            if not item.is_valid:
                break
                
            results.append(process_item(item))
        return results
    """
    
    patterns = detect_conditional_patterns(code)
    
    assert len(patterns) >= 3
    assert any(p['type'] == 'for_loop' for p in patterns)
    assert any(p['type'] == 'if_continue' for p in patterns)
    assert any(p['type'] == 'if_break' for p in patterns)

def test_detect_nested_conditions():
    """Test detection of nested conditional statements."""
    code = """
    def validate_user(user, permissions):
        if user.is_authenticated:
            if user.is_active:
                if 'admin' in permissions:
                    return True
                else:
                    return False
            else:
                return False
        return False
    """
    
    patterns = detect_conditional_patterns(code)
    
    assert len(patterns) >= 3  # At least 3 if statements
    
    # Find the outer if statement
    outer_if = next((p for p in patterns if p['type'] == 'if_statement' 
                     and 'user.is_authenticated' in p['condition']), None)
    assert outer_if is not None
    
    # Check nesting level
    assert any(p['nesting_level'] > 0 for p in patterns)

def test_detect_try_except():
    """Test detection of try-except blocks as conditional flows."""
    code = """
    def fetch_data(url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching data: {e}")
            return None
    """
    
    patterns = detect_conditional_patterns(code)
    
    assert len(patterns) == 1
    assert patterns[0]['type'] == 'try_except'
    assert patterns[0]['has_handlers'] == True 