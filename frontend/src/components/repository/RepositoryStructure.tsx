import React, { useState } from 'react';
import { Input } from '../common/Input';
import { Button } from '../common/Button';

const RepositoryStructure: React.FC = () => {
  const [repositoryId, setRepositoryId] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const handleRepositoryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setRepositoryId(e.target.value);
  };
  
  const handleAnalyze = () => {
    if (repositoryId) {
      setIsLoading(true);
      console.log('Analyzing repository structure for:', repositoryId);
      // Simulate API call
      setTimeout(() => {
        setIsLoading(false);
      }, 1500);
    }
  };
  
  return (
    <div className="repository-structure-page">
      <h1 className="text-2xl font-bold mb-6">Repository Structure</h1>
      
      <div className="bg-white shadow-md rounded-lg p-6 mb-6">
        <div className="mb-4">
          <Input
            id="repository"
            label="Repository ID or URL"
            value={repositoryId}
            onChange={handleRepositoryChange}
            placeholder="Enter repository ID or GitHub URL"
          />
        </div>
        
        <Button 
          onClick={handleAnalyze}
          disabled={!repositoryId || isLoading}
        >
          {isLoading ? 'Analyzing...' : 'Analyze Structure'}
        </Button>
      </div>
      
      {isLoading ? (
        <div className="bg-white shadow-md rounded-lg p-6 flex items-center justify-center">
          <p className="text-gray-500">Loading repository structure...</p>
        </div>
      ) : repositoryId && !isLoading ? (
        <div className="bg-white shadow-md rounded-lg p-6">
          <div className="h-96 flex items-center justify-center border border-gray-200 rounded">
            <p className="text-gray-500">Repository structure for {repositoryId} would appear here</p>
          </div>
        </div>
      ) : null}
    </div>
  );
};

export default RepositoryStructure; 