import React, { useState, useEffect } from 'react';
import AsyncSequenceDiagram, { AsyncSequenceDiagramData } from './AsyncSequenceDiagram';
import { fetchSequenceDiagramData } from '../../../services/diagramService';

interface AsyncSequenceDiagramContainerProps {
  repositoryId: string;
  filePath?: string;
  functionName?: string;
  width?: number;
  height?: number;
}

const AsyncSequenceDiagramContainer: React.FC<AsyncSequenceDiagramContainerProps> = ({
  repositoryId,
  filePath,
  functionName,
  width = 800,
  height = 600
}) => {
  const [diagramData, setDiagramData] = useState<AsyncSequenceDiagramData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedElement, setSelectedElement] = useState<string | null>(null);
  const [codeSnippet, setCodeSnippet] = useState<string | null>(null);

  useEffect(() => {
    const loadDiagramData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const data = await fetchSequenceDiagramData(
          repositoryId, 
          filePath, 
          functionName,
          true  // Request async-enhanced diagram data
        );
        
        setDiagramData(data as AsyncSequenceDiagramData);
      } catch (err) {
        setError(`Failed to load diagram data: ${err instanceof Error ? err.message : String(err)}`);
      } finally {
        setLoading(false);
      }
    };
    
    loadDiagramData();
  }, [repositoryId, filePath, functionName]);

  const handleElementClick = (elementId: string) => {
    setSelectedElement(elementId);
    
    // Find the message associated with this element to show code snippet
    if (diagramData?.messages) {
      const message = diagramData.messages.find(m => m.id === elementId);
      if (message && message.code_snippet) {
        setCodeSnippet(message.code_snippet);
      } else {
        setCodeSnippet(null);
      }
    }
  };

  if (loading) {
    return <div className="loading">Loading diagram...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (!diagramData) {
    return <div className="no-data">No diagram data available.</div>;
  }

  return (
    <div className="async-sequence-diagram-container">
      <div className="diagram-area">
        <AsyncSequenceDiagram 
          data={diagramData}
          width={width}
          height={height}
          onElementClick={handleElementClick}
        />
      </div>
      
      {codeSnippet && (
        <div className="code-snippet-panel">
          <h3>Code Snippet</h3>
          <pre>{codeSnippet}</pre>
        </div>
      )}
    </div>
  );
};

export default AsyncSequenceDiagramContainer; 