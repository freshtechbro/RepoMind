"""
Tests for the Python code to sequence diagram integration.
"""
import pytest
from app.diagrams.sequence.analyzer import analyze_python_code, extract_callee_from_method_calls


class TestPythonSequenceAnalyzer:
    """Tests for the Python sequence diagram analyzer."""
    
    def test_extract_callee_from_method_calls(self):
        """Test extraction of callee from method calls."""
        method_calls = [
            {
                "caller": "client",
                "method": "database.query",
                "args": ["SELECT * FROM users"],
                "lineno": 5
            },
            {
                "caller": "app",
                "method": "getData",
                "args": [],
                "lineno": 7
            },
            {
                "caller": "user",
                "method": "validateInput",
                "args": ["input"],
                "lineno": 9
            }
        ]
        
        enhanced_calls = extract_callee_from_method_calls(method_calls)
        
        # Check that callees were properly inferred
        assert enhanced_calls[0]['callee'] == 'Database'
        assert enhanced_calls[0]['method'] == 'query'
        
        assert enhanced_calls[1]['callee'] == 'Data'
        
        assert enhanced_calls[2]['callee'] == 'Validator'
    
    def test_analyze_simple_python_code(self):
        """Test analysis of simple Python code."""
        code = """
        class UserService:
            def authenticate(self, username, password):
                self.db = Database()
                user = self.db.find_user(username)
                if user.validate_password(password):
                    return user
                return None
        
        def main():
            service = UserService()
            user = service.authenticate("alice", "password")
            if user:
                data = user.get_profile()
                print(data)
        """
        
        diagram = analyze_python_code(code)
        
        # Check that the diagram contains the expected elements
        assert "sequenceDiagram" in diagram
        assert "participant UserService" in diagram
        assert "participant Database" in diagram
        assert "main->>UserService: authenticate" in diagram
        assert "UserService->>Database: find_user" in diagram
    
    def test_analyze_code_with_conditional_logic(self):
        """Test analysis of Python code with conditional logic."""
        code = """
        def process_order(order):
            if order.is_valid():
                payment = PaymentProcessor()
                if payment.process(order.amount):
                    OrderService().fulfill(order)
                else:
                    NotificationService().send_failure(order.customer)
            else:
                ValidationService().report_errors(order.errors)
        """
        
        diagram = analyze_python_code(code)
        
        # Check diagram contains correct elements
        assert "process_order->>Order: is_valid" in diagram
        assert "process_order->>PaymentProcessor: process" in diagram
        assert "process_order->>OrderService: fulfill" in diagram
        assert "process_order->>NotificationService: send_failure" in diagram
        assert "process_order->>ValidationService: report_errors" in diagram
        
    def test_analyze_code_with_nested_calls(self):
        """Test analysis of Python code with nested method calls."""
        code = """
        def complex_operation():
            result = database.query().filter(criteria).sort().limit(10)
            return result
        """
        
        diagram = analyze_python_code(code)
        
        # Check diagram contains the method chain
        assert "complex_operation->>Database: query" in diagram
        # The rest might be more complex to verify directly, but the diagram should be generated
        assert "sequenceDiagram" in diagram 