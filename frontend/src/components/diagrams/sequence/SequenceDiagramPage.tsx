import React, { useState } from 'react';
import { Input } from '../../common/Input';
import { Button } from '../../common/Button';

const SequenceDiagramPage: React.FC = () => {
  const [selectedFilePath, setSelectedFilePath] = useState('');
  const [selectedFunction, setSelectedFunction] = useState('');
  const [repositoryId, setRepositoryId] = useState('repo123'); // This would come from context or route params

  const handleFilePathChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedFilePath(e.target.value);
  };

  const handleFunctionChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedFunction(e.target.value);
  };

  const handleGenerateDiagram = () => {
    console.log('Generating diagram for:', {
      repositoryId,
      filePath: selectedFilePath,
      functionName: selectedFunction || undefined
    });
    // Here you would call an API or dispatch an action to generate the diagram
  };

  return (
    <div className="sequence-diagram-page">
      <h1 className="text-2xl font-bold mb-6">Sequence Diagram</h1>
      
      <div className="bg-white shadow-md rounded-lg p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <Input
            id="filePath"
            label="File Path"
            value={selectedFilePath}
            onChange={handleFilePathChange}
            placeholder="Enter file path"
          />
          
          <Input
            id="functionName"
            label="Function Name (optional)"
            value={selectedFunction}
            onChange={handleFunctionChange}
            placeholder="Enter function name"
          />
        </div>
        
        <Button 
          onClick={handleGenerateDiagram}
          disabled={!selectedFilePath}
        >
          Generate Diagram
        </Button>
      </div>
      
      {selectedFilePath && (
        <div className="diagram-container bg-white shadow-md rounded-lg p-6">
          <div className="h-96 flex items-center justify-center border border-gray-200 rounded">
            <p className="text-gray-500">
              {selectedFilePath && selectedFunction
                ? `Sequence diagram for ${selectedFunction} in ${selectedFilePath} would appear here`
                : `Sequence diagram for ${selectedFilePath} would appear here`}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default SequenceDiagramPage; 