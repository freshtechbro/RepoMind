import React from 'react';

export interface FolderIconProps {
  isOpen?: boolean;
  className?: string;
}

export const FolderIcon: React.FC<FolderIconProps> = ({ 
  isOpen = false, 
  className = '' 
}) => {
  return (
    <span className={`inline-flex items-center justify-center ${className}`}>
      {isOpen ? '📂' : '📁'}
    </span>
  );
}; 