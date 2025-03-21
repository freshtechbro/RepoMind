import React, { useState, useEffect, useCallback } from 'react';
import { FileIcon } from './FileIcon';
import { FolderIcon } from './FolderIcon';

interface TreeNode {
  id: string;
  name: string;
  path: string;
  isDirectory: boolean;
}

interface TreeSearchProps {
  nodes: TreeNode[];
  onNodeSelect: (node: TreeNode) => void;
  placeholder?: string;
  debounceTime?: number;
}

export const TreeSearch: React.FC<TreeSearchProps> = ({ 
  nodes, 
  onNodeSelect, 
  placeholder = 'Search files...', 
  debounceTime = 300 
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState<TreeNode[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  // Debounced search function to avoid excessive filtering for each keystroke
  const performSearch = useCallback(() => {
    if (!searchTerm.trim()) {
      setSearchResults([]);
      setIsSearching(false);
      return;
    }

    setIsSearching(true);
    
    const lowerSearchTerm = searchTerm.toLowerCase();
    const results = nodes.filter(node => 
      node.name.toLowerCase().includes(lowerSearchTerm) || 
      node.path.toLowerCase().includes(lowerSearchTerm)
    );
    
    setSearchResults(results);
    setIsSearching(false);
  }, [searchTerm, nodes]);

  // Debounce search to improve performance
  useEffect(() => {
    const handler = setTimeout(() => {
      performSearch();
    }, debounceTime);

    return () => {
      clearTimeout(handler);
    };
  }, [searchTerm, performSearch, debounceTime]);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };

  const handleNodeClick = (node: TreeNode) => {
    onNodeSelect(node);
  };

  return (
    <div className="tree-search flex flex-col w-full">
      <div className="search-input-container p-2">
        <input
          type="text"
          value={searchTerm}
          onChange={handleSearchChange}
          placeholder={placeholder}
          className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          data-testid="tree-search-input"
        />
      </div>
      
      {searchTerm.trim() !== '' && (
        <div className="search-results max-h-80 overflow-y-auto border-t border-gray-200">
          {isSearching ? (
            <div className="p-4 text-center text-gray-500">Searching...</div>
          ) : searchResults.length > 0 ? (
            <ul className="divide-y divide-gray-200">
              {searchResults.map((node) => (
                <li 
                  key={node.id} 
                  className="p-2 hover:bg-gray-100 cursor-pointer"
                  onClick={() => handleNodeClick(node)}
                >
                  <div className="flex items-center">
                    <span className="mr-2">
                      {node.isDirectory ? <FolderIcon /> : <FileIcon filename={node.name} />}
                    </span>
                    <div className="flex flex-col">
                      <span className="text-sm font-medium">{node.name}</span>
                      <span className="text-xs text-gray-500">{node.path}</span>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <div className="p-4 text-center text-gray-500">No results found</div>
          )}
        </div>
      )}
    </div>
  );
}; 