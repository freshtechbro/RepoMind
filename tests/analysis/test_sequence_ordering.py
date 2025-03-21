import pytest
from app.analysis.sequence_ordering import order_sequence_from_call_graph, SequenceItem, enhance_sequence_with_object_creations
from app.analysis.call_graph_builder import CallGraphNode


class TestSequenceOrdering:
    """Test cases for the sequence ordering algorithm."""

    def test_simple_sequence_ordering(self):
        """Test ordering a simple sequence from a call graph."""
        # Create a simple call graph
        root = CallGraphNode("Main", "start", [], 1)
        
        call1 = CallGraphNode("Main.start", "process", ["data"], 2)
        call2 = CallGraphNode("Main.start", "finish", [], 5)
        
        nested_call = CallGraphNode("Main.start.process", "validate", [], 3)
        call1.add_child(nested_call)
        
        root.add_child(call1)
        root.add_child(call2)
        
        # Order the sequence
        sequence = order_sequence_from_call_graph([root])
        
        # Check the sequence
        assert len(sequence) == 4
        
        # Check sequence ordering
        assert sequence[0].caller == "Main"
        assert sequence[0].method == "start"
        
        assert sequence[1].caller == "Main.start"
        assert sequence[1].method == "process"
        
        assert sequence[2].caller == "Main.start.process"
        assert sequence[2].method == "validate"
        
        assert sequence[3].caller == "Main.start"
        assert sequence[3].method == "finish"

    def test_sequence_with_multiple_roots(self):
        """Test ordering a sequence with multiple entry points."""
        # Create two independent call graphs
        root1 = CallGraphNode("ClassA", "methodA", [], 1)
        child1 = CallGraphNode("ClassA.methodA", "helper", [], 2)
        root1.add_child(child1)
        
        root2 = CallGraphNode("ClassB", "methodB", [], 5)
        child2 = CallGraphNode("ClassB.methodB", "util", [], 6)
        root2.add_child(child2)
        
        # Order the sequence
        sequence = order_sequence_from_call_graph([root1, root2])
        
        # Check combined sequence
        assert len(sequence) == 4
        
        # First graph's calls should come first (lower line numbers)
        assert sequence[0].caller == "ClassA"
        assert sequence[0].method == "methodA"
        
        assert sequence[1].caller == "ClassA.methodA"
        assert sequence[1].method == "helper"
        
        # Second graph's calls should come after
        assert sequence[2].caller == "ClassB"
        assert sequence[2].method == "methodB"
        
        assert sequence[3].caller == "ClassB.methodB"
        assert sequence[3].method == "util"

    def test_sequence_with_cycles(self):
        """Test ordering a sequence with cyclic calls."""
        # Create a call graph with a cycle
        root = CallGraphNode("Service", "start", [], 1)
        
        call1 = CallGraphNode("Service.start", "process", [], 2)
        root.add_child(call1)
        
        # This call creates a cycle back to process
        cycle_call = CallGraphNode("Service.start.process", "process", [], 3)
        cycle_call.is_cycle_ref = True  # Mark as cycle reference
        call1.add_child(cycle_call)
        
        # Order the sequence
        sequence = order_sequence_from_call_graph([root])
        
        # Should include cycle reference but avoid infinite recursion
        assert len(sequence) == 3
        
        assert sequence[0].caller == "Service"
        assert sequence[0].method == "start"
        
        assert sequence[1].caller == "Service.start"
        assert sequence[1].method == "process"
        
        assert sequence[2].caller == "Service.start.process"
        assert sequence[2].method == "process"
        assert sequence[2].is_cycle_ref

    def test_sequence_with_async_calls(self):
        """Test ordering a sequence with asynchronous calls."""
        # Create a call graph with async calls
        root = CallGraphNode("AsyncService", "start", [], 1)
        
        async_call1 = CallGraphNode("AsyncService.start", "fetchData", [], 2)
        async_call1.is_async = True  # Mark as async
        
        async_call2 = CallGraphNode("AsyncService.start", "processData", [], 3)
        async_call2.is_async = True  # Mark as async
        
        root.add_child(async_call1)
        root.add_child(async_call2)
        
        # Order the sequence
        sequence = order_sequence_from_call_graph([root])
        
        # Check the sequence maintains async flag
        assert len(sequence) == 3
        
        assert sequence[0].caller == "AsyncService"
        assert sequence[0].method == "start"
        
        assert sequence[1].caller == "AsyncService.start"
        assert sequence[1].method == "fetchData"
        assert sequence[1].is_async
        
        assert sequence[2].caller == "AsyncService.start"
        assert sequence[2].method == "processData"
        assert sequence[2].is_async
        
    def test_sequence_with_object_creations(self):
        """Test ordering a sequence with object creation nodes."""
        # Create a call graph with object creation
        creation_node = CallGraphNode("Constructor", "User", ["username"], 1)
        creation_node.is_object_creation = True
        creation_node.target_object = "user"
        
        method_call = CallGraphNode("user", "login", ["password"], 2)
        creation_node.add_child(method_call)
        
        # Order the sequence
        sequence = order_sequence_from_call_graph([creation_node])
        
        # Check the sequence includes object creation
        assert len(sequence) == 2
        
        assert sequence[0].caller == "Constructor"
        assert sequence[0].method == "User"
        assert sequence[0].is_object_creation
        assert sequence[0].target_object == "user"
        
        assert sequence[1].caller == "user"
        assert sequence[1].method == "login"
        
    def test_sequence_with_conditional_blocks(self):
        """Test ordering a sequence with conditional blocks."""
        # Create a call graph with conditional calls
        root = CallGraphNode("Controller", "process", [], 1)
        
        if_call = CallGraphNode("Controller.process", "handleSuccess", [], 2)
        if_call.is_conditional = True
        if_call.condition = "if result.success"
        
        else_call = CallGraphNode("Controller.process", "handleError", [], 3)
        else_call.is_conditional = True
        else_call.condition = "if not result.success"
        
        root.add_child(if_call)
        root.add_child(else_call)
        
        # Order the sequence
        sequence = order_sequence_from_call_graph([root])
        
        # Check the sequence maintains conditional information
        assert len(sequence) == 3
        
        assert sequence[0].caller == "Controller"
        assert sequence[0].method == "process"
        
        assert sequence[1].caller == "Controller.process"
        assert sequence[1].method == "handleSuccess"
        assert sequence[1].is_conditional
        assert sequence[1].condition == "if result.success"
        
        assert sequence[2].caller == "Controller.process"
        assert sequence[2].method == "handleError"
        assert sequence[2].is_conditional
        assert sequence[2].condition == "if not result.success"
        
    def test_complex_sequence_with_object_lifecycle(self):
        """Test ordering a complex sequence with object creations and method calls."""
        # Create user object
        user_creation = CallGraphNode("Constructor", "User", ["name"], 1)
        user_creation.is_object_creation = True
        user_creation.target_object = "user"
        
        # Create service object
        service_creation = CallGraphNode("Constructor", "AuthService", [], 2)
        service_creation.is_object_creation = True
        service_creation.target_object = "authService"
        
        # User calls login
        user_login = CallGraphNode("user", "login", ["password"], 3)
        
        # Login calls auth service
        auth_validate = CallGraphNode("authService", "validate", ["user", "password"], 4)
        user_login.add_child(auth_validate)
        
        # Auth service returns result asynchronously 
        auth_result = CallGraphNode("authService", "returnResult", [], 5)
        auth_result.is_async = True
        auth_validate.add_child(auth_result)
        
        # Connect the graph
        user_creation.add_child(user_login)
        
        # Order the sequence
        sequence = order_sequence_from_call_graph([user_creation, service_creation])
        
        # Check the sequence
        assert len(sequence) == 5
        
        # Check object creations
        assert sequence[0].is_object_creation
        assert sequence[0].target_object == "user"
        
        assert sequence[1].is_object_creation
        assert sequence[1].target_object == "authService"
        
        # Check method calls
        assert sequence[2].caller == "user"
        assert sequence[2].method == "login"
        
        assert sequence[3].caller == "authService"
        assert sequence[3].method == "validate"
        
        assert sequence[4].caller == "authService"
        assert sequence[4].method == "returnResult"
        assert sequence[4].is_async
        
    def test_enhance_sequence_with_object_creations(self):
        """Test enhancing a sequence with object creation information."""
        # Create a basic sequence without explicit object creations
        sequence = [
            SequenceItem("user", "login", ["password"], 1),
            SequenceItem("service", "authenticate", ["user", "password"], 2),
            SequenceItem("user", "accessResource", [], 3)
        ]
        
        # Object creation information
        object_creations = [
            {
                'class': 'User',
                'args': ['name'],
                'target': 'user',
                'lineno': 0  # Before the sequence
            },
            {
                'class': 'AuthService',
                'args': [],
                'target': 'service',
                'lineno': 0  # Before the sequence
            }
        ]
        
        # Enhance the sequence
        enhanced = enhance_sequence_with_object_creations(sequence, object_creations)
        
        # Check the enhanced sequence
        assert len(enhanced) == 5  # Added 2 creation items
        
        # First items should be object creations
        assert enhanced[0].is_object_creation
        assert enhanced[0].target_object == "user"
        assert enhanced[0].method == "User"
        
        assert enhanced[1].is_object_creation
        assert enhanced[1].target_object == "service"
        assert enhanced[1].method == "AuthService"
        
        # Original items should follow, in the same order
        assert enhanced[2].caller == "user"
        assert enhanced[2].method == "login"
        
        assert enhanced[3].caller == "service"
        assert enhanced[3].method == "authenticate"
        
        assert enhanced[4].caller == "user"
        assert enhanced[4].method == "accessResource" 