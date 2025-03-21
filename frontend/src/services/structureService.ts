import { TreeNode } from '../components/structure/TreeVisualization';

export interface RepositoryStructureResponse {
  root: TreeNode;
  stats: Record<string, any>;
}

export interface DependencyNode {
  id: string;
  name: string;
  path: string;
  type: string;
}

export interface DependencyEdge {
  source: string;
  target: string;
  type: string;
}

export interface DependencyGraphResponse {
  nodes: DependencyNode[];
  edges: DependencyEdge[];
  stats: Record<string, any>;
}

/**
 * Service for fetching repository structure and dependency data
 */
export const structureService = {
  /**
   * Fetch repository structure tree
   * 
   * @param repositoryId - ID of the repository
   * @param excludeDirs - Optional directories to exclude
   * @returns Promise with repository structure data
   */
  async getRepositoryStructure(
    repositoryId: string, 
    excludeDirs?: string[]
  ): Promise<RepositoryStructureResponse> {
    let url = `/api/structure/tree/${repositoryId}`;
    
    // Add exclude_dirs query parameters if provided
    if (excludeDirs && excludeDirs.length > 0) {
      const params = new URLSearchParams();
      excludeDirs.forEach(dir => params.append('exclude_dirs', dir));
      url += `?${params.toString()}`;
    }
    
    const response = await fetch(url);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(
        error.detail || `Failed to fetch repository structure: ${response.statusText}`
      );
    }
    
    return await response.json();
  },
  
  /**
   * Fetch repository dependency graph
   * 
   * @param repositoryId - ID of the repository
   * @param excludeDirs - Optional directories to exclude
   * @returns Promise with dependency graph data
   */
  async getRepositoryDependencies(
    repositoryId: string,
    excludeDirs?: string[]
  ): Promise<DependencyGraphResponse> {
    let url = `/api/structure/dependencies/${repositoryId}`;
    
    // Add exclude_dirs query parameters if provided
    if (excludeDirs && excludeDirs.length > 0) {
      const params = new URLSearchParams();
      excludeDirs.forEach(dir => params.append('exclude_dirs', dir));
      url += `?${params.toString()}`;
    }
    
    const response = await fetch(url);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(
        error.detail || `Failed to fetch repository dependencies: ${response.statusText}`
      );
    }
    
    return await response.json();
  }
}; 