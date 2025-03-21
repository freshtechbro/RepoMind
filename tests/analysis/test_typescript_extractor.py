"""
Tests for extracting method calls from TypeScript/JavaScript code.
"""
import pytest
from app.analysis.typescript_extractor import extract_method_calls


class TestTypeScriptExtractor:
    """Test cases for TypeScript/JavaScript method call extraction."""

    def test_simple_method_call_extraction(self):
        """Test extraction of simple method calls from TypeScript code."""
        code = """
        const obj = new MyClass();
        obj.method1();
        obj.method2(param1, param2);
        """
        
        method_calls = extract_method_calls(code)
        
        # Should extract two method calls and one constructor
        assert len(method_calls) == 3
        
        # Check constructor
        constructor_call = next(call for call in method_calls if call['is_constructor'])
        assert constructor_call['class'] == 'MyClass'
        
        # Find method calls
        method1_call = next(call for call in method_calls if call['method'] == 'method1')
        method2_call = next(call for call in method_calls if call['method'] == 'method2')
        
        # Check first method call
        assert method1_call['caller'] == 'obj'
        assert len(method1_call['args']) == 0
        
        # Check second method call
        assert method2_call['caller'] == 'obj'
        assert len(method2_call['args']) == 2

    def test_nested_method_call_extraction(self):
        """Test extraction of nested method calls in TypeScript."""
        code = """
        const result = obj1.method1().method2();
        """
        
        method_calls = extract_method_calls(code)
        
        # Should extract two method calls
        assert len(method_calls) == 2
        
        # Check method calls exist (order depends on implementation)
        methods = {call['method'] for call in method_calls}
        assert 'method1' in methods
        assert 'method2' in methods

    def test_arrow_function_method_calls(self):
        """Test extraction of method calls within arrow functions."""
        code = """
        const handler = () => {
            service.fetchData();
            return data.process();
        };
        """
        
        method_calls = extract_method_calls(code)
        
        # Should extract two method calls
        assert len(method_calls) == 2
        
        # Check method calls
        callers = {call['caller'] for call in method_calls}
        methods = {call['method'] for call in method_calls}
        
        assert 'service' in callers
        assert 'data' in callers
        assert 'fetchData' in methods
        assert 'process' in methods

    def test_class_method_calls(self):
        """Test extraction of method calls within class methods."""
        code = """
        class UserService {
            constructor(private httpClient: HttpClient) {}
            
            async getUsers() {
                const response = await this.httpClient.get('/users');
                return response.data.map(user => this.transformUser(user));
            }
            
            private transformUser(userData: any) {
                return new User(userData);
            }
        }
        """
        
        method_calls = extract_method_calls(code)
        
        # Check method calls within class methods
        http_get_call = next((call for call in method_calls if call['method'] == 'get'), None)
        assert http_get_call is not None
        assert http_get_call['caller'] == 'this.httpClient'
        
        # Check for map and transformUser calls
        transform_call = next((call for call in method_calls if call['method'] == 'transformUser'), None)
        assert transform_call is not None
        assert transform_call['caller'] == 'this'
        
        # Check for constructor
        user_constructor = next((call for call in method_calls if call['is_constructor'] and call['class'] == 'User'), None)
        assert user_constructor is not None

    def test_async_await_pattern(self):
        """Test extraction of async/await method calls."""
        code = """
        async function fetchData() {
            const result = await api.getData();
            return result.process();
        }
        """
        
        method_calls = extract_method_calls(code)
        
        # Should find getData and process calls
        assert len(method_calls) >= 2
        
        # Check for async calls
        get_data_call = next((call for call in method_calls if call['method'] == 'getData'), None)
        assert get_data_call is not None
        assert get_data_call['caller'] == 'api'
        assert get_data_call.get('is_async', False) is True
        
        process_call = next((call for call in method_calls if call['method'] == 'process'), None)
        assert process_call is not None
        assert process_call['caller'] == 'result' 