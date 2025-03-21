import React from 'react';
import { TreeNode } from './TreeVisualization';
import { FileIcon } from './FileIcon';
import { FolderIcon } from './FolderIcon';

export interface DetailPanelProps {
  node: TreeNode;
}

export const DetailPanel: React.FC<DetailPanelProps> = ({ node }) => {
  const isDirectory = node.type === 'directory';
  
  // Format the timestamp from unix timestamp to readable date
  const formatDate = (timestamp?: number) => {
    if (!timestamp) return 'Unknown';
    return new Date(timestamp * 1000).toLocaleString();
  };
  
  // Format file size
  const formatFileSize = (size?: number) => {
    if (size === undefined) return 'Unknown';
    
    if (size < 1024) {
      return `${size} bytes`;
    } else if (size < 1024 * 1024) {
      return `${(size / 1024).toFixed(2)} KB`;
    } else if (size < 1024 * 1024 * 1024) {
      return `${(size / (1024 * 1024)).toFixed(2)} MB`;
    } else {
      return `${(size / (1024 * 1024 * 1024)).toFixed(2)} GB`;
    }
  };
  
  return (
    <div className="bg-white dark:bg-gray-800 rounded shadow p-4">
      <h3 className="text-lg font-semibold mb-4 flex items-center">
        {isDirectory ? (
          <FolderIcon className="mr-2 text-yellow-500" />
        ) : (
          <FileIcon extension={node.extension || ''} className="mr-2" />
        )}
        {node.name}
      </h3>
      
      <div className="space-y-3">
        <div>
          <p className="text-sm text-gray-500 dark:text-gray-400">Type</p>
          <p className="font-medium">{isDirectory ? 'Directory' : 'File'}</p>
        </div>
        
        <div>
          <p className="text-sm text-gray-500 dark:text-gray-400">Path</p>
          <p className="font-medium break-all">{node.path}</p>
        </div>
        
        {!isDirectory && (
          <>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Size</p>
              <p className="font-medium">{formatFileSize(node.size)}</p>
            </div>
            
            {node.extension && (
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Extension</p>
                <p className="font-medium">{node.extension}</p>
              </div>
            )}
          </>
        )}
        
        {isDirectory && node.children && (
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">Contents</p>
            <p className="font-medium">{node.children.length} items</p>
          </div>
        )}
        
        {node.metadata && node.metadata.modified && (
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">Modified</p>
            <p className="font-medium">{formatDate(node.metadata.modified)}</p>
          </div>
        )}
      </div>
    </div>
  );
}; 