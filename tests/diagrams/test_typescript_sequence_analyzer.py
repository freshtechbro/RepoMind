"""
Tests for the TypeScript/JavaScript code to sequence diagram integration.
"""
import pytest
from app.diagrams.sequence.typescript_analyzer import analyze_typescript_code, extract_callee_from_ts_method_calls


class TestTypeScriptSequenceAnalyzer:
    """Tests for the TypeScript sequence diagram analyzer."""
    
    def test_extract_callee_from_ts_method_calls(self):
        """Test extraction of callee from TypeScript method calls."""
        method_calls = [
            {
                "caller": "service",
                "method": "fetchData",
                "args": [],
                "lineno": 5
            },
            {
                "caller": "this.httpClient",
                "method": "get",
                "args": ["/api/users"],
                "lineno": 7
            },
            {
                "is_constructor": True,
                "class": "UserService",
                "args": ["config"],
                "lineno": 9
            }
        ]
        
        enhanced_calls = extract_callee_from_ts_method_calls(method_calls)
        
        # Check that callees were properly inferred
        assert enhanced_calls[0]['callee'] == 'Service'
        assert enhanced_calls[1]['callee'] == 'Httpclient'
        
        # Check constructor transformation
        assert enhanced_calls[2]['callee'] == 'UserService'
        assert enhanced_calls[2]['method'] == 'constructor'
    
    def test_analyze_simple_typescript_code(self):
        """Test analysis of simple TypeScript code."""
        code = """
        class UserService {
            constructor(private httpClient: HttpClient) {}
            
            async getUsers() {
                const response = await this.httpClient.get('/users');
                return response.data;
            }
        }
        
        function main() {
            const service = new UserService(httpClient);
            const users = service.getUsers();
            console.log(users);
        }
        """
        
        diagram = analyze_typescript_code(code)
        
        # Check that the diagram contains the expected elements
        assert "sequenceDiagram" in diagram
        assert "participant UserService" in diagram
        assert "participant Httpclient" in diagram
        assert "main->>UserService: constructor" in diagram
    
    def test_analyze_typescript_with_chained_calls(self):
        """Test analysis of TypeScript code with chained method calls."""
        code = """
        function processData(data) {
            return data
                .filter(item => item.active)
                .map(item => transformItem(item))
                .reduce((acc, item) => {
                    return acc + item.value;
                }, 0);
        }
        
        function transformItem(item) {
            return apiClient.fetchDetails(item.id);
        }
        """
        
        diagram = analyze_typescript_code(code)
        
        # Check diagram contains expected elements
        assert "sequenceDiagram" in diagram
        assert "processData->>Data: filter" in diagram or "processData->>Array: filter" in diagram
        assert "transformItem->>ApiClient: fetchDetails" in diagram
        
    def test_analyze_typescript_with_async_patterns(self):
        """Test analysis of TypeScript code with async/await patterns."""
        code = """
        async function loadUserData(userId) {
            try {
                const user = await userService.findById(userId);
                const permissions = await permissionService.getForUser(user.id);
                
                return {
                    user,
                    permissions
                };
            } catch (error) {
                errorService.log(error);
                return null;
            }
        }
        """
        
        diagram = analyze_typescript_code(code)
        
        # Check diagram contains async operations
        assert "sequenceDiagram" in diagram
        assert "loadUserData-)UserService: findById" in diagram  # Note the async arrow notation
        assert "loadUserData-)PermissionService: getForUser" in diagram
        assert "loadUserData->>ErrorService: log" in diagram 