import React from 'react';

export interface ZoomControlsProps {
  zoomLevel: number;
  minZoom?: number;
  maxZoom?: number;
  onZoom: (type: 'in' | 'out' | 'reset') => void;
}

export const ZoomControls: React.FC<ZoomControlsProps> = ({
  zoomLevel,
  minZoom = 0.5,
  maxZoom = 2.0,
  onZoom
}) => {
  const isZoomInDisabled = zoomLevel >= maxZoom;
  const isZoomOutDisabled = zoomLevel <= minZoom;
  
  return (
    <div className="flex flex-col bg-white dark:bg-gray-800 rounded shadow p-2">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-gray-600 dark:text-gray-300">Zoom</span>
        <span className="text-sm font-medium" data-testid="zoom-level">
          {Math.round(zoomLevel * 100)}%
        </span>
      </div>
      
      <div className="flex space-x-2">
        <button
          aria-label="Zoom Out"
          className={`p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700 
            ${isZoomOutDisabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          onClick={() => !isZoomOutDisabled && onZoom('out')}
          disabled={isZoomOutDisabled}
        >
          <span className="text-lg">−</span>
        </button>
        
        <button
          aria-label="Reset Zoom"
          className="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer"
          onClick={() => onZoom('reset')}
        >
          <span className="text-sm">Reset</span>
        </button>
        
        <button
          aria-label="Zoom In"
          className={`p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700
            ${isZoomInDisabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          onClick={() => !isZoomInDisabled && onZoom('in')}
          disabled={isZoomInDisabled}
        >
          <span className="text-lg">+</span>
        </button>
      </div>
    </div>
  );
}; 