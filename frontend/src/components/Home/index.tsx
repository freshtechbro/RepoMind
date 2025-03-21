import React from 'react';
import { Button } from '../common/Button';
import { Input } from '../common/Input';

const Home: React.FC = () => {
  const [repositoryUrl, setRepositoryUrl] = React.useState('');

  const handleRepositoryUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setRepositoryUrl(e.target.value);
  };

  const handleAnalyzeRepository = () => {
    if (repositoryUrl) {
      console.log('Analyzing repository:', repositoryUrl);
      // Add navigation or API call here
    }
  };

  return (
    <div className="pt-10">
      <div className="max-w-3xl mx-auto text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-6">
          Welcome to RepoMind
        </h1>
        <p className="text-xl text-gray-600 mb-10">
          Visualize and understand your GitHub repositories with powerful code analysis.
        </p>

        <div className="bg-white shadow-md rounded-lg p-6 mb-10">
          <h2 className="text-2xl font-semibold mb-4">Analyze Repository</h2>
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-grow">
              <Input
                id="repository-url"
                label="GitHub Repository URL"
                placeholder="https://github.com/username/repository"
                value={repositoryUrl}
                onChange={handleRepositoryUrlChange}
              />
            </div>
            <div className="self-end">
              <Button
                onClick={handleAnalyzeRepository}
                disabled={!repositoryUrl}
              >
                Analyze
              </Button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white shadow-md rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-2">Sequence Diagrams</h3>
            <p className="text-gray-600 mb-4">
              Visualize method calls and interactions between components.
            </p>
          </div>
          <div className="bg-white shadow-md rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-2">Class Diagrams</h3>
            <p className="text-gray-600 mb-4">
              Understand class hierarchies and relationships in your codebase.
            </p>
          </div>
          <div className="bg-white shadow-md rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-2">Repository Structure</h3>
            <p className="text-gray-600 mb-4">
              Explore the overall architecture and organization of your code.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home; 