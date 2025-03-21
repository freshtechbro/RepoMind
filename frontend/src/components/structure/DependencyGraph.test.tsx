import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { DependencyGraph } from './DependencyGraph';
import { DependencyNode, DependencyEdge } from '../../services/structureService';

describe('DependencyGraph Component', () => {
  const mockNodes: DependencyNode[] = [
    { id: 'node1', name: 'main.py', path: '/repo/main.py', type: 'python' },
    { id: 'node2', name: 'utils.py', path: '/repo/utils.py', type: 'python' },
    { id: 'node3', name: 'config.py', path: '/repo/config.py', type: 'python' }
  ];

  const mockEdges: DependencyEdge[] = [
    { source: 'node1', target: 'node2', type: 'dependency' },
    { source: 'node1', target: 'node3', type: 'dependency' },
    { source: 'node2', target: 'node3', type: 'dependency' }
  ];

  const mockStats = {
    total_files: 3,
    total_dependencies: 3,
    circular_dependencies: []
  };

  test('renders the graph with nodes and edges', () => {
    render(
      <DependencyGraph
        nodes={mockNodes}
        edges={mockEdges}
        stats={mockStats}
      />
    );

    // Check that all node names are rendered
    expect(screen.getByText('main.py')).toBeInTheDocument();
    expect(screen.getByText('utils.py')).toBeInTheDocument();
    expect(screen.getByText('config.py')).toBeInTheDocument();

    // Check that the container exists
    expect(screen.getByTestId('dependency-graph-container')).toBeInTheDocument();
  });

  test('renders graph stats correctly', () => {
    render(
      <DependencyGraph
        nodes={mockNodes}
        edges={mockEdges}
        stats={mockStats}
      />
    );

    expect(screen.getByText('Total Files')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument(); // Total files count
    expect(screen.getByText('3')).toBeInTheDocument(); // Total dependencies count
  });

  test('handles node selection', () => {
    const handleNodeSelect = jest.fn();

    render(
      <DependencyGraph
        nodes={mockNodes}
        edges={mockEdges}
        stats={mockStats}
        onNodeSelect={handleNodeSelect}
      />
    );

    // Click on a node (note: this is a simplification, as the actual DOM structure
    // will depend on the graph rendering implementation)
    const nodeElement = screen.getByText('main.py');
    fireEvent.click(nodeElement);

    expect(handleNodeSelect).toHaveBeenCalledWith(mockNodes[0]);
  });

  test('handles zoom controls', () => {
    render(
      <DependencyGraph
        nodes={mockNodes}
        edges={mockEdges}
        stats={mockStats}
      />
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

    // Test reset zoom
    fireEvent.click(zoomInButton);
    fireEvent.click(zoomInButton);
    const resetButton = screen.getByLabelText('Reset Zoom');
    fireEvent.click(resetButton);
    expect(zoomLevelElement.textContent).toBe('100%');
  });

  test('displays dependency details when a node is selected', () => {
    render(
      <DependencyGraph
        nodes={mockNodes}
        edges={mockEdges}
        stats={mockStats}
      />
    );

    // Click on a node
    const nodeElement = screen.getByText('main.py');
    fireEvent.click(nodeElement);

    // Check that details panel appears
    expect(screen.getByText('Dependencies')).toBeInTheDocument();
    // main.py depends on utils.py and config.py
    expect(screen.getByText('utils.py')).toBeInTheDocument();
    expect(screen.getByText('config.py')).toBeInTheDocument();
  });

  test('renders circular dependencies warning when present', () => {
    const statsWithCircularDeps = {
      ...mockStats,
      circular_dependencies: [['node1', 'node2', 'node1']]
    };

    render(
      <DependencyGraph
        nodes={mockNodes}
        edges={mockEdges}
        stats={statsWithCircularDeps}
      />
    );

    expect(screen.getByText('Circular Dependencies')).toBeInTheDocument();
    expect(screen.getByText('main.py → utils.py → main.py')).toBeInTheDocument();
  });
}); 