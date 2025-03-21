import React from 'react';
import { Button } from '../../components/common/Button';

const RepositoriesList: React.FC = () => {
  // This would typically come from an API
  const repositories = [
    { id: 'repo1', name: 'Example Repository 1', stars: 120, lastUpdated: '2023-11-15' },
    { id: 'repo2', name: 'Example Repository 2', stars: 45, lastUpdated: '2023-12-01' },
    { id: 'repo3', name: 'Example Repository 3', stars: 230, lastUpdated: '2023-10-22' },
  ];

  return (
    <div className="repositories-page">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Your Repositories</h1>
        <Button>Add Repository</Button>
      </div>

      <div className="bg-white shadow-md rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Repository
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Stars
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Last Updated
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {repositories.map((repo) => (
              <tr key={repo.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{repo.name}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-500">{repo.stars}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-500">{repo.lastUpdated}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <Button size="small" variant="secondary" className="mr-2">
                    View
                  </Button>
                  <Button size="small">
                    Analyze
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default RepositoriesList; 