import React from 'react';

export interface FileIconProps {
  extension: string;
  className?: string;
}

export const FileIcon: React.FC<FileIconProps> = ({ extension, className = '' }) => {
  const getIconForExtension = (ext: string): string => {
    // Map file extensions to appropriate icons
    switch (ext.toLowerCase()) {
      // Code files
      case '.js':
      case '.jsx':
        return '📄 JS';
      case '.ts':
      case '.tsx':
        return '📄 TS';
      case '.py':
        return '📄 PY';
      case '.java':
        return '📄 JV';
      case '.go':
        return '📄 GO';
      case '.rb':
        return '📄 RB';
      case '.php':
        return '📄 PHP';
      case '.c':
      case '.cpp':
      case '.h':
      case '.hpp':
        return '📄 C/C++';
        
      // Web files
      case '.html':
      case '.htm':
        return '📄 HTML';
      case '.css':
        return '📄 CSS';
      case '.scss':
      case '.sass':
        return '📄 SCSS';
        
      // Data files
      case '.json':
        return '📄 JSON';
      case '.xml':
        return '📄 XML';
      case '.yml':
      case '.yaml':
        return '📄 YAML';
      case '.csv':
        return '📄 CSV';
      case '.md':
        return '📄 MD';
        
      // Media files
      case '.jpg':
      case '.jpeg':
      case '.png':
      case '.gif':
      case '.svg':
        return '🖼️';
        
      // Config files
      case '.gitignore':
        return '📄 GIT';
      case '.env':
        return '📄 ENV';
        
      // Default
      default:
        return '📄';
    }
  };
  
  const icon = getIconForExtension(extension);
  
  return (
    <span className={`inline-flex items-center justify-center ${className}`}>
      {icon}
    </span>
  );
}; 