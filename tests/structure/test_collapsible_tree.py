import unittest
from app.structure.collapsible_tree import TreeNode, CollapsibleTree

class TestCollapsibleTree(unittest.TestCase):
    """Tests for the CollapsibleTree class and TreeNode functionality."""
    
    def setUp(self):
        """Set up a sample tree structure for testing."""
        # Create a simple directory tree
        self.root = TreeNode("root", "root", is_directory=True)
        
        # Add first level children
        self.src = TreeNode("src", "root/src", is_directory=True)
        self.docs = TreeNode("docs", "root/docs", is_directory=True)
        self.readme = TreeNode("README.md", "root/README.md", is_directory=False)
        
        self.root.add_child(self.src)
        self.root.add_child(self.docs)
        self.root.add_child(self.readme)
        
        # Add second level children
        self.main_py = TreeNode("main.py", "root/src/main.py", is_directory=False)
        self.utils_py = TreeNode("utils.py", "root/src/utils.py", is_directory=False)
        self.src.add_child(self.main_py)
        self.src.add_child(self.utils_py)
        
        self.index_md = TreeNode("index.md", "root/docs/index.md", is_directory=False)
        self.api_md = TreeNode("api.md", "root/docs/api.md", is_directory=False)
        self.docs.add_child(self.index_md)
        self.docs.add_child(self.api_md)
        
        # Create the collapsible tree
        self.tree = CollapsibleTree(self.root)
    
    def test_tree_node_creation(self):
        """Test the creation of TreeNode objects."""
        node = TreeNode("test", "path/to/test", is_directory=True)
        self.assertEqual(node.name, "test")
        self.assertEqual(node.path, "path/to/test")
        self.assertTrue(node.is_directory)
        self.assertEqual(node.children, [])
        self.assertEqual(node.parent, None)
        self.assertFalse(node.is_collapsed)
    
    def test_add_child(self):
        """Test adding child nodes to a parent node."""
        parent = TreeNode("parent", "path/parent", is_directory=True)
        child = TreeNode("child", "path/parent/child", is_directory=False)
        
        parent.add_child(child)
        
        self.assertEqual(len(parent.children), 1)
        self.assertEqual(parent.children[0], child)
        self.assertEqual(child.parent, parent)
    
    def test_collapse_expand_node(self):
        """Test collapsing and expanding nodes."""
        # Test collapsing
        self.tree.collapse_node(self.src)
        self.assertTrue(self.src.is_collapsed)
        
        # Test expanding
        self.tree.expand_node(self.src)
        self.assertFalse(self.src.is_collapsed)
    
    def test_toggle_node(self):
        """Test toggling node collapse state."""
        # Initial state is expanded
        self.assertFalse(self.docs.is_collapsed)
        
        # Toggle to collapsed
        self.tree.toggle_node(self.docs)
        self.assertTrue(self.docs.is_collapsed)
        
        # Toggle back to expanded
        self.tree.toggle_node(self.docs)
        self.assertFalse(self.docs.is_collapsed)
    
    def test_get_visible_nodes(self):
        """Test getting only visible nodes from the tree."""
        # All nodes visible initially
        visible_nodes = self.tree.get_visible_nodes()
        self.assertEqual(len(visible_nodes), 7)  # root + 2 dirs + 4 files
        
        # Collapse src directory
        self.tree.collapse_node(self.src)
        visible_nodes = self.tree.get_visible_nodes()
        self.assertEqual(len(visible_nodes), 5)  # root + 2 dirs + 1 file (README.md)
        # main.py and utils.py should not be visible
        visible_paths = [node.path for node in visible_nodes]
        self.assertNotIn("root/src/main.py", visible_paths)
        self.assertNotIn("root/src/utils.py", visible_paths)
        
        # Collapse docs directory
        self.tree.collapse_node(self.docs)
        visible_nodes = self.tree.get_visible_nodes()
        self.assertEqual(len(visible_nodes), 3)  # root + 2 dirs + 1 file
        # No doc files should be visible
        visible_paths = [node.path for node in visible_nodes]
        self.assertNotIn("root/docs/index.md", visible_paths)
        self.assertNotIn("root/docs/api.md", visible_paths)
    
    def test_collapse_all(self):
        """Test collapsing all directory nodes."""
        self.tree.collapse_all()
        
        # All directories should be collapsed
        self.assertTrue(self.root.is_collapsed)
        self.assertTrue(self.src.is_collapsed)
        self.assertTrue(self.docs.is_collapsed)
        
        # Only root should be visible
        visible_nodes = self.tree.get_visible_nodes()
        self.assertEqual(len(visible_nodes), 1)
        self.assertEqual(visible_nodes[0].path, "root")
    
    def test_expand_all(self):
        """Test expanding all directory nodes."""
        # First collapse all
        self.tree.collapse_all()
        
        # Then expand all
        self.tree.expand_all()
        
        # All directories should be expanded
        self.assertFalse(self.root.is_collapsed)
        self.assertFalse(self.src.is_collapsed)
        self.assertFalse(self.docs.is_collapsed)
        
        # All nodes should be visible
        visible_nodes = self.tree.get_visible_nodes()
        self.assertEqual(len(visible_nodes), 7)
    
    def test_find_node(self):
        """Test finding a node by path."""
        # Find existing nodes
        found_node = self.tree.find_node("root/src/main.py")
        self.assertEqual(found_node, self.main_py)
        
        found_node = self.tree.find_node("root/docs")
        self.assertEqual(found_node, self.docs)
        
        # Try to find non-existent node
        found_node = self.tree.find_node("root/non-existent")
        self.assertIsNone(found_node)
    
    def test_get_expanded_paths(self):
        """Test getting the paths of all expanded directories."""
        # Initially all directories are expanded
        expanded_paths = self.tree.get_expanded_paths()
        self.assertIn("root", expanded_paths)
        self.assertIn("root/src", expanded_paths)
        self.assertIn("root/docs", expanded_paths)
        
        # Collapse src directory
        self.tree.collapse_node(self.src)
        expanded_paths = self.tree.get_expanded_paths()
        self.assertIn("root", expanded_paths)
        self.assertNotIn("root/src", expanded_paths)
        self.assertIn("root/docs", expanded_paths)


if __name__ == "__main__":
    unittest.main() 