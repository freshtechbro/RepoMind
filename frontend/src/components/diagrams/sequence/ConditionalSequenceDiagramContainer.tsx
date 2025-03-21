import React, { useState, useEffect } from 'react';
import ConditionalSequenceDiagram, { ConditionalSequenceDiagramData } from './ConditionalSequenceDiagram';
import { fetchConditionalDiagramData } from '../../../services/diagramService';

interface ConditionalSequenceDiagramContainerProps {
  repositoryId: string;
  filePath?: string;
  functionName?: string;
  width?: number;
  height?: number;
}

const ConditionalSequenceDiagramContainer: React.FC<ConditionalSequenceDiagramContainerProps> = ({
  repositoryId,
  filePath,
  functionName,
  width = 800,
  height = 600
}) => {
  const [diagramData, setDiagramData] = useState<ConditionalSequenceDiagramData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedElement, setSelectedElement] = useState<string | null>(null);
  const [codeSnippet, setCodeSnippet] = useState<string | null>(null);

  useEffect(() => {
    const loadDiagramData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const data = await fetchConditionalDiagramData(
          repositoryId, 
          filePath, 
          functionName
        );
        
        setDiagramData(data as ConditionalSequenceDiagramData);
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
    <div className="conditional-sequence-diagram-container">
      <div className="diagram-area">
        <ConditionalSequenceDiagram 
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

export default ConditionalSequenceDiagramContainer; 