"""
Module for analyzing dependencies between files in a repository.

Provides functionality to analyze import statements in Python, JavaScript, and TypeScript
files and build a dependency graph representing the relationships between modules.
"""
import os
import re
import ast
from typing import Dict, List, Any, Optional, Set, Tuple


class DependencyNode:
    """
    Represents a node in the dependency graph.
    
    Attributes:
        path: Path to the file relative to the repository root
        dependencies: Set of dependency nodes
        external_dependencies: Set of external dependencies (e.g., imported libraries)
    """
    
    def __init__(self, path: str, file_type: str):
        """
        Initialize a dependency node.
        
        Args:
            path: Path to the file relative to the repository root
            file_type: Type of the file ('python', 'javascript', 'typescript', etc.)
        """
        self.path = path
        self.name = os.path.basename(path)
        self.file_type = file_type
        self.dependencies = set()  # Internal dependencies (other files in the repository)
        self.external_dependencies = set()  # External dependencies (libraries)
        
    def add_dependency(self, dependency: 'DependencyNode') -> None:
        """
        Add a dependency to another file in the repository.
        
        Args:
            dependency: The dependency node
        """
        if dependency != self:  # Avoid self-dependencies
            self.dependencies.add(dependency)
            
    def add_external_dependency(self, name: str, imports: Optional[List[str]] = None) -> None:
        """
        Add an external dependency (imported library).
        
        Args:
            name: Name of the external dependency
            imports: List of specific imports from the dependency
        """
        external_dep = ExternalDependency(name, imports or [])
        self.external_dependencies.add(external_dep)


class ExternalDependency:
    """
    Represents an external dependency (imported library).
    
    Attributes:
        name: Name of the external dependency
        imports: List of specific imports from the dependency
    """
    
    def __init__(self, name: str, imports: List[str]):
        """
        Initialize an external dependency.
        
        Args:
            name: Name of the external dependency
            imports: List of specific imports from the dependency
        """
        self.name = name
        self.imports = imports
        
    def __eq__(self, other):
        if not isinstance(other, ExternalDependency):
            return False
        return self.name == other.name
        
    def __hash__(self):
        return hash(self.name)


class DependencyGraph:
    """
    Represents a dependency graph for a repository.
    
    Attributes:
        nodes: Dictionary of dependency nodes by path
    """
    
    def __init__(self):
        """Initialize an empty dependency graph."""
        self.nodes = {}
        
    def add_node(self, path: str, file_type: str) -> DependencyNode:
        """
        Add a node to the graph or get an existing one.
        
        Args:
            path: Path to the file relative to the repository root
            file_type: Type of the file
            
        Returns:
            The new or existing node
        """
        if path not in self.nodes:
            self.nodes[path] = DependencyNode(path, file_type)
        return self.nodes[path]
        
    def find_circular_dependencies(self) -> List[List[str]]:
        """
        Find circular dependencies in the graph.
        
        Returns:
            List of lists, where each inner list is a cycle of files
        """
        cycles = []
        visited = set()
        path = []
        path_set = set()
        
        def dfs(node):
            if node.path in path_set:
                # Found a cycle
                cycle_start = path.index(node.path)
                cycles.append(path[cycle_start:])
                return
                
            if node.path in visited:
                return
                
            visited.add(node.path)
            path.append(node.path)
            path_set.add(node.path)
            
            for dep in node.dependencies:
                dfs(dep)
                
            path.pop()
            path_set.remove(node.path)
        
        # Run DFS from each node
        for node in self.nodes.values():
            if node.path not in visited:
                dfs(node)
                
        return cycles
        
    def get_dependencies_for(self, path: str) -> List[str]:
        """
        Get the dependencies for a specific file.
        
        Args:
            path: Path to the file
            
        Returns:
            List of paths to dependencies
        """
        if path not in self.nodes:
            return []
            
        return [dep.path for dep in self.nodes[path].dependencies]
        
    def get_dependents_for(self, path: str) -> List[str]:
        """
        Get the files that depend on a specific file.
        
        Args:
            path: Path to the file
            
        Returns:
            List of paths to dependent files
        """
        if path not in self.nodes:
            return []
            
        dependents = []
        for node_path, node in self.nodes.items():
            if self.nodes[path] in node.dependencies:
                dependents.append(node_path)
                
        return dependents


def extract_python_imports(code: str) -> Dict[str, List[str]]:
    """
    Extract import statements from Python code.
    
    Args:
        code: Python source code
        
    Returns:
        Dictionary mapping imported module names to lists of imported symbols
    """
    imports = {}
    
    try:
        # Parse the code into an AST
        tree = ast.parse(code)
        
        # Find all import statements
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                # Handle "import module"
                for name in node.names:
                    imports[name.name] = []
                    
            elif isinstance(node, ast.ImportFrom):
                # Handle "from module import name"
                if node.module:
                    if node.module not in imports:
                        imports[node.module] = []
                    
                    for name in node.names:
                        if name.name != '*':
                            imports[node.module].append(name.name)
    except SyntaxError:
        # If the code has syntax errors, try a regex-based approach
        import_regex = re.compile(r'^(?:from\s+([.\w]+)\s+import\s+([*\w, ]+)|import\s+([.\w, ]+))', re.MULTILINE)
        matches = import_regex.findall(code)
        
        for match in matches:
            if match[0]:  # from X import Y
                module = match[0]
                if module not in imports:
                    imports[module] = []
                
                for name in match[1].split(','):
                    name = name.strip()
                    if name and name != '*':
                        imports[module].append(name)
            else:  # import X
                for module in match[2].split(','):
                    module = module.strip()
                    if module:
                        imports[module] = []
    
    return imports


def extract_js_imports(code: str) -> Dict[str, List[str]]:
    """
    Extract import statements from JavaScript/TypeScript code.
    
    Args:
        code: JavaScript/TypeScript source code
        
    Returns:
        Dictionary mapping imported module names to lists of imported symbols
    """
    imports = {}
    
    # Match ES6 imports: import X from 'module'
    es6_import_regex = re.compile(r'import\s+(\w+|\{[^}]+\}|\*\s+as\s+\w+)\s+from\s+[\'"]([^\'"]*)[\'"]\s*;?', re.MULTILINE)
    es6_matches = es6_import_regex.findall(code)
    
    for match in es6_matches:
        imported_symbols = match[0]
        module = match[1]
        
        if module not in imports:
            imports[module] = []
        
        if imported_symbols.startswith('{'):
            # Handle named imports: import { X, Y } from 'module'
            symbols_str = imported_symbols.strip('{}')
            symbols = [s.strip().split(' as ')[0] for s in symbols_str.split(',')]
            imports[module].extend(symbols)
        elif imported_symbols.startswith('*'):
            # Handle namespace imports: import * as X from 'module'
            imports[module].append('*')
        else:
            # Handle default imports: import X from 'module'
            imports[module].append('default')
    
    # Match import statements without 'from': import 'module'
    direct_import_regex = re.compile(r'import\s+[\'"]([^\'"]*)[\'"]\s*;?', re.MULTILINE)
    direct_matches = direct_import_regex.findall(code)
    
    for module in direct_matches:
        if module not in imports:
            imports[module] = []
    
    # Match require statements: const x = require('module')
    require_regex = re.compile(r'(?:const|let|var)\s+(\w+)\s*=\s*require\([\'"]([^\'"]*)[\'"]\)', re.MULTILINE)
    require_matches = require_regex.findall(code)
    
    for match in require_matches:
        module = match[1]
        if module not in imports:
            imports[module] = ['default']
    
    return imports


def resolve_import_path(import_path: str, file_path: str, root_path: str) -> Optional[str]:
    """
    Resolve an import path to a file path in the repository.
    
    Args:
        import_path: The import path from the code
        file_path: Path to the file containing the import
        root_path: Path to the repository root
        
    Returns:
        Resolved path or None if it can't be resolved
    """
    # Check if it's a relative import
    if import_path.startswith('.'):
        # Convert the file path to a directory path
        dir_path = os.path.dirname(file_path)
        
        # Handle different types of relative imports
        if import_path.startswith('./'):
            # Same directory: ./module
            relative_path = import_path[2:]
        elif import_path.startswith('../'):
            # Parent directory: ../module
            relative_path = import_path
            while relative_path.startswith('../'):
                dir_path = os.path.dirname(dir_path)
                relative_path = relative_path[3:]
        else:
            # Implicit same directory: .module
            relative_path = import_path[1:]
        
        # Construct potential file paths
        potential_paths = [
            os.path.join(dir_path, relative_path),
            os.path.join(dir_path, relative_path + '.py'),
            os.path.join(dir_path, relative_path + '.js'),
            os.path.join(dir_path, relative_path + '.jsx'),
            os.path.join(dir_path, relative_path + '.ts'),
            os.path.join(dir_path, relative_path + '.tsx'),
            os.path.join(dir_path, relative_path, '__init__.py'),
            os.path.join(dir_path, relative_path, 'index.js'),
            os.path.join(dir_path, relative_path, 'index.jsx'),
            os.path.join(dir_path, relative_path, 'index.ts'),
            os.path.join(dir_path, relative_path, 'index.tsx')
        ]
        
        # Check if any potential path exists
        for path in potential_paths:
            if os.path.exists(path):
                # Convert to a path relative to the repository root
                rel_path = os.path.relpath(path, root_path)
                return rel_path
    
    # Check if it's a package-relative import (e.g., 'src/module')
    potential_paths = [
        os.path.join(root_path, import_path),
        os.path.join(root_path, import_path + '.py'),
        os.path.join(root_path, import_path + '.js'),
        os.path.join(root_path, import_path + '.jsx'),
        os.path.join(root_path, import_path + '.ts'),
        os.path.join(root_path, import_path + '.tsx'),
        os.path.join(root_path, import_path, '__init__.py'),
        os.path.join(root_path, import_path, 'index.js'),
        os.path.join(root_path, import_path, 'index.jsx'),
        os.path.join(root_path, import_path, 'index.ts'),
        os.path.join(root_path, import_path, 'index.tsx')
    ]
    
    for path in potential_paths:
        if os.path.exists(path):
            # Convert to a path relative to the repository root
            rel_path = os.path.relpath(path, root_path)
            return rel_path
    
    # Python package imports (e.g., 'package.module')
    if '.' in import_path and not import_path.startswith('.'):
        parts = import_path.split('.')
        
        # Try different combinations of package paths
        for i in range(len(parts)):
            package_path = os.path.join(root_path, *parts[:i+1])
            init_path = os.path.join(package_path, '__init__.py')
            
            if os.path.exists(init_path):
                # Found a package, try to resolve the rest
                remaining_parts = parts[i+1:]
                if not remaining_parts:
                    # This is the module we're looking for
                    rel_path = os.path.relpath(init_path, root_path)
                    return rel_path
                
                # Try to find the submodule
                submodule_path = os.path.join(package_path, *remaining_parts)
                potential_paths = [
                    submodule_path + '.py',
                    os.path.join(submodule_path, '__init__.py')
                ]
                
                for path in potential_paths:
                    if os.path.exists(path):
                        rel_path = os.path.relpath(path, root_path)
                        return rel_path
    
    # Couldn't resolve to a file in the repository (likely an external dependency)
    return None


def analyze_dependencies(repo_path: str) -> DependencyGraph:
    """
    Analyze dependencies between files in a repository.
    
    Args:
        repo_path: Path to the repository root
        
    Returns:
        DependencyGraph: Graph representing the dependencies between files
    """
    graph = DependencyGraph()
    
    # Walk the repository and process each file
    for root, _, files in os.walk(repo_path):
        # Skip common directories to ignore
        if any(ignored in root for ignored in ['/node_modules/', '/.git/', '/__pycache__/']):
            continue
        
        for filename in files:
            file_path = os.path.join(root, filename)
            rel_path = os.path.relpath(file_path, repo_path)
            
            # Determine file type
            ext = os.path.splitext(filename)[1].lower()
            
            if ext == '.py':
                file_type = 'python'
                import_extractor = extract_python_imports
            elif ext in ['.js', '.jsx']:
                file_type = 'javascript'
                import_extractor = extract_js_imports
            elif ext in ['.ts', '.tsx']:
                file_type = 'typescript'
                import_extractor = extract_js_imports
            else:
                # Skip non-code files
                continue
            
            # Create a node for this file
            node = graph.add_node(rel_path, file_type)
            
            # Extract imports
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                imports = import_extractor(code)
                
                # Process each import
                for module, imported_symbols in imports.items():
                    # Try to resolve the import to a file in the repository
                    resolved_path = resolve_import_path(module, file_path, repo_path)
                    
                    if resolved_path:
                        # This is an internal dependency
                        dep_node = graph.add_node(
                            resolved_path, 
                            'python' if resolved_path.endswith('.py') else 
                            'typescript' if resolved_path.endswith(('.ts', '.tsx')) else 
                            'javascript'
                        )
                        node.add_dependency(dep_node)
                    else:
                        # This is an external dependency
                        node.add_external_dependency(module, imported_symbols)
            except (UnicodeDecodeError, PermissionError):
                # Skip files that can't be read
                continue
    
    return graph 