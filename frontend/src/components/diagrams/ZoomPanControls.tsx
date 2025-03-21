import React from 'react';

export interface ZoomPanControlsProps {
  zoomLevel: number;
  minZoom?: number;
  maxZoom?: number;
  onZoom: (action: 'in' | 'out' | 'reset') => void;
  onPan?: (direction: 'up' | 'down' | 'left' | 'right') => void;
}

/**
 * A component that provides zoom and pan controls for diagrams.
 * 
 * @param props The component props
 * @returns The ZoomPanControls component
 */
const ZoomPanControls: React.FC<ZoomPanControlsProps> = ({
  zoomLevel,
  minZoom = 0.1,
  maxZoom = 5.0,
  onZoom,
  onPan
}) => {
  const isZoomInDisabled = zoomLevel >= maxZoom;
  const isZoomOutDisabled = zoomLevel <= minZoom;
  
  return (
    <div className="bg-white rounded shadow p-2 flex flex-col absolute right-4 top-4 z-10">
      <div className="mb-2 text-center text-sm text-gray-600">
        {Math.round(zoomLevel * 100)}%
      </div>
      
      <button
        aria-label="Zoom In"
        className="p-2 hover:bg-gray-100 rounded mb-1 disabled:opacity-50"
        onClick={() => onZoom('in')}
        disabled={isZoomInDisabled}
        data-testid="zoom-in-button"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
      </button>
      
      <button
        aria-label="Reset Zoom"
        className="p-2 hover:bg-gray-100 rounded mb-1"
        onClick={() => onZoom('reset')}
        data-testid="reset-zoom-button"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"></path>
        </svg>
      </button>
      
      <button
        aria-label="Zoom Out"
        className="p-2 hover:bg-gray-100 rounded mb-3 disabled:opacity-50"
        onClick={() => onZoom('out')}
        disabled={isZoomOutDisabled}
        data-testid="zoom-out-button"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
      </button>
      
      {onPan && (
        <div className="border-t pt-2">
          <div className="grid grid-cols-3 gap-1">
            <div></div>
            <button
              aria-label="Pan Up"
              className="p-2 hover:bg-gray-100 rounded"
              onClick={() => onPan('up')}
              data-testid="pan-up-button"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="18 15 12 9 6 15"></polyline>
              </svg>
            </button>
            <div></div>
            
            <button
              aria-label="Pan Left"
              className="p-2 hover:bg-gray-100 rounded"
              onClick={() => onPan('left')}
              data-testid="pan-left-button"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="15 18 9 12 15 6"></polyline>
              </svg>
            </button>
            
            <div></div>
            
            <button
              aria-label="Pan Right"
              className="p-2 hover:bg-gray-100 rounded"
              onClick={() => onPan('right')}
              data-testid="pan-right-button"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="9 18 15 12 9 6"></polyline>
              </svg>
            </button>
            
            <div></div>
            <button
              aria-label="Pan Down"
              className="p-2 hover:bg-gray-100 rounded"
              onClick={() => onPan('down')}
              data-testid="pan-down-button"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </button>
            <div></div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ZoomPanControls; 