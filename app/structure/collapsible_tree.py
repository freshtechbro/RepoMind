"""
Collapsible tree module for RepoMind file structure visualization.

This module provides functionality for creating and managing collapsible tree
structures for representing directory hierarchies with expand/collapse controls.
"""

class TreeNode:
    """
    Represents a node in a tree structure with collapsible functionality.
    
    A TreeNode can represent either a file or directory, with directories
    having the ability to be collapsed or expanded to show or hide their children.
    """
    
    def __init__(self, name, path, is_directory=False, parent=None):
        """
        Initialize a new TreeNode.
        
        Args:
            name (str): Display name of the node
            path (str): Full path of the node (used for identification)
            is_directory (bool): Whether this node represents a directory
            parent (TreeNode, optional): Parent node in the tree
        """
        self.name = name
        self.path = path
        self.is_directory = is_directory
        self.parent = parent
        self.children = []
        self.is_collapsed = False
        self.metadata = {}  # Additional data about the node
    
    def add_child(self, child_node):
        """
        Add a child node to this node.
        
        Args:
            child_node (TreeNode): Node to add as a child
        """
        self.children.append(child_node)
        child_node.parent = self
    
    def get_depth(self):
        """
        Calculate the depth of this node in the tree.
        
        Returns:
            int: Depth (0 for root, 1 for first level, etc.)
        """
        depth = 0
        current = self
        while current.parent:
            depth += 1
            current = current.parent
        return depth
    
    def __repr__(self):
        """String representation of the node."""
        return f"TreeNode(name='{self.name}', path='{self.path}', is_directory={self.is_directory})"


class CollapsibleTree:
    """
    Manages a collapsible tree structure for directory visualization.
    
    This class provides methods to collapse and expand nodes, find nodes by path,
    and get currently visible nodes based on the collapsed state of directories.
    """
    
    def __init__(self, root_node):
        """
        Initialize a new CollapsibleTree.
        
        Args:
            root_node (TreeNode): The root node of the tree
        """
        self.root = root_node
    
    def collapse_node(self, node):
        """
        Collapse a node, hiding its children from view.
        
        Args:
            node (TreeNode): The node to collapse
        """
        if node.is_directory:
            node.is_collapsed = True
    
    def expand_node(self, node):
        """
        Expand a node, showing its children.
        
        Args:
            node (TreeNode): The node to expand
        """
        if node.is_directory:
            node.is_collapsed = False
    
    def toggle_node(self, node):
        """
        Toggle the collapse state of a node.
        
        Args:
            node (TreeNode): The node to toggle
        """
        if node.is_directory:
            node.is_collapsed = not node.is_collapsed
    
    def get_visible_nodes(self):
        """
        Get a list of all nodes that should be visible based on collapse state.
        
        Returns:
            list: List of visible TreeNode objects
        """
        visible_nodes = []
        self._collect_visible_nodes(self.root, visible_nodes)
        return visible_nodes
    
    def _collect_visible_nodes(self, node, result_list):
        """
        Recursively collect visible nodes.
        
        Args:
            node (TreeNode): Current node to process
            result_list (list): List to collect visible nodes
        """
        # Add the current node
        result_list.append(node)
        
        # If node is a directory and not collapsed, add its children
        if node.is_directory and not node.is_collapsed:
            for child in node.children:
                self._collect_visible_nodes(child, result_list)
    
    def collapse_all(self):
        """Collapse all directory nodes in the tree."""
        self._set_collapse_state_recursive(self.root, True)
    
    def expand_all(self):
        """Expand all directory nodes in the tree."""
        self._set_collapse_state_recursive(self.root, False)
    
    def _set_collapse_state_recursive(self, node, collapsed):
        """
        Recursively set collapse state for a node and its children.
        
        Args:
            node (TreeNode): Node to process
            collapsed (bool): Whether to collapse (True) or expand (False)
        """
        if node.is_directory:
            node.is_collapsed = collapsed
            for child in node.children:
                self._set_collapse_state_recursive(child, collapsed)
    
    def find_node(self, path):
        """
        Find a node by its path.
        
        Args:
            path (str): Path to search for
            
        Returns:
            TreeNode: The found node, or None if no node exists with the path
        """
        return self._find_node_recursive(self.root, path)
    
    def _find_node_recursive(self, node, path):
        """
        Recursively search for a node with the given path.
        
        Args:
            node (TreeNode): Current node to check
            path (str): Path to search for
            
        Returns:
            TreeNode: The found node, or None if not found
        """
        if node.path == path:
            return node
        
        for child in node.children:
            result = self._find_node_recursive(child, path)
            if result:
                return result
        
        return None
    
    def get_expanded_paths(self):
        """
        Get a list of paths for all expanded directory nodes.
        
        Returns:
            list: List of paths (strings) for expanded directories
        """
        expanded_paths = []
        self._collect_expanded_paths(self.root, expanded_paths)
        return expanded_paths
    
    def _collect_expanded_paths(self, node, result_list):
        """
        Recursively collect paths of expanded directories.
        
        Args:
            node (TreeNode): Current node to process
            result_list (list): List to collect expanded paths
        """
        if node.is_directory and not node.is_collapsed:
            result_list.append(node.path)
            for child in node.children:
                self._collect_expanded_paths(child, result_list)


def build_tree_from_directory_node(dir_node):
    """
    Build a CollapsibleTree from a DirectoryNode (from directory_scanner).
    
    Args:
        dir_node: DirectoryNode from directory_scanner
        
    Returns:
        CollapsibleTree: Tree structure built from the directory node
    """
    # Create root TreeNode
    root = TreeNode(dir_node.name, dir_node.path, is_directory=True)
    
    # Build tree recursively
    _build_tree_recursive(root, dir_node)
    
    return CollapsibleTree(root)

def _build_tree_recursive(tree_node, dir_node):
    """
    Recursively build tree structure from directory nodes.
    
    Args:
        tree_node (TreeNode): Current tree node to add children to
        dir_node: DirectoryNode from directory_scanner
    """
    for child in dir_node.children:
        is_directory = hasattr(child, 'children')
        child_tree_node = TreeNode(child.name, child.path, is_directory=is_directory)
        
        # Add any metadata from the original node
        if hasattr(child, 'metadata'):
            child_tree_node.metadata = child.metadata
        
        tree_node.add_child(child_tree_node)
        
        # Recurse for directories
        if is_directory:
            _build_tree_recursive(child_tree_node, child) 