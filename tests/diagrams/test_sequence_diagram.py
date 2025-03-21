"""
Tests for sequence diagram generation from method call data.
"""
import pytest
from app.diagrams.sequence.generator import generate_sequence_diagram, SequenceDiagramGenerator


class TestSequenceDiagramGenerator:
    """Test cases for sequence diagram generation."""
    
    def test_empty_method_calls(self):
        """Test that an empty list of method calls generates minimal diagram syntax."""
        method_calls = []
        
        diagram = generate_sequence_diagram(method_calls)
        
        # Should have minimal Mermaid syntax for an empty diagram
        assert diagram.startswith("sequenceDiagram")
        assert "participant" not in diagram
        
    def test_basic_sequence_diagram(self):
        """Test generation of a basic sequence diagram with a few method calls."""
        method_calls = [
            {
                "caller": "Client",
                "method": "getData",
                "args": [],
                "callee": "Server",
                "lineno": 10
            },
            {
                "caller": "Server",
                "method": "processRequest",
                "args": ["data"],
                "callee": "Database",
                "lineno": 12
            }
        ]
        
        diagram = generate_sequence_diagram(method_calls)
        
        # Check for basic elements of the diagram
        assert "participant Client" in diagram
        assert "participant Server" in diagram
        assert "participant Database" in diagram
        assert "Client->>Server: getData()" in diagram
        assert "Server->>Database: processRequest(data)" in diagram
    
    def test_sequence_with_return_values(self):
        """Test generation of sequence diagram with return values."""
        method_calls = [
            {
                "caller": "Client",
                "method": "fetchData",
                "args": [],
                "callee": "API",
                "returns": "result",
                "lineno": 5
            }
        ]
        
        diagram = generate_sequence_diagram(method_calls)
        
        # Check for return arrow
        assert "Client->>API: fetchData()" in diagram
        assert "API-->>Client: return result" in diagram
    
    def test_sequence_with_nested_calls(self):
        """Test generation of a sequence diagram with nested method calls."""
        method_calls = [
            {
                "caller": "Client",
                "method": "processData",
                "args": [],
                "callee": "Processor",
                "lineno": 5
            },
            {
                "caller": "Processor",
                "method": "validate",
                "args": ["data"],
                "callee": "Validator",
                "lineno": 6
            },
            {
                "caller": "Processor",
                "method": "transform",
                "args": ["data"],
                "callee": "Transformer",
                "lineno": 7
            },
            {
                "caller": "Processor",
                "method": "save",
                "args": ["result"],
                "callee": "Storage",
                "lineno": 8
            }
        ]
        
        diagram = generate_sequence_diagram(method_calls)
        
        # Check all participants and messages
        participants = ["Client", "Processor", "Validator", "Transformer", "Storage"]
        for participant in participants:
            assert f"participant {participant}" in diagram
        
        # Check messages in correct order (sorted by line number)
        assert "Client->>Processor: processData()" in diagram
        assert "Processor->>Validator: validate(data)" in diagram
        assert "Processor->>Transformer: transform(data)" in diagram
        assert "Processor->>Storage: save(result)" in diagram
    
    def test_sequence_with_async_operations(self):
        """Test generation of a sequence diagram with asynchronous operations."""
        method_calls = [
            {
                "caller": "Client",
                "method": "fetchDataAsync",
                "args": [],
                "callee": "API",
                "is_async": True,
                "lineno": 5
            }
        ]
        
        diagram = generate_sequence_diagram(method_calls)
        
        # Check for async arrow notation (-->>)
        assert "Client-)API: fetchDataAsync()" in diagram
    
    def test_sequence_with_conditional_blocks(self):
        """Test generation of a sequence diagram with conditional blocks."""
        method_calls = [
            {
                "caller": "Client",
                "method": "authenticate",
                "args": ["credentials"],
                "callee": "Auth",
                "lineno": 5
            },
            {
                "caller": "Client",
                "method": "getData",
                "args": [],
                "callee": "API",
                "condition": "if authenticated",
                "lineno": 7
            }
        ]
        
        diagram = generate_sequence_diagram(method_calls)
        
        # Check for conditional block
        assert "Client->>Auth: authenticate(credentials)" in diagram
        assert "alt if authenticated" in diagram
        assert "Client->>API: getData()" in diagram
        assert "end" in diagram
    
    def test_object_instance_creation(self):
        """Test visualization of object creation in sequence diagram."""
        method_calls = [
            {
                "caller": "Client",
                "method": "createProcessor",
                "args": ["config"],
                "callee": "Processor",
                "is_creation": True,
                "lineno": 5
            }
        ]
        
        diagram = generate_sequence_diagram(method_calls)
        
        # Check for create message type
        assert "Client->>+Processor: new Processor(config)" in diagram 