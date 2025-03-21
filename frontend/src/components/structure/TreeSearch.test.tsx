import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TreeSearch } from './TreeSearch';

// Mock node data
const mockNodes = [
  { id: '1', name: 'src', path: '/src', isDirectory: true },
  { id: '2', name: 'components', path: '/src/components', isDirectory: true }, 
  { id: '3', name: 'App.tsx', path: '/src/App.tsx', isDirectory: false },
  { id: '4', name: 'index.tsx', path: '/src/index.tsx', isDirectory: false },
  { id: '5', name: 'Button.tsx', path: '/src/components/Button.tsx', isDirectory: false },
  { id: '6', name: 'utils', path: '/src/utils', isDirectory: true },
  { id: '7', name: 'helpers.ts', path: '/src/utils/helpers.ts', isDirectory: false },
];

describe('TreeSearch Component', () => {
  const handleNodeSelectMock = jest.fn();
  
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  test('renders search input', () => {
    render(
      <TreeSearch 
        nodes={mockNodes} 
        onNodeSelect={handleNodeSelectMock} 
      />
    );
    
    expect(screen.getByPlaceholderText('Search files...')).toBeInTheDocument();
  });
  
  test('searches for files and shows results', async () => {
    render(
      <TreeSearch 
        nodes={mockNodes} 
        onNodeSelect={handleNodeSelectMock} 
      />
    );
    
    const searchInput = screen.getByPlaceholderText('Search files...');
    userEvent.type(searchInput, 'tsx');
    
    await waitFor(() => {
      // Should find 3 .tsx files
      expect(screen.getByText('App.tsx')).toBeInTheDocument();
      expect(screen.getByText('index.tsx')).toBeInTheDocument();
      expect(screen.getByText('Button.tsx')).toBeInTheDocument();
    });
  });
  
  test('shows "No results found" when no matches', async () => {
    render(
      <TreeSearch 
        nodes={mockNodes} 
        onNodeSelect={handleNodeSelectMock} 
      />
    );
    
    const searchInput = screen.getByPlaceholderText('Search files...');
    userEvent.type(searchInput, 'nonexistent');
    
    await waitFor(() => {
      expect(screen.getByText('No results found')).toBeInTheDocument();
    });
  });
  
  test('selects node when clicked', async () => {
    render(
      <TreeSearch 
        nodes={mockNodes} 
        onNodeSelect={handleNodeSelectMock} 
      />
    );
    
    const searchInput = screen.getByPlaceholderText('Search files...');
    userEvent.type(searchInput, 'App');
    
    await waitFor(() => {
      expect(screen.getByText('App.tsx')).toBeInTheDocument();
    });
    
    fireEvent.click(screen.getByText('App.tsx'));
    
    expect(handleNodeSelectMock).toHaveBeenCalledWith(mockNodes[2]);
  });
  
  test('clears search results when input is cleared', async () => {
    render(
      <TreeSearch 
        nodes={mockNodes} 
        onNodeSelect={handleNodeSelectMock} 
      />
    );
    
    const searchInput = screen.getByPlaceholderText('Search files...');
    userEvent.type(searchInput, 'tsx');
    
    await waitFor(() => {
      expect(screen.getByText('App.tsx')).toBeInTheDocument();
    });
    
    // Clear the input
    userEvent.clear(searchInput);
    
    await waitFor(() => {
      expect(screen.queryByText('App.tsx')).not.toBeInTheDocument();
    });
  });
  
  test('handles case-insensitive search', async () => {
    render(
      <TreeSearch 
        nodes={mockNodes} 
        onNodeSelect={handleNodeSelectMock} 
      />
    );
    
    const searchInput = screen.getByPlaceholderText('Search files...');
    userEvent.type(searchInput, 'TSX');
    
    await waitFor(() => {
      // Should still find .tsx files with uppercase search
      expect(screen.getByText('App.tsx')).toBeInTheDocument();
      expect(screen.getByText('index.tsx')).toBeInTheDocument();
      expect(screen.getByText('Button.tsx')).toBeInTheDocument();
    });
  });
  
  test('displays path for search results', async () => {
    render(
      <TreeSearch 
        nodes={mockNodes} 
        onNodeSelect={handleNodeSelectMock} 
      />
    );
    
    const searchInput = screen.getByPlaceholderText('Search files...');
    userEvent.type(searchInput, 'Button');
    
    await waitFor(() => {
      expect(screen.getByText('Button.tsx')).toBeInTheDocument();
      expect(screen.getByText('/src/components/Button.tsx')).toBeInTheDocument();
    });
  });
  
  test('matches by path as well as filename', async () => {
    render(
      <TreeSearch 
        nodes={mockNodes} 
        onNodeSelect={handleNodeSelectMock} 
      />
    );
    
    const searchInput = screen.getByPlaceholderText('Search files...');
    userEvent.type(searchInput, 'utils');
    
    await waitFor(() => {
      // Should find both the utils directory and files within it
      expect(screen.getByText('utils')).toBeInTheDocument();
      expect(screen.getByText('helpers.ts')).toBeInTheDocument();
    });
  });
}); 