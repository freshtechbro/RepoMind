import React, { useState, useRef, useEffect } from 'react';
import { ZoomControls } from './ZoomControls';
import { DependencyNode, DependencyEdge } from '../../services/structureService';

export interface DependencyGraphProps {
  nodes: DependencyNode[];
  edges: DependencyEdge[];
  stats: Record<string, any>;
  onNodeSelect?: (node: DependencyNode) => void;
}

export const DependencyGraph: React.FC<DependencyGraphProps> = ({
  nodes,
  edges,
  stats,
  onNodeSelect
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [zoomLevel, setZoomLevel] = useState<number>(1);
  const [pan, setPan] = useState<{ x: number, y: number }>({ x: 0, y: 0 });
  const [selectedNode, setSelectedNode] = useState<DependencyNode | null>(null);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [dragStart, setDragStart] = useState<{ x: number, y: number }>({ x: 0, y: 0 });
  
  // Calculate node positions using a force-directed layout simulation
  const [nodePositions, setNodePositions] = useState<Map<string, { x: number, y: number }>>(new Map());
  
  // Simple force-directed layout
  useEffect(() => {
    // Initialize random positions
    const positions = new Map<string, { x: number, y: number }>();
    const width = 800;
    const height = 600;
    
    nodes.forEach(node => {
      positions.set(node.id, {
        x: Math.random() * width,
        y: Math.random() * height
      });
    });
    
    // Run simple force-directed layout
    // In a real implementation, you'd use a proper algorithm like D3-force
    // This is a simplified version for demonstration
    const iterations = 30;
    
    for (let i = 0; i < iterations; i++) {
      // Repulsive forces between all nodes
      for (let j = 0; j < nodes.length; j++) {
        for (let k = j + 1; k < nodes.length; k++) {
          const node1 = nodes[j];
          const node2 = nodes[k];
          const pos1 = positions.get(node1.id)!;
          const pos2 = positions.get(node2.id)!;
          
          const dx = pos2.x - pos1.x;
          const dy = pos2.y - pos1.y;
          const distance = Math.sqrt(dx * dx + dy * dy) || 1;
          const force = 1000 / distance;
          
          // Apply repulsive force
          const moveX = (dx / distance) * force;
          const moveY = (dy / distance) * force;
          
          positions.set(node1.id, { x: pos1.x - moveX, y: pos1.y - moveY });
          positions.set(node2.id, { x: pos2.x + moveX, y: pos2.y + moveY });
        }
      }
      
      // Attractive forces for connected nodes
      edges.forEach(edge => {
        const sourcePos = positions.get(edge.source);
        const targetPos = positions.get(edge.target);
        
        if (sourcePos && targetPos) {
          const dx = targetPos.x - sourcePos.x;
          const dy = targetPos.y - sourcePos.y;
          const distance = Math.sqrt(dx * dx + dy * dy) || 1;
          const force = distance / 30;
          
          // Apply attractive force
          const moveX = (dx / distance) * force;
          const moveY = (dy / distance) * force;
          
          positions.set(edge.source, { x: sourcePos.x + moveX, y: sourcePos.y + moveY });
          positions.set(edge.target, { x: targetPos.x - moveX, y: targetPos.y - moveY });
        }
      });
    }
    
    // Center the graph
    const centerX = width / 2;
    const centerY = height / 2;
    let avgX = 0;
    let avgY = 0;
    
    positions.forEach(pos => {
      avgX += pos.x;
      avgY += pos.y;
    });
    
    avgX /= positions.size;
    avgY /= positions.size;
    
    const offsetX = centerX - avgX;
    const offsetY = centerY - avgY;
    
    positions.forEach((pos, id) => {
      positions.set(id, { x: pos.x + offsetX, y: pos.y + offsetY });
    });
    
    setNodePositions(positions);
  }, [nodes, edges]);
  
  const handleZoom = (type: 'in' | 'out' | 'reset') => {
    if (type === 'in') {
      setZoomLevel(prev => Math.min(prev + 0.1, 2.0));
    } else if (type === 'out') {
      setZoomLevel(prev => Math.max(prev - 0.1, 0.5));
    } else {
      setZoomLevel(1);
      setPan({ x: 0, y: 0 });
    }
  };
  
  const handleNodeClick = (node: DependencyNode) => {
    setSelectedNode(node);
    if (onNodeSelect) {
      onNodeSelect(node);
    }
  };
  
  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button === 0) { // Left mouse button
      setIsDragging(true);
      setDragStart({ x: e.clientX, y: e.clientY });
    }
  };
  
  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      const dx = e.clientX - dragStart.x;
      const dy = e.clientY - dragStart.y;
      setPan(prev => ({ x: prev.x + dx, y: prev.y + dy }));
      setDragStart({ x: e.clientX, y: e.clientY });
    }
  };
  
  const handleMouseUp = () => {
    setIsDragging(false);
  };
  
  // Get node dependencies (outgoing edges)
  const getNodeDependencies = (nodeId: string): DependencyNode[] => {
    const dependencyIds = edges
      .filter(edge => edge.source === nodeId)
      .map(edge => edge.target);
    
    return nodes.filter(node => dependencyIds.includes(node.id));
  };
  
  // Get node dependents (incoming edges)
  const getNodeDependents = (nodeId: string): DependencyNode[] => {
    const dependentIds = edges
      .filter(edge => edge.target === nodeId)
      .map(edge => edge.source);
    
    return nodes.filter(node => dependentIds.includes(node.id));
  };
  
  // Get node name from ID for circular dependencies
  const getNodeNameFromId = (nodeId: string): string => {
    const node = nodes.find(n => n.id === nodeId);
    return node ? node.name : nodeId;
  };
  
  // Format circular dependencies for display
  const formatCircularDependency = (cycle: string[]): string => {
    return cycle.map(nodeId => getNodeNameFromId(nodeId)).join(' → ');
  };
  
  // Node element rendering
  const renderNode = (node: DependencyNode) => {
    const position = nodePositions.get(node.id);
    if (!position) return null;
    
    const isSelected = selectedNode && selectedNode.id === node.id;
    const radius = 20;
    
    // Determine node color based on type
    let nodeColor = '#6B7280'; // Default gray
    if (node.type === 'python') nodeColor = '#3572A5';
    if (node.type === 'javascript') nodeColor = '#F7DF1E';
    if (node.type === 'typescript') nodeColor = '#3178C6';
    
    return (
      <g 
        key={node.id} 
        transform={`translate(${position.x}, ${position.y})`}
        onClick={() => handleNodeClick(node)}
        style={{ cursor: 'pointer' }}
      >
        <circle 
          r={radius} 
          fill={nodeColor}
          stroke={isSelected ? '#2563EB' : '#4B5563'}
          strokeWidth={isSelected ? 3 : 1}
        />
        <text 
          textAnchor="middle" 
          dy="0.3em" 
          fill="#FFFFFF"
          fontSize="10"
        >
          {node.name.length > 10 ? node.name.substring(0, 8) + '...' : node.name}
        </text>
      </g>
    );
  };
  
  // Edge element rendering
  const renderEdge = (edge: DependencyEdge) => {
    const sourcePos = nodePositions.get(edge.source);
    const targetPos = nodePositions.get(edge.target);
    
    if (!sourcePos || !targetPos) return null;
    
    return (
      <line
        key={`${edge.source}-${edge.target}`}
        x1={sourcePos.x}
        y1={sourcePos.y}
        x2={targetPos.x}
        y2={targetPos.y}
        stroke="#9CA3AF"
        strokeWidth={1.5}
        markerEnd="url(#arrowhead)"
      />
    );
  };
  
  return (
    <div className="flex h-full">
      <div 
        className="flex-1 overflow-hidden relative"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <svg 
          ref={svgRef}
          className="w-full h-full"
          data-testid="dependency-graph-container"
          style={{ 
            cursor: isDragging ? 'grabbing' : 'grab',
            transform: `scale(${zoomLevel}) translate(${pan.x}px, ${pan.y}px)`,
            transformOrigin: 'center center'
          }}
        >
          <defs>
            <marker
              id="arrowhead"
              markerWidth="10"
              markerHeight="7"
              refX="30"
              refY="3.5"
              orient="auto"
            >
              <polygon points="0 0, 10 3.5, 0 7" fill="#9CA3AF" />
            </marker>
          </defs>
          {/* Render edges first so they appear behind nodes */}
          {edges.map(renderEdge)}
          {/* Render nodes */}
          {nodes.map(renderNode)}
        </svg>
      </div>
      
      <div className="w-64 border-l border-gray-200 dark:border-gray-700 p-4 flex flex-col">
        {/* Zoom controls */}
        <div className="mb-4">
          <ZoomControls 
            zoomLevel={zoomLevel} 
            onZoom={handleZoom} 
            minZoom={0.5} 
            maxZoom={2.0} 
          />
        </div>
        
        {/* Selected node details */}
        {selectedNode && (
          <div className="bg-white dark:bg-gray-800 rounded shadow p-4 mb-4">
            <h3 className="text-lg font-semibold mb-4">{selectedNode.name}</h3>
            
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Type</p>
                <p className="font-medium">{selectedNode.type}</p>
              </div>
              
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Path</p>
                <p className="font-medium break-all">{selectedNode.path}</p>
              </div>
              
              {/* Dependencies (outgoing) */}
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Dependencies</p>
                <ul className="list-disc list-inside">
                  {getNodeDependencies(selectedNode.id).map(dep => (
                    <li key={dep.id} className="font-medium">{dep.name}</li>
                  ))}
                  {getNodeDependencies(selectedNode.id).length === 0 && (
                    <p className="text-sm italic">No dependencies</p>
                  )}
                </ul>
              </div>
              
              {/* Dependents (incoming) */}
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Used by</p>
                <ul className="list-disc list-inside">
                  {getNodeDependents(selectedNode.id).map(dep => (
                    <li key={dep.id} className="font-medium">{dep.name}</li>
                  ))}
                  {getNodeDependents(selectedNode.id).length === 0 && (
                    <p className="text-sm italic">Not used by other files</p>
                  )}
                </ul>
              </div>
            </div>
          </div>
        )}
        
        {/* Stats */}
        <div className="mt-auto bg-white dark:bg-gray-800 rounded shadow p-4">
          <h3 className="text-lg font-semibold mb-4">Dependency Statistics</h3>
          
          <div className="space-y-4">
            {stats.total_files !== undefined && (
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Total Files</p>
                <p className="font-medium">{stats.total_files}</p>
              </div>
            )}
            
            {stats.total_dependencies !== undefined && (
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Total Dependencies</p>
                <p className="font-medium">{stats.total_dependencies}</p>
              </div>
            )}
            
            {/* Circular dependencies */}
            {stats.circular_dependencies && stats.circular_dependencies.length > 0 && (
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">Circular Dependencies</p>
                <ul className="list-disc list-inside text-amber-600 dark:text-amber-400">
                  {stats.circular_dependencies.map((cycle: string[], index: number) => (
                    <li key={index} className="font-medium text-sm">
                      {formatCircularDependency(cycle)}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}; 