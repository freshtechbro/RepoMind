import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { FileTreeNode } from './FileTreeNode';
import { TreeNode } from './TreeVisualization';

describe('FileTreeNode Component', () => {
  const mockFileNode: TreeNode = {
    id: 'file1',
    name: 'example.js',
    type: 'file',
    path: '/root/example.js',
    extension: '.js',
    size: 1024
  };

  const mockDirectoryNode: TreeNode = {
    id: 'dir1',
    name: 'src',
    type: 'directory',
    path: '/root/src',
    children: [
      {
        id: 'file2',
        name: 'index.js',
        type: 'file',
        path: '/root/src/index.js',
        extension: '.js',
        size: 512
      }
    ]
  };

  const mockOnNodeClick = jest.fn();

  beforeEach(() => {
    mockOnNodeClick.mockClear();
  });

  test('renders a file node correctly', () => {
    render(
      <FileTreeNode 
        node={mockFileNode} 
        depth={1} 
        onNodeClick={mockOnNodeClick}
        isSelected={false}
      />
    );

    // Check file name is displayed
    expect(screen.getByText('example.js')).toBeInTheDocument();
    
    // Check file size is displayed
    expect(screen.getByText('1.0 KB')).toBeInTheDocument();
    
    // File nodes should not have expand/collapse buttons
    const expandButtons = screen.queryByRole('button', { name: /expand|collapse/i });
    expect(expandButtons).not.toBeInTheDocument();
  });

  test('renders a directory node correctly', () => {
    render(
      <FileTreeNode 
        node={mockDirectoryNode} 
        depth={1} 
        onNodeClick={mockOnNodeClick}
        isSelected={false}
      />
    );

    // Check directory name is displayed
    expect(screen.getByText('src')).toBeInTheDocument();
    
    // Directory should have an expand/collapse button
    expect(screen.getByLabelText('Expand')).toBeInTheDocument();
    
    // By default, child nodes should not be visible
    expect(screen.queryByText('index.js')).not.toBeInTheDocument();
  });

  test('expands and collapses a directory node', () => {
    render(
      <FileTreeNode 
        node={mockDirectoryNode} 
        depth={1} 
        onNodeClick={mockOnNodeClick}
        isSelected={false}
      />
    );

    // Initially, child node should not be visible
    expect(screen.queryByText('index.js')).not.toBeInTheDocument();
    
    // Click the expand button
    fireEvent.click(screen.getByLabelText('Expand'));
    
    // Child node should now be visible
    expect(screen.getByText('index.js')).toBeInTheDocument();
    
    // Toggle button should now be a collapse button
    expect(screen.getByLabelText('Collapse')).toBeInTheDocument();
    
    // Click the collapse button
    fireEvent.click(screen.getByLabelText('Collapse'));
    
    // Child node should be hidden again
    expect(screen.queryByText('index.js')).not.toBeInTheDocument();
  });

  test('calls onNodeClick when clicked', () => {
    render(
      <FileTreeNode 
        node={mockFileNode} 
        depth={1} 
        onNodeClick={mockOnNodeClick}
        isSelected={false}
      />
    );

    // Click the node
    fireEvent.click(screen.getByText('example.js'));
    
    // Check that the click handler was called with the right node
    expect(mockOnNodeClick).toHaveBeenCalledTimes(1);
    expect(mockOnNodeClick).toHaveBeenCalledWith(mockFileNode);
  });

  test('applies selected styles when isSelected is true', () => {
    const { rerender } = render(
      <FileTreeNode 
        node={mockFileNode} 
        depth={1} 
        onNodeClick={mockOnNodeClick}
        isSelected={false}
      />
    );

    // Node should not have selected class initially
    const nodeElement = screen.getByText('example.js').parentElement;
    expect(nodeElement).not.toHaveClass('bg-blue-100');

    // Re-render with isSelected=true
    rerender(
      <FileTreeNode 
        node={mockFileNode} 
        depth={1} 
        onNodeClick={mockOnNodeClick}
        isSelected={true}
      />
    );

    // Node should have selected class now
    expect(nodeElement).toHaveClass('bg-blue-100');
  });

  test('handles keyboard navigation', () => {
    render(
      <FileTreeNode 
        node={mockDirectoryNode} 
        depth={1} 
        onNodeClick={mockOnNodeClick}
        isSelected={false}
      />
    );

    const nodeElement = screen.getByText('src').parentElement;
    
    // Press Enter to select the node
    fireEvent.keyDown(nodeElement!, { key: 'Enter' });
    expect(mockOnNodeClick).toHaveBeenCalledTimes(1);
    
    // Press ArrowRight to expand the directory
    fireEvent.keyDown(nodeElement!, { key: 'ArrowRight' });
    
    // Child node should be visible
    expect(screen.getByText('index.js')).toBeInTheDocument();
    
    // Press ArrowLeft to collapse the directory
    fireEvent.keyDown(nodeElement!, { key: 'ArrowLeft' });
    
    // Child node should be hidden
    expect(screen.queryByText('index.js')).not.toBeInTheDocument();
  });
}); 