import React, { useState, useEffect, useCallback } from 'react';
import { SequenceDiagram, SequenceDiagramData } from './';
import { getSequenceDiagramData } from '../../../services/diagramService';
import { ZoomPanControls } from '../';

interface SequenceDiagramContainerProps {
  repositoryId: string;
  filePath: string;
  functionName?: string;
  width?: number;
  height?: number;
}

/**
 * Container component for the sequence diagram that adds additional functionality
 * such as zooming, panning, and other interactive features.
 */
const SequenceDiagramContainer: React.FC<SequenceDiagramContainerProps> = ({
  repositoryId,
  filePath,
  functionName,
  width = 800,
  height = 600
}) => {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [diagramData, setDiagramData] = useState<SequenceDiagramData | null>(null);
  const [selectedElement, setSelectedElement] = useState<string | null>(null);
  const [zoomLevel, setZoomLevel] = useState<number>(1.0);
  const [panPosition, setPanPosition] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  
  const MIN_ZOOM = 0.2;
  const MAX_ZOOM = 3.0;
  const ZOOM_STEP = 0.1;
  const PAN_STEP = 30;

  useEffect(() => {
    const fetchDiagramData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const data = await getSequenceDiagramData(repositoryId, filePath, functionName);
        setDiagramData(data);
      } catch (err) {
        setError(`Failed to fetch sequence diagram data: ${err instanceof Error ? err.message : String(err)}`);
      } finally {
        setLoading(false);
      }
    };
    
    fetchDiagramData();
  }, [repositoryId, filePath, functionName]);

  const handleElementClick = (elementId: string) => {
    setSelectedElement(elementId);
    // Additional logic can be added here, like showing details in a sidebar
  };

  const handleZoom = useCallback((action: 'in' | 'out' | 'reset') => {
    setZoomLevel(prevZoom => {
      if (action === 'in') {
        return Math.min(prevZoom + ZOOM_STEP, MAX_ZOOM);
      } else if (action === 'out') {
        return Math.max(prevZoom - ZOOM_STEP, MIN_ZOOM);
      } else {
        return 1.0; // Reset to default
      }
    });
  }, []);
  
  const handlePan = useCallback((direction: 'up' | 'down' | 'left' | 'right') => {
    setPanPosition(prevPosition => {
      switch (direction) {
        case 'up':
          return { ...prevPosition, y: prevPosition.y + PAN_STEP };
        case 'down':
          return { ...prevPosition, y: prevPosition.y - PAN_STEP };
        case 'left':
          return { ...prevPosition, x: prevPosition.x + PAN_STEP };
        case 'right':
          return { ...prevPosition, x: prevPosition.x - PAN_STEP };
        default:
          return prevPosition;
      }
    });
  }, []);

  if (loading) {
    return <div className="diagram-loading">Loading sequence diagram...</div>;
  }

  if (error) {
    return <div className="diagram-error">Error: {error}</div>;
  }

  if (!diagramData) {
    return <div className="diagram-empty">No sequence diagram data available.</div>;
  }

  return (
    <div className="sequence-diagram-container relative" style={{ width, height, overflow: 'hidden' }}>
      <div 
        className="sequence-diagram-content"
        style={{
          transform: `scale(${zoomLevel}) translate(${panPosition.x}px, ${panPosition.y}px)`,
          transformOrigin: 'center center',
          transition: 'transform 0.2s ease',
          width: '100%',
          height: '100%'
        }}
      >
        <SequenceDiagram
          data={diagramData}
          width={width}
          height={height}
          onElementClick={handleElementClick}
        />
      </div>
      
      <ZoomPanControls 
        zoomLevel={zoomLevel}
        minZoom={MIN_ZOOM}
        maxZoom={MAX_ZOOM}
        onZoom={handleZoom}
        onPan={handlePan}
      />
      
      {selectedElement && (
        <div className="element-details">
          <h4>Element Details</h4>
          <p>Selected element: {selectedElement}</p>
          {/* Additional details can be displayed here */}
        </div>
      )}
    </div>
  );
};

export default SequenceDiagramContainer; 