"""
Tests for module dependency analysis functionality.
"""
import os
import tempfile
import unittest.mock as mock
import pytest
from app.structure.dependency_analyzer import (
    analyze_dependencies, 
    extract_python_imports,
    extract_js_imports,
    DependencyGraph
)


class TestDependencyAnalyzer:
    """Tests for module dependency analysis functionality."""

    def test_python_import_extraction(self):
        """Test extraction of imports from Python code."""
        python_code = """
        import os
        import sys
        from datetime import datetime
        from utils.helpers import format_date
        import numpy as np
        
        # Some code
        def my_function():
            from pathlib import Path
            return Path.cwd()
        """
        
        imports = extract_python_imports(python_code)
        
        assert len(imports) == 6
        assert 'os' in imports
        assert 'sys' in imports
        assert 'datetime' in imports
        assert 'utils.helpers' in imports
        assert 'numpy' in imports
        assert 'pathlib' in imports
        
        # Check import details
        assert imports['utils.helpers'] == ['format_date']

    def test_js_import_extraction(self):
        """Test extraction of imports from JavaScript/TypeScript code."""
        js_code = """
        import React from 'react';
        import { useState, useEffect } from 'react';
        import axios from 'axios';
        import * as d3 from 'd3';
        import Component from './Component';
        
        // Some code
        const MyComponent = () => {
            const helper = require('./utils/helper');
            return <div>Hello</div>;
        };
        """
        
        imports = extract_js_imports(js_code)
        
        assert len(imports) == 6
        assert 'react' in imports
        assert 'axios' in imports
        assert 'd3' in imports
        assert './Component' in imports
        assert './utils/helper' in imports
        
        # Check specific imports
        assert imports['react'] == ['default', 'useState', 'useEffect']

    def test_dependency_graph_creation(self):
        """Test creation of dependency graph from files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a simple project structure
            os.makedirs(os.path.join(temp_dir, 'src'))
            os.makedirs(os.path.join(temp_dir, 'src', 'utils'))
            
            # Create files with dependencies
            with open(os.path.join(temp_dir, 'src', 'main.py'), 'w') as f:
                f.write("""
                from utils.helper import format_date
                from datetime import datetime
                
                def main():
                    print(format_date(datetime.now()))
                """)
                
            with open(os.path.join(temp_dir, 'src', 'utils', 'helper.py'), 'w') as f:
                f.write("""
                from datetime import datetime
                
                def format_date(dt):
                    return dt.strftime('%Y-%m-%d')
                """)
            
            # Create a dependency graph
            graph = analyze_dependencies(temp_dir)
            
            # Verify graph structure
            assert isinstance(graph, DependencyGraph)
            
            # Check nodes
            assert len(graph.nodes) >= 2
            assert os.path.join('src', 'main.py') in graph.nodes
            assert os.path.join('src', 'utils', 'helper.py') in graph.nodes
            
            # Check edges
            main_node = graph.nodes[os.path.join('src', 'main.py')]
            helper_node = graph.nodes[os.path.join('src', 'utils', 'helper.py')]
            
            assert helper_node in main_node.dependencies
            
            # Both depend on datetime
            assert 'datetime' in [dep.name for dep in main_node.external_dependencies]
            assert 'datetime' in [dep.name for dep in helper_node.external_dependencies]

    def test_circular_dependency_detection(self):
        """Test detection of circular dependencies."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create files with circular dependencies
            os.makedirs(os.path.join(temp_dir, 'src'))
            
            with open(os.path.join(temp_dir, 'src', 'module_a.py'), 'w') as f:
                f.write("""
                from src.module_b import function_b
                
                def function_a():
                    return function_b()
                """)
                
            with open(os.path.join(temp_dir, 'src', 'module_b.py'), 'w') as f:
                f.write("""
                from src.module_a import function_a
                
                def function_b():
                    return function_a()
                """)
            
            # Create a dependency graph
            graph = analyze_dependencies(temp_dir)
            
            # Verify circular dependencies
            module_a = graph.nodes[os.path.join('src', 'module_a.py')]
            module_b = graph.nodes[os.path.join('src', 'module_b.py')]
            
            assert module_b in module_a.dependencies
            assert module_a in module_b.dependencies
            
            # Check circular dependency detection
            circular_deps = graph.find_circular_dependencies()
            assert len(circular_deps) > 0
            
            # Should detect the A->B->A circular reference
            detected = False
            for cycle in circular_deps:
                if (os.path.join('src', 'module_a.py') in cycle and 
                    os.path.join('src', 'module_b.py') in cycle):
                    detected = True
                    break
            
            assert detected

    def test_mixed_language_dependencies(self):
        """Test analysis of mixed language dependencies (Python and JS/TS)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mixed language project
            os.makedirs(os.path.join(temp_dir, 'src'))
            os.makedirs(os.path.join(temp_dir, 'src', 'frontend'))
            os.makedirs(os.path.join(temp_dir, 'src', 'backend'))
            
            # Python backend files
            with open(os.path.join(temp_dir, 'src', 'backend', 'api.py'), 'w') as f:
                f.write("""
                from datetime import datetime
                from .models import User
                
                def get_users():
                    return [User(id=1, name='test')]
                """)
                
            with open(os.path.join(temp_dir, 'src', 'backend', 'models.py'), 'w') as f:
                f.write("""
                class User:
                    def __init__(self, id, name):
                        self.id = id
                        self.name = name
                """)
            
            # JS frontend files
            with open(os.path.join(temp_dir, 'src', 'frontend', 'api.js'), 'w') as f:
                f.write("""
                import axios from 'axios';
                
                export const fetchUsers = async () => {
                    const response = await axios.get('/api/users');
                    return response.data;
                };
                """)
                
            with open(os.path.join(temp_dir, 'src', 'frontend', 'UserList.jsx'), 'w') as f:
                f.write("""
                import React, { useState, useEffect } from 'react';
                import { fetchUsers } from './api';
                
                const UserList = () => {
                    const [users, setUsers] = useState([]);
                    
                    useEffect(() => {
                        fetchUsers().then(setUsers);
                    }, []);
                    
                    return (
                        <ul>
                            {users.map(user => (
                                <li key={user.id}>{user.name}</li>
                            ))}
                        </ul>
                    );
                };
                
                export default UserList;
                """)
            
            # Create a dependency graph
            graph = analyze_dependencies(temp_dir)
            
            # Verify graph structure
            assert isinstance(graph, DependencyGraph)
            
            # Check nodes exist
            api_py = os.path.join('src', 'backend', 'api.py')
            models_py = os.path.join('src', 'backend', 'models.py')
            api_js = os.path.join('src', 'frontend', 'api.js')
            userlist_jsx = os.path.join('src', 'frontend', 'UserList.jsx')
            
            assert api_py in graph.nodes
            assert models_py in graph.nodes
            assert api_js in graph.nodes
            assert userlist_jsx in graph.nodes
            
            # Check Python dependencies
            assert graph.nodes[models_py] in graph.nodes[api_py].dependencies
            
            # Check JS dependencies
            assert graph.nodes[api_js] in graph.nodes[userlist_jsx].dependencies 