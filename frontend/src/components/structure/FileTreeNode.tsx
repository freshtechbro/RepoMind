import React from 'react';
import { FileIcon } from './FileIcon';
import { FolderIcon } from './FolderIcon';
import { TreeNode } from './TreeVisualization';

export interface FileTreeNodeProps {
  node: TreeNode;
  depth: number;
  onNodeClick: (node: TreeNode) => void;
  isSelected: boolean;
  isExpanded?: boolean;
}

export const FileTreeNode: React.FC<FileTreeNodeProps> = ({
  node,
  depth,
  onNodeClick,
  isSelected,
  isExpanded
}) => {
  const hasChildren = node.type === 'directory' && node.children && node.children.length > 0;
  
  // Use the external isExpanded prop if provided, otherwise default to expanded for first two levels
  const nodeIsExpanded = isExpanded !== undefined ? isExpanded : depth < 2;
  
  const handleToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    // Instead of managing state locally, propagate to parent
    onNodeClick(node);
  };
  
  const handleClick = () => {
    onNodeClick(node);
  };
  
  return (
    <div>
      <div 
        className={`flex items-center py-1 px-2 rounded cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 ${
          isSelected ? 'bg-blue-100 dark:bg-blue-900' : ''
        }`}
        style={{ paddingLeft: `${depth * 16}px` }}
        onClick={handleClick}
        role="button"
        tabIndex={0}
        aria-expanded={hasChildren ? nodeIsExpanded : undefined}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            handleClick();
          } else if (e.key === 'ArrowRight' && hasChildren && !nodeIsExpanded) {
            // Just call handleClick to toggle via parent
            handleClick();
          } else if (e.key === 'ArrowLeft' && hasChildren && nodeIsExpanded) {
            // Just call handleClick to toggle via parent
            handleClick();
          }
        }}
      >
        {hasChildren && (
          <button
            className="mr-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 focus:outline-none"
            onClick={handleToggle}
            aria-label={nodeIsExpanded ? 'Collapse' : 'Expand'}
          >
            <span className="w-4 h-4 inline-block text-center">
              {nodeIsExpanded ? '▼' : '▶'}
            </span>
          </button>
        )}
        
        {node.type === 'directory' ? (
          <FolderIcon isOpen={nodeIsExpanded} className="mr-2 text-yellow-500" />
        ) : (
          <FileIcon filename={node.name} className="mr-2" />
        )}
        
        <span className="truncate">{node.name}</span>
        
        {node.type === 'file' && node.size !== undefined && (
          <span className="ml-2 text-xs text-gray-500 dark:text-gray-400">
            {formatFileSize(node.size)}
          </span>
        )}
      </div>
      
      {hasChildren && nodeIsExpanded && (
        <div>
          {node.children!.map(childNode => (
            <FileTreeNode
              key={childNode.id}
              node={childNode}
              depth={depth + 1}
              onNodeClick={onNodeClick}
              isSelected={isSelected && childNode.id === node.id}
              isExpanded={isExpanded !== undefined ? (childNode.type === 'directory' ? isExpanded : undefined) : undefined}
            />
          ))}
        </div>
      )}
    </div>
  );
};

function formatFileSize(size: number): string {
  if (size < 1024) {
    return `${size} B`;
  } else if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(1)} KB`;
  } else if (size < 1024 * 1024 * 1024) {
    return `${(size / (1024 * 1024)).toFixed(1)} MB`;
  } else {
    return `${(size / (1024 * 1024 * 1024)).toFixed(1)} GB`;
  }
} 