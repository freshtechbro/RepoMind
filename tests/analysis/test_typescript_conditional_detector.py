import pytest
from app.analysis.typescript_conditional_detector import detect_conditional_patterns

def test_detect_if_statement():
    """Test detection of if statements in TypeScript."""
    code = """
    function processData(data) {
        if (data.isValid) {
            const result = data.process();
            return result;
        } else {
            return null;
        }
    }
    """
    
    patterns = detect_conditional_patterns(code)
    
    assert len(patterns) == 1
    assert patterns[0]['type'] == 'if_statement'
    assert 'data.isValid' in patterns[0]['condition']
    assert patterns[0]['has_else'] == True

def test_detect_if_else_if_chain():
    """Test detection of if-else if-else chains in TypeScript."""
    code = """
    function checkStatus(statusCode: number): string {
        if (statusCode >= 200 && statusCode < 300) {
            return "Success";
        } else if (statusCode >= 400 && statusCode < 500) {
            return "Client Error";
        } else if (statusCode >= 500) {
            return "Server Error";
        } else {
            return "Unknown Status";
        }
    }
    """
    
    patterns = detect_conditional_patterns(code)
    
    assert len(patterns) == 1  # One if-else if-else chain
    assert patterns[0]['type'] == 'if_else_if_chain'
    assert patterns[0]['branches'] == 3  # if + 2 else if
    assert patterns[0]['has_else'] == True

def test_detect_ternary_operator():
    """Test detection of ternary operators in TypeScript."""
    code = """
    function getDisplayName(user) {
        return user.name ? user.name : "Anonymous";
    }
    
    const status = isActive ? 'Active' : 'Inactive';
    """
    
    patterns = detect_conditional_patterns(code)
    
    assert len(patterns) == 2  # Two ternary expressions
    assert all(p['type'] == 'ternary' for p in patterns)
    assert any('user.name' in p['condition'] for p in patterns)
    assert any('isActive' in p['condition'] for p in patterns)

def test_detect_switch_case():
    """Test detection of switch-case statements in TypeScript."""
    code = """
    function getStatusMessage(statusCode: number): string {
        switch (statusCode) {
            case 200:
                return "OK";
            case 201:
                return "Created";
            case 404:
                return "Not Found";
            case 500:
                return "Server Error";
            default:
                return "Unknown Status";
        }
    }
    """
    
    patterns = detect_conditional_patterns(code)
    
    assert len(patterns) == 1
    assert patterns[0]['type'] == 'switch_case'
    assert patterns[0]['switch_expression'] == 'statusCode'
    assert patterns[0]['cases'] >= 4  # At least 4 cases
    assert patterns[0]['has_default'] == True

def test_detect_loops_with_conditions():
    """Test detection of loops with conditional breaks or continues in TypeScript."""
    code = """
    function processItems(items) {
        const results = [];
        for (const item of items) {
            if (item === null) {
                continue;
            }
            
            if (!item.isValid) {
                break;
            }
            
            results.push(processItem(item));
        }
        return results;
    }
    """
    
    patterns = detect_conditional_patterns(code)
    
    assert len(patterns) >= 3
    assert any(p['type'] == 'for_of_loop' for p in patterns)
    assert any(p['type'] == 'if_continue' for p in patterns)
    assert any(p['type'] == 'if_break' for p in patterns)

def test_detect_nullish_coalescing():
    """Test detection of nullish coalescing operator in TypeScript."""
    code = """
    function getConfig(config) {
        const timeout = config.timeout ?? 1000;
        const baseUrl = config.baseUrl ?? 'https://api.example.com';
        return { timeout, baseUrl };
    }
    """
    
    patterns = detect_conditional_patterns(code)
    
    assert len(patterns) == 2  # Two nullish coalescing expressions
    assert all(p['type'] == 'nullish_coalescing' for p in patterns)

def test_detect_try_catch():
    """Test detection of try-catch blocks in TypeScript."""
    code = """
    async function fetchData(url: string) {
        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching data:', error);
            return null;
        }
    }
    """
    
    patterns = detect_conditional_patterns(code)
    
    assert len(patterns) >= 2  # try-catch and if statement
    assert any(p['type'] == 'try_catch' for p in patterns)
    assert any(p['type'] == 'if_statement' for p in patterns) 