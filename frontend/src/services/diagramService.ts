import axios from 'axios';
import { SequenceDiagramData } from '../components/diagrams/sequence';
import { AsyncSequenceDiagramData } from '../components/diagrams/sequence/AsyncSequenceDiagram';
import { ConditionalSequenceDiagramData } from '../components/diagrams/sequence/ConditionalSequenceDiagram';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';

/**
 * Fetch sequence diagram data for a file or function
 * 
 * @param repositoryId - The ID of the repository
 * @param filePath - The path of the file to analyze
 * @param functionName - Optional function name to focus on
 * @returns Promise resolving to sequence diagram data
 */
export const getSequenceDiagramData = async (
  repositoryId: string,
  filePath: string,
  functionName?: string
): Promise<SequenceDiagramData> => {
  try {
    const params: Record<string, string> = { filePath };
    if (functionName) {
      params.functionName = functionName;
    }
    
    const response = await axios.get(
      `${API_BASE_URL}/repositories/${repositoryId}/sequence-diagram`,
      { params }
    );
    
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(`Server error: ${error.response.data.detail || error.message}`);
    }
    throw error;
  }
};

/**
 * Generate a sequence diagram for a code snippet
 * 
 * @param code - The code snippet to analyze
 * @param language - The programming language of the code (python, javascript, typescript)
 * @returns Promise resolving to sequence diagram data
 */
export const generateSequenceDiagramFromCode = async (
  code: string,
  language: 'python' | 'javascript' | 'typescript'
): Promise<SequenceDiagramData> => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/diagrams/sequence/generate`,
      { code, language }
    );
    
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(`Server error: ${error.response.data.detail || error.message}`);
    }
    throw error;
  }
};

/**
 * Fetch sequence diagram data with enhanced async pattern support
 * 
 * @param repositoryId - The ID of the repository
 * @param filePath - The path of the file to analyze
 * @param functionName - Optional function name to focus on
 * @param includeAsyncPatterns - Whether to include async pattern detection
 * @returns Promise resolving to sequence diagram data
 */
export const fetchSequenceDiagramData = async (
  repositoryId: string,
  filePath?: string,
  functionName?: string,
  includeAsyncPatterns: boolean = false
): Promise<SequenceDiagramData | AsyncSequenceDiagramData> => {
  try {
    const endpoint = includeAsyncPatterns ? 'sequence-async' : 'sequence';
    
    const response = await axios.post(
      `${API_BASE_URL}/diagrams/${endpoint}`,
      {
        repository_id: repositoryId,
        file_path: filePath,
        function_name: functionName,
        options: {
          include_returns: true
        }
      }
    );
    
    return response.data.diagram_data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(`Server error: ${error.response.data.detail || error.message}`);
    }
    throw error;
  }
};

/**
 * Fetch sequence diagram data with enhanced conditional flow visualization
 * 
 * @param repositoryId - The ID of the repository
 * @param filePath - The path of the file to analyze
 * @param functionName - Optional function name to focus on
 * @returns Promise resolving to conditional sequence diagram data
 */
export const fetchConditionalDiagramData = async (
  repositoryId: string,
  filePath?: string,
  functionName?: string
): Promise<ConditionalSequenceDiagramData> => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/diagrams/sequence-conditional`,
      {
        repository_id: repositoryId,
        file_path: filePath,
        function_name: functionName,
        options: {
          include_returns: true
        }
      }
    );
    
    return response.data.diagram_data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(`Server error: ${error.response.data.detail || error.message}`);
    }
    throw error;
  }
};

/**
 * Get call graph data for visualization
 * 
 * @param repositoryId - The ID of the repository
 * @param filePath - The path of the file to analyze
 * @param methodName - Optional method name to focus on
 * @returns Promise resolving to call graph data
 */
export const getCallGraphData = async (
  repositoryId: string,
  filePath: string,
  methodName?: string
): Promise<any> => {
  try {
    const params: Record<string, string> = { filePath };
    if (methodName) {
      params.methodName = methodName;
    }
    
    const response = await axios.get(
      `${API_BASE_URL}/repositories/${repositoryId}/call-graph`,
      { params }
    );
    
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(`Server error: ${error.response.data.detail || error.message}`);
    }
    throw error;
  }
}; 