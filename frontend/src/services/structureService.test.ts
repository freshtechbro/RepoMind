import { structureService } from './structureService';

// Mock global fetch
global.fetch = jest.fn();

describe('Structure Service', () => {
  const mockRepositoryId = 'test-repo-123';
  
  beforeEach(() => {
    // Clear all mocks
    jest.clearAllMocks();
  });

  describe('getRepositoryStructure', () => {
    const mockResponse = {
      root: {
        id: 'root',
        name: 'root',
        type: 'directory',
        path: '/root',
        children: []
      },
      stats: {
        total_files: 10
      }
    };

    test('fetches repository structure successfully', async () => {
      // Setup mock fetch response
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValueOnce(mockResponse)
      });

      // Call the service
      const result = await structureService.getRepositoryStructure(mockRepositoryId);

      // Verify fetch was called correctly
      expect(global.fetch).toHaveBeenCalledWith(`/api/structure/tree/${mockRepositoryId}`);
      
      // Verify response
      expect(result).toEqual(mockResponse);
    });

    test('handles fetch errors', async () => {
      // Setup mock fetch error response
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        statusText: 'Not Found',
        json: jest.fn().mockResolvedValueOnce({ detail: 'Repository not found' })
      });

      // Call the service and expect it to throw
      await expect(structureService.getRepositoryStructure(mockRepositoryId))
        .rejects
        .toThrow('Repository not found');
    });

    test('adds exclude_dirs as query parameters', async () => {
      // Setup mock fetch response
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValueOnce(mockResponse)
      });

      // Call with exclude_dirs
      const excludeDirs = ['node_modules', '.git'];
      await structureService.getRepositoryStructure(mockRepositoryId, excludeDirs);

      // Verify query parameters were added
      const expectedUrl = `/api/structure/tree/${mockRepositoryId}?exclude_dirs=node_modules&exclude_dirs=.git`;
      expect(global.fetch).toHaveBeenCalledWith(expectedUrl);
    });
  });

  describe('getRepositoryDependencies', () => {
    const mockResponse = {
      nodes: [
        { id: 'node1', name: 'File1', path: '/root/file1.js', type: 'javascript' }
      ],
      edges: [
        { source: 'node1', target: 'node2', type: 'dependency' }
      ],
      stats: {
        total_files: 10,
        total_dependencies: 5
      }
    };

    test('fetches repository dependencies successfully', async () => {
      // Setup mock fetch response
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValueOnce(mockResponse)
      });

      // Call the service
      const result = await structureService.getRepositoryDependencies(mockRepositoryId);

      // Verify fetch was called correctly
      expect(global.fetch).toHaveBeenCalledWith(`/api/structure/dependencies/${mockRepositoryId}`);
      
      // Verify response
      expect(result).toEqual(mockResponse);
    });

    test('handles fetch errors', async () => {
      // Setup mock fetch error response
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        statusText: 'Not Found',
        json: jest.fn().mockResolvedValueOnce({ detail: 'Repository not found' })
      });

      // Call the service and expect it to throw
      await expect(structureService.getRepositoryDependencies(mockRepositoryId))
        .rejects
        .toThrow('Repository not found');
    });

    test('adds exclude_dirs as query parameters', async () => {
      // Setup mock fetch response
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValueOnce(mockResponse)
      });

      // Call with exclude_dirs
      const excludeDirs = ['node_modules', '.git'];
      await structureService.getRepositoryDependencies(mockRepositoryId, excludeDirs);

      // Verify query parameters were added
      const expectedUrl = `/api/structure/dependencies/${mockRepositoryId}?exclude_dirs=node_modules&exclude_dirs=.git`;
      expect(global.fetch).toHaveBeenCalledWith(expectedUrl);
    });
  });
}); 