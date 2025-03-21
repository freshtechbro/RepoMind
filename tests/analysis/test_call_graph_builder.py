import pytest
from app.analysis.call_graph_builder import build_call_graph, CallGraphNode, build_object_lifetime_graph


class TestCallGraphBuilder:
    """Test cases for the call graph builder."""

    def test_simple_call_graph_construction(self):
        """Test building a simple call graph from method calls."""
        method_calls = [
            {
                'caller': 'main',
                'method': 'initialize',
                'args': [],
                'lineno': 1
            },
            {
                'caller': 'main',
                'method': 'process_data',
                'args': ['data'],
                'lineno': 2
            },
            {
                'caller': 'main.process_data',
                'method': 'validate',
                'args': [],
                'lineno': 3
            }
        ]
        
        graph = build_call_graph(method_calls)
        
        # Check root nodes (direct calls from main)
        assert len(graph) == 2
        
        # Find the nodes for initialize and process_data
        initialize_node = next(node for node in graph if node.method == 'initialize')
        process_node = next(node for node in graph if node.method == 'process_data')
        
        # Check properties
        assert initialize_node.caller == 'main'
        assert process_node.caller == 'main'
        
        # Check children
        assert len(initialize_node.children) == 0
        assert len(process_node.children) == 1
        assert process_node.children[0].method == 'validate'

    def test_call_graph_with_cycles(self):
        """Test building a call graph that contains cycles."""
        method_calls = [
            {
                'caller': 'ClassA',
                'method': 'methodA',
                'args': [],
                'lineno': 1
            },
            {
                'caller': 'ClassA.methodA',
                'method': 'methodB',
                'args': [],
                'lineno': 2
            },
            {
                'caller': 'ClassA.methodB',
                'method': 'methodA',  # Cycle back to methodA
                'args': [],
                'lineno': 3
            }
        ]
        
        graph = build_call_graph(method_calls)
        
        # Should have one root node
        assert len(graph) == 1
        
        # Check the cycle is handled
        root_node = graph[0]
        assert root_node.method == 'methodA'
        assert len(root_node.children) == 1
        
        child_node = root_node.children[0]
        assert child_node.method == 'methodB'
        assert len(child_node.children) == 1
        
        # This should reference back to methodA but not create an infinite loop
        cycle_node = child_node.children[0]
        assert cycle_node.method == 'methodA'
        assert cycle_node.is_cycle_ref  # Should be marked as a cycle reference

    def test_multiple_roots_with_shared_children(self):
        """Test call graph with multiple entry points that call the same method."""
        method_calls = [
            {
                'caller': 'ClassA',
                'method': 'methodA',
                'args': [],
                'lineno': 1
            },
            {
                'caller': 'ClassB',
                'method': 'methodB',
                'args': [],
                'lineno': 2
            },
            {
                'caller': 'ClassA.methodA',
                'method': 'sharedMethod',
                'args': [],
                'lineno': 3
            },
            {
                'caller': 'ClassB.methodB',
                'method': 'sharedMethod',
                'args': [],
                'lineno': 4
            }
        ]
        
        graph = build_call_graph(method_calls)
        
        # Should have two root nodes
        assert len(graph) == 2
        
        # Both should have children that call sharedMethod
        for node in graph:
            assert len(node.children) == 1
            assert node.children[0].method == 'sharedMethod'

    def test_call_graph_with_out_of_order_calls(self):
        """Test building a call graph when calls are not in sequential order."""
        method_calls = [
            {
                'caller': 'nested.method',
                'method': 'deeplyNested',
                'args': [],
                'lineno': 5
            },
            {
                'caller': 'main',
                'method': 'outer',
                'args': [],
                'lineno': 1
            },
            {
                'caller': 'main.outer',
                'method': 'nested',
                'args': [],
                'lineno': 3
            }
        ]
        
        graph = build_call_graph(method_calls)
        
        # Should correctly order despite the calls being out of order
        assert len(graph) == 1
        assert graph[0].method == 'outer'
        assert len(graph[0].children) == 1
        assert graph[0].children[0].method == 'nested'
        assert len(graph[0].children[0].children) == 1
        assert graph[0].children[0].children[0].method == 'deeplyNested'
    
    def test_call_graph_with_object_creation(self):
        """Test building a call graph that includes object creation information."""
        method_calls = [
            {
                'caller': 'main',
                'method': 'initialize',
                'args': [],
                'lineno': 2
            },
            {
                'caller': 'dataProcessor',
                'method': 'process',
                'args': ['data'],
                'lineno': 4
            }
        ]
        
        object_creations = [
            {
                'class': 'DataProcessor',
                'args': [],
                'target': 'dataProcessor',
                'lineno': 3
            }
        ]
        
        graph = build_call_graph(method_calls, object_creations)
        
        # Should have two root nodes: main.initialize and the object creation
        assert len(graph) == 2
        
        # Find the object creation node
        creation_node = next(node for node in graph if node.is_object_creation)
        assert creation_node.method == 'DataProcessor'
        assert creation_node.target_object == 'dataProcessor'
        
        # Check if method call on the object is linked to creation
        assert len(creation_node.children) == 1
        assert creation_node.children[0].method == 'process'
        assert creation_node.children[0].caller == 'dataProcessor'
    
    def test_call_graph_with_multiple_object_creations(self):
        """Test building a call graph with multiple object creations and method calls."""
        method_calls = [
            {
                'caller': 'controller',
                'method': 'start',
                'args': [],
                'lineno': 2
            },
            {
                'caller': 'service',
                'method': 'initialize',
                'args': [],
                'lineno': 4
            },
            {
                'caller': 'controller.start',
                'method': 'setupService',
                'args': [],
                'lineno': 3
            },
            {
                'caller': 'service.initialize',
                'method': 'loadConfig',
                'args': [],
                'lineno': 5
            }
        ]
        
        object_creations = [
            {
                'class': 'Controller',
                'args': [],
                'target': 'controller',
                'lineno': 1
            },
            {
                'class': 'Service',
                'args': ['config'],
                'target': 'service',
                'lineno': 3
            }
        ]
        
        graph = build_call_graph(method_calls, object_creations)
        
        # Should have root nodes for creations and the controller.start call
        controller_creation = next(node for node in graph if node.method == 'Controller')
        assert controller_creation.is_object_creation
        assert controller_creation.target_object == 'controller'
        
        # Controller creation should lead to controller.start
        start_node = controller_creation.children[0]
        assert start_node.method == 'start'
        assert start_node.caller == 'controller'
        
        # controller.start should lead to setupService
        setup_node = start_node.children[0]
        assert setup_node.method == 'setupService'
    
    def test_call_graph_with_async_and_conditional_flags(self):
        """Test building a call graph with async and conditional flags preserved."""
        method_calls = [
            {
                'caller': 'executor',
                'method': 'runTask',
                'args': [],
                'lineno': 1,
                'is_async': True
            },
            {
                'caller': 'validator',
                'method': 'checkInput',
                'args': ['data'],
                'lineno': 2,
                'is_conditional': True,
                'condition': 'if input_valid'
            }
        ]
        
        graph = build_call_graph(method_calls)
        
        # Check that flags are preserved
        async_node = next(node for node in graph if node.caller == 'executor')
        assert async_node.is_async
        
        conditional_node = next(node for node in graph if node.caller == 'validator')
        assert conditional_node.is_conditional
        assert conditional_node.condition == 'if input_valid'


class TestObjectLifetimeGraph:
    """Test cases for the object lifetime graph builder."""
    
    def test_basic_object_lifetime_graph(self):
        """Test building a basic object lifetime graph."""
        method_calls = [
            {
                'caller': 'user',
                'method': 'login',
                'args': ['password'],
                'lineno': 2
            },
            {
                'caller': 'user',
                'method': 'fetchData',
                'args': [],
                'lineno': 3
            }
        ]
        
        object_creations = [
            {
                'class': 'User',
                'args': ['username'],
                'target': 'user',
                'lineno': 1
            }
        ]
        
        lifetime_graph = build_object_lifetime_graph(method_calls, object_creations)
        
        # Should have one object with three interactions (creation + 2 methods)
        assert 'user' in lifetime_graph
        assert len(lifetime_graph['user']) == 3
        
        # First interaction should be creation
        assert lifetime_graph['user'][0]['type'] == 'creation'
        assert lifetime_graph['user'][0]['class'] == 'User'
        
        # Next interactions should be method calls in order
        assert lifetime_graph['user'][1]['type'] == 'method_call'
        assert lifetime_graph['user'][1]['method'] == 'login'
        
        assert lifetime_graph['user'][2]['type'] == 'method_call'
        assert lifetime_graph['user'][2]['method'] == 'fetchData'
    
    def test_object_lifetime_with_inferred_objects(self):
        """Test building an object lifetime graph with objects that weren't explicitly created."""
        method_calls = [
            {
                'caller': 'user',
                'method': 'login',
                'args': ['password'],
                'lineno': 1
            },
            {
                'caller': 'service',
                'method': 'authenticate',
                'args': ['user', 'password'],
                'lineno': 2
            }
        ]
        
        object_creations = []  # No explicit creations
        
        lifetime_graph = build_object_lifetime_graph(method_calls, object_creations)
        
        # Should infer both user and service objects
        assert 'user' in lifetime_graph
        assert 'service' in lifetime_graph
        
        # First interaction for each should be inferred creation
        assert lifetime_graph['user'][0]['type'] == 'inferred'
        assert lifetime_graph['service'][0]['type'] == 'inferred'
        
        # Followed by the method calls
        assert lifetime_graph['user'][1]['method'] == 'login'
        assert lifetime_graph['service'][1]['method'] == 'authenticate'
    
    def test_object_lifetime_with_nested_calls(self):
        """Test building an object lifetime graph with nested method calls."""
        method_calls = [
            {
                'caller': 'app',
                'method': 'start',
                'args': [],
                'lineno': 2
            },
            {
                'caller': 'app.start',
                'method': 'initialize',
                'args': [],
                'lineno': 3
            },
            {
                'caller': 'app.start.initialize',
                'method': 'loadConfig',
                'args': [],
                'lineno': 4
            }
        ]
        
        object_creations = [
            {
                'class': 'Application',
                'args': [],
                'target': 'app',
                'lineno': 1
            }
        ]
        
        lifetime_graph = build_object_lifetime_graph(method_calls, object_creations)
        
        # Should have one object with multiple interactions
        assert 'app' in lifetime_graph
        
        # Should include creation and all method calls, including intermediate ones
        interactions = lifetime_graph['app']
        assert len(interactions) > 1
        
        # Methods should be in the right order
        methods = [i['method'] for i in interactions if i.get('type') == 'method_call']
        assert 'start' in methods
        assert 'initialize' in methods
        assert 'loadConfig' in methods
        
        # Check that ordering is correct by line number
        for i in range(1, len(interactions)):
            assert interactions[i-1].get('lineno', 0) <= interactions[i].get('lineno', 0)
    
    def test_object_lifetime_with_async_and_conditional(self):
        """Test building an object lifetime graph with async and conditional flags."""
        method_calls = [
            {
                'caller': 'worker',
                'method': 'processTask',
                'args': [],
                'lineno': 2,
                'is_async': True
            },
            {
                'caller': 'worker',
                'method': 'reportResult',
                'args': [],
                'lineno': 3,
                'is_conditional': True,
                'condition': 'if task.success'
            }
        ]
        
        object_creations = [
            {
                'class': 'Worker',
                'args': [],
                'target': 'worker',
                'lineno': 1
            }
        ]
        
        lifetime_graph = build_object_lifetime_graph(method_calls, object_creations)
        
        # Check that flags are preserved in the interactions
        process_call = next(
            i for i in lifetime_graph['worker'] 
            if i.get('type') == 'method_call' and i.get('method') == 'processTask'
        )
        assert process_call['is_async']
        
        report_call = next(
            i for i in lifetime_graph['worker']
            if i.get('type') == 'method_call' and i.get('method') == 'reportResult'
        )
        assert report_call['is_conditional']
        assert report_call['condition'] == 'if task.success' 