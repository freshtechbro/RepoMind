import ast
import pytest
from app.analysis.python_extractor import MethodCallExtractor, ObjectCreationExtractor


class TestMethodCallExtractor:
    """Test cases for the Python method call extractor."""

    def test_simple_method_call_extraction(self):
        """Test extraction of simple method calls from Python code."""
        code = """
obj = MyClass()
obj.method1()
obj.method2(param1, param2)
"""
        
        tree = ast.parse(code)
        extractor = MethodCallExtractor()
        extractor.visit(tree)
        
        # Should extract two method calls
        assert len(extractor.calls) == 2
        
        # Check first call
        assert extractor.calls[0]['caller'] == 'obj'
        assert extractor.calls[0]['method'] == 'method1'
        assert len(extractor.calls[0]['args']) == 0
        
        # Check second call
        assert extractor.calls[1]['caller'] == 'obj'
        assert extractor.calls[1]['method'] == 'method2'
        assert len(extractor.calls[1]['args']) == 2

    def test_nested_method_call_extraction(self):
        """Test extraction of nested method calls."""
        code = """
result = obj1.method1().method2()
"""
        
        tree = ast.parse(code)
        extractor = MethodCallExtractor()
        extractor.visit(tree)
        
        # Should extract two method calls
        assert len(extractor.calls) == 2
        
        # Check method calls (order depends on AST traversal)
        methods = {call['method'] for call in extractor.calls}
        assert 'method1' in methods
        assert 'method2' in methods

    def test_method_call_with_complex_args(self):
        """Test extraction of method calls with complex arguments."""
        code = """
obj.complex_method(
    arg1,
    obj2.get_value(),
    [1, 2, 3],
    {"key": "value"}
)
"""
        
        tree = ast.parse(code)
        extractor = MethodCallExtractor()
        extractor.visit(tree)
        
        assert len(extractor.calls) == 2  # one for complex_method, one for get_value
        
        # Find the complex_method call
        complex_call = next(call for call in extractor.calls if call['method'] == 'complex_method')
        assert complex_call['caller'] == 'obj'
        assert len(complex_call['args']) == 4

    def test_method_call_in_conditional_blocks(self):
        """Test extraction of method calls inside conditional blocks."""
        code = """
if condition:
    obj.method_if()
else:
    obj.method_else()

for item in items:
    item.process()
"""
        
        tree = ast.parse(code)
        extractor = MethodCallExtractor()
        extractor.visit(tree)
        
        assert len(extractor.calls) == 3
        methods = {call['method'] for call in extractor.calls}
        assert 'method_if' in methods
        assert 'method_else' in methods
        assert 'process' in methods

    def test_extraction_with_source_location(self):
        """Test that source location is correctly extracted for method calls."""
        code = """
obj.method1()
obj.method2()
"""
        
        tree = ast.parse(code)
        extractor = MethodCallExtractor()
        extractor.visit(tree)
        
        assert len(extractor.calls) == 2
        
        # Verify line numbers are captured
        assert 'lineno' in extractor.calls[0]
        assert 'lineno' in extractor.calls[1]
        assert extractor.calls[0]['lineno'] < extractor.calls[1]['lineno']


class TestObjectCreationExtractor:
    """Test cases for the Python object creation extractor."""
    
    def test_simple_object_creation(self):
        """Test extraction of simple object creation."""
        code = """
obj = MyClass()
another = AnotherClass(param1, "string param")
"""
        
        tree = ast.parse(code)
        extractor = ObjectCreationExtractor()
        extractor.visit(tree)
        
        # Should extract two object creations
        assert len(extractor.creations) == 2
        
        # Check first creation
        assert extractor.creations[0]['class'] == 'MyClass'
        assert len(extractor.creations[0]['args']) == 0
        assert extractor.creations[0]['target'] == 'obj'
        
        # Check second creation
        assert extractor.creations[1]['class'] == 'AnotherClass'
        assert len(extractor.creations[1]['args']) == 2
        assert extractor.creations[1]['target'] == 'another'
    
    def test_object_creation_in_complex_assignments(self):
        """Test extraction of object creation with complex assignments."""
        code = """
# Simple assignment
user = User()

# Multiple assignment
admin1 = admin2 = Admin()

# Assignment with attributes
self.logger = Logger()

# No assignment (anonymous object)
Database().connect()

# Assignment in dictionary
users = {'admin': Admin(), 'guest': Guest()}
"""
        
        tree = ast.parse(code)
        extractor = ObjectCreationExtractor()
        extractor.visit(tree)
        
        # Should extract 6 object creations: User, Admin, Logger, Database, Admin in dict, Guest in dict
        assert len(extractor.creations) == 6
        
        # Check specific target names
        targets = {creation['target'] for creation in extractor.creations if creation['target'] is not None}
        assert 'user' in targets
        assert 'admin1' in targets  # First name in multiple assignment
        assert 'self.logger' in targets
        
        # Check for anonymous object (no target)
        anonymous = [c for c in extractor.creations if c['class'] == 'Database']
        assert len(anonymous) == 1
        assert anonymous[0]['target'] is None
        
        # Check for dictionary value objects
        dict_values = [c for c in extractor.creations if c['class'] in ('Admin', 'Guest') and c['target'] is None]
        assert len(dict_values) == 2
    
    def test_nested_object_creation(self):
        """Test extraction of nested object creation."""
        code = """
# Object creation in method arguments
result = ProcessResult(ErrorHandler())

# Object creation as argument in method call
user.process(ValidationResult(data))
"""
        
        tree = ast.parse(code)
        extractor = ObjectCreationExtractor()
        extractor.visit(tree)
        
        # Should extract 3 object creations
        assert len(extractor.creations) == 3
        
        # Verify classes
        classes = {creation['class'] for creation in extractor.creations}
        assert 'ProcessResult' in classes
        assert 'ErrorHandler' in classes
        assert 'ValidationResult' in classes
        
        # Check target of outer creation
        process_result = next(c for c in extractor.creations if c['class'] == 'ProcessResult')
        assert process_result['target'] == 'result'
        
        # Inner creations should not have targets
        inner_creations = [c for c in extractor.creations if c['class'] in ('ErrorHandler', 'ValidationResult')]
        for creation in inner_creations:
            assert creation['target'] is None 