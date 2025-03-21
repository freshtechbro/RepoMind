import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { TreeVisualization, TreeNode } from './TreeVisualization';

describe('TreeVisualization Component', () => {
  const mockRootNode: TreeNode = {
    id: 'root',
    name: 'root',
    type: 'directory',
    path: '/root',
    children: [
      {
        id: 'dir1',
        name: 'dir1',
        type: 'directory',
        path: '/root/dir1',
        children: [
          {
            id: 'file1',
            name: 'file1.txt',
            type: 'file',
            path: '/root/dir1/file1.txt',
            extension: '.txt',
            size: 1024
          }
        ]
      },
      {
        id: 'file2',
        name: 'file2.js',
        type: 'file',
        path: '/root/file2.js',
        extension: '.js',
        size: 2048
      }
    ]
  };

  const mockStats = {
    total_files: 2,
    total_size: 3072,
    files_by_type: {
      text: 1,
      javascript: 1
    },
    files_by_extension: {
      '.txt': 1,
      '.js': 1
    }
  };

  test('renders the component with tree structure', () => {
    render(
      <TreeVisualization rootNode={mockRootNode} stats={mockStats} />
    );
    
    // Check that root node is rendered
    expect(screen.getByText('root')).toBeInTheDocument();
    
    // Check that first level children are rendered (dir1 should be visible by default)
    expect(screen.getByText('dir1')).toBeInTheDocument();
    expect(screen.getByText('file2.js')).toBeInTheDocument();
    
    // Check stats section exists
    expect(screen.getByText('Repository Statistics')).toBeInTheDocument();
    expect(screen.getByText('Total Files')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument(); // Total files count
  });

  test('handles zoom controls correctly', () => {
    render(
      <TreeVisualization rootNode={mockRootNode} stats={mockStats} />
    );
    
    // Get initial zoom level
    const zoomLevelElement = screen.getByTestId('zoom-level');
    expect(zoomLevelElement.textContent).toBe('100%');
    
    // Test zoom in
    const zoomInButton = screen.getByLabelText('Zoom In');
    fireEvent.click(zoomInButton);
    expect(zoomLevelElement.textContent).toBe('110%');
    
    // Test zoom out
    const zoomOutButton = screen.getByLabelText('Zoom Out');
    fireEvent.click(zoomOutButton);
    expect(zoomLevelElement.textContent).toBe('100%');
    
    // Test reset zoom (after zooming in twice)
    fireEvent.click(zoomInButton);
    fireEvent.click(zoomInButton);
    expect(zoomLevelElement.textContent).toBe('120%');
    
    const resetButton = screen.getByLabelText('Reset Zoom');
    fireEvent.click(resetButton);
    expect(zoomLevelElement.textContent).toBe('100%');
  });

  test('handles node selection', () => {
    const handleNodeSelect = jest.fn();
    
    render(
      <TreeVisualization 
        rootNode={mockRootNode} 
        stats={mockStats} 
        onNodeSelect={handleNodeSelect}
      />
    );
    
    // Click on a node
    fireEvent.click(screen.getByText('file2.js'));
    
    // Check that the handler was called with the correct node
    expect(handleNodeSelect).toHaveBeenCalledTimes(1);
    expect(handleNodeSelect).toHaveBeenCalledWith(mockRootNode.children![1]);
    
    // Check that detail panel appears with correct info
    expect(screen.getByText('Size')).toBeInTheDocument();
    expect(screen.getByText('2.00 KB')).toBeInTheDocument();
  });
}); 