import React from 'react';

export interface TreeStatsProps {
  stats: Record<string, any>;
}

export const TreeStats: React.FC<TreeStatsProps> = ({ stats }) => {
  // Format file size
  const formatFileSize = (size: number): string => {
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

  // Get top N items from an object
  const getTopItems = (obj: Record<string, number>, count: number = 5): [string, number][] => {
    return Object.entries(obj)
      .sort((a, b) => b[1] - a[1])
      .slice(0, count);
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded shadow p-4">
      <h3 className="text-lg font-semibold mb-4">Repository Statistics</h3>
      
      <div className="space-y-4">
        {stats.total_files !== undefined && (
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">Total Files</p>
            <p className="font-medium">{stats.total_files}</p>
          </div>
        )}
        
        {stats.total_size !== undefined && (
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">Total Size</p>
            <p className="font-medium">{formatFileSize(stats.total_size)}</p>
          </div>
        )}
        
        {stats.files_by_type && Object.keys(stats.files_by_type).length > 0 && (
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">Files by Type</p>
            <div className="space-y-1">
              {getTopItems(stats.files_by_type).map(([type, count]) => (
                <div key={type} className="flex justify-between">
                  <span className="text-sm">{type || 'unknown'}</span>
                  <span className="text-sm font-medium">{count}</span>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {stats.files_by_extension && Object.keys(stats.files_by_extension).length > 0 && (
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">Files by Extension</p>
            <div className="space-y-1">
              {getTopItems(stats.files_by_extension).map(([ext, count]) => (
                <div key={ext} className="flex justify-between">
                  <span className="text-sm">{ext || 'no extension'}</span>
                  <span className="text-sm font-medium">{count}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}; 