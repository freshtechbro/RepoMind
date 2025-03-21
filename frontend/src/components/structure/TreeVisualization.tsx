import React, { useState, useEffect, useMemo } from 'react';
import { FileTreeNode } from './FileTreeNode';
import { ZoomControls } from './ZoomControls';
import { DetailPanel } from './DetailPanel';
import { TreeStats } from './TreeStats';
import { TreeSearch } from './TreeSearch';

export interface TreeNode {
  id: string;
  name: string;
  type: 'file' | 'directory';
  path: string;
  children?: TreeNode[];
  extension?: string;
  size?: number;
  metadata?: Record<string, any>;
  isCollapsed?: boolean;
}

export interface TreeVisualizationProps {
  rootNode: TreeNode;
  stats: Record<string, any>;
  onNodeSelect?: (node: TreeNode) => void;
}

export const TreeVisualization: React.FC<TreeVisualizationProps> = ({
  rootNode,
  stats,
  onNodeSelect
}) => {
  const [selectedNode, setSelectedNode] = useState<TreeNode | null>(null);
  const [zoomLevel, setZoomLevel] = useState<number>(1);
  const [expandedNodes, setExpandedNodes] = useState<Record<string, boolean>>({});
  
  // Flatten the tree into a searchable list of nodes
  const flattenedNodes = useMemo(() => {
    const nodes: TreeNode[] = [];
    
    const traverse = (node: TreeNode) => {
      // Convert type to isDirectory for TreeSearch component
      const searchNode = {
        ...node,
        isDirectory: node.type === 'directory'
      };
      
      nodes.push(searchNode as any);
      
      if (node.children) {
        node.children.forEach(traverse);
      }
    };
    
    traverse(rootNode);
    return nodes;
  }, [rootNode]);
  
  // Toggle node collapse state
  const toggleNodeCollapse = (nodeId: string) => {
    setExpandedNodes(prev => ({
      ...prev,
      [nodeId]: !prev[nodeId]
    }));
  };
  
  const handleNodeClick = (node: TreeNode) => {
    setSelectedNode(node);
    
    // If it's a directory, toggle its collapse state
    if (node.type === 'directory') {
      toggleNodeCollapse(node.id);
    }
    
    if (onNodeSelect) {
      onNodeSelect(node);
    }
  };
  
  const handleSearchNodeSelect = (node: any) => {
    // Convert back from TreeSearch node to TreeNode
    const treeNode: TreeNode = {
      ...node,
      type: node.isDirectory ? 'directory' : 'file'
    };
    
    setSelectedNode(treeNode);
    
    // Ensure all parent nodes are expanded to show the selected node
    if (treeNode.path) {
      const pathParts = treeNode.path.split('/').filter(Boolean);
      let currentPath = '';
      
      pathParts.forEach(part => {
        currentPath += '/' + part;
        const nodeInPath = flattenedNodes.find(n => n.path === currentPath && n.type === 'directory');
        if (nodeInPath) {
          setExpandedNodes(prev => ({
            ...prev,
            [nodeInPath.id]: true
          }));
        }
      });
    }
    
    if (onNodeSelect) {
      onNodeSelect(treeNode);
    }
  };
  
  const handleZoom = (type: 'in' | 'out' | 'reset') => {
    if (type === 'in') {
      setZoomLevel(prev => Math.min(prev + 0.1, 2.0));
    } else if (type === 'out') {
      setZoomLevel(prev => Math.max(prev - 0.1, 0.5));
    } else {
      setZoomLevel(1);
    }
  };
  
  const handleExpandAll = () => {
    const allExpanded: Record<string, boolean> = {};
    flattenedNodes.forEach(node => {
      if (node.type === 'directory') {
        allExpanded[node.id] = true;
      }
    });
    setExpandedNodes(allExpanded);
  };
  
  const handleCollapseAll = () => {
    setExpandedNodes({});
  };
  
  // Initialize with root expanded
  useEffect(() => {
    if (rootNode) {
      setExpandedNodes(prev => ({
        ...prev,
        [rootNode.id]: true
      }));
    }
  }, [rootNode]);
  
  return (
    <div className="flex flex-col h-full">
      <div className="border-b border-gray-200 dark:border-gray-700 p-4">
        <TreeSearch 
          nodes={flattenedNodes as any} 
          onNodeSelect={handleSearchNodeSelect}
          placeholder="Search files and directories..." 
        />
      </div>
      
      <div className="flex flex-1 overflow-hidden">
        <div className="flex-1 overflow-auto relative">
          <div 
            className="p-4"
            style={{ transform: `scale(${zoomLevel})`, transformOrigin: 'top left' }}
          >
            <div className="mb-4 flex items-center space-x-2">
              <button 
                onClick={handleExpandAll}
                className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded text-sm"
              >
                Expand All
              </button>
              <button 
                onClick={handleCollapseAll}
                className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded text-sm"
              >
                Collapse All
              </button>
            </div>
            
            <FileTreeNode 
              node={rootNode} 
              depth={0} 
              onNodeClick={handleNodeClick}
              isSelected={selectedNode?.id === rootNode.id}
              isExpanded={expandedNodes[rootNode.id]}
            />
          </div>
          
          <div className="absolute top-4 right-4">
            <ZoomControls 
              zoomLevel={zoomLevel} 
              onZoom={handleZoom} 
              minZoom={0.5} 
              maxZoom={2.0} 
            />
          </div>
        </div>
        
        <div className="w-64 border-l border-gray-200 dark:border-gray-700 p-4 flex flex-col">
          {selectedNode && (
            <DetailPanel node={selectedNode} />
          )}
          
          <div className="mt-auto">
            <TreeStats stats={stats} />
          </div>
        </div>
      </div>
    </div>
  );
}; 