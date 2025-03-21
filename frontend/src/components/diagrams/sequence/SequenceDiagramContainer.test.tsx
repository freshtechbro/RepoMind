import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import SequenceDiagramContainer from './SequenceDiagramContainer';
import { getSequenceDiagramData } from '../../../services/diagramService';

// Mock the diagram service
jest.mock('../../../services/diagramService');
const mockGetSequenceDiagramData = getSequenceDiagramData as jest.MockedFunction<typeof getSequenceDiagramData>;

// Mock the SequenceDiagram component since we're testing the container
jest.mock('./SequenceDiagram', () => {
  return function MockSequenceDiagram({ data, onElementClick }: any) {
    return (
      <div data-testid="sequence-diagram" onClick={() => onElementClick && onElementClick('test-element')}>
        Sequence Diagram Mock
        {data?.title && <div data-testid="diagram-title">{data.title}</div>}
      </div>
    );
  };
});

// Mock the ZoomPanControls component
jest.mock('../ZoomPanControls', () => {
  return function MockZoomPanControls({ zoomLevel, onZoom, onPan }: any) {
    return (
      <div data-testid="zoom-pan-controls">
        <div data-testid="current-zoom">{Math.round(zoomLevel * 100)}%</div>
        <button 
          data-testid="zoom-in-button" 
          onClick={() => onZoom('in')}
        >
          Zoom In
        </button>
        <button 
          data-testid="zoom-out-button" 
          onClick={() => onZoom('out')}
        >
          Zoom Out
        </button>
        <button 
          data-testid="reset-zoom-button" 
          onClick={() => onZoom('reset')}
        >
          Reset Zoom
        </button>
        {onPan && (
          <>
            <button data-testid="pan-up-button" onClick={() => onPan('up')}>Pan Up</button>
            <button data-testid="pan-down-button" onClick={() => onPan('down')}>Pan Down</button>
            <button data-testid="pan-left-button" onClick={() => onPan('left')}>Pan Left</button>
            <button data-testid="pan-right-button" onClick={() => onPan('right')}>Pan Right</button>
          </>
        )}
      </div>
    );
  };
});

describe('SequenceDiagramContainer Component', () => {
  const mockDiagramData = {
    participants: ['User', 'System'],
    messages: [
      { from: 'User', to: 'System', method: 'request' },
      { from: 'System', to: 'User', method: 'response', is_return: true }
    ],
    title: 'Test Diagram'
  };

  beforeEach(() => {
    mockGetSequenceDiagramData.mockResolvedValue(mockDiagramData);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('loads and displays sequence diagram data', async () => {
    render(<SequenceDiagramContainer 
      repositoryId="repo123" 
      functionName="test_function" 
    />);
    
    // Should show loading initially
    expect(screen.getByText('Loading diagram...')).toBeInTheDocument();
    
    // Wait for data to load
    await waitFor(() => {
      expect(mockGetSequenceDiagramData).toHaveBeenCalledWith('repo123', 'test_function');
      expect(screen.getByTestId('diagram-title')).toHaveText('Test Diagram');
    });
  });

  it('handles element click', async () => {
    render(<SequenceDiagramContainer 
      repositoryId="repo123" 
      functionName="test_function" 
    />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByTestId('sequence-diagram')).toBeInTheDocument();
    });
    
    // Click on diagram element
    fireEvent.click(screen.getByTestId('sequence-diagram'));
    
    // Selected element details should be shown
    expect(screen.getByText(/Selected: test-element/i)).toBeInTheDocument();
  });

  it('zooms in when zoom in button is clicked', async () => {
    render(<SequenceDiagramContainer 
      repositoryId="repo123" 
      functionName="test_function" 
    />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByTestId('zoom-pan-controls')).toBeInTheDocument();
    });
    
    // Initial zoom should be 100%
    expect(screen.getByTestId('current-zoom')).toHaveTextContent('100%');
    
    // Click zoom in button
    fireEvent.click(screen.getByTestId('zoom-in-button'));
    
    // Zoom should increase
    expect(screen.getByTestId('current-zoom')).toHaveTextContent('110%');
  });

  it('zooms out when zoom out button is clicked', async () => {
    render(<SequenceDiagramContainer 
      repositoryId="repo123" 
      functionName="test_function" 
    />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByTestId('zoom-pan-controls')).toBeInTheDocument();
    });
    
    // Click zoom out button
    fireEvent.click(screen.getByTestId('zoom-out-button'));
    
    // Zoom should decrease
    expect(screen.getByTestId('current-zoom')).toHaveTextContent('90%');
  });

  it('resets zoom when reset button is clicked', async () => {
    render(<SequenceDiagramContainer 
      repositoryId="repo123" 
      functionName="test_function" 
    />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByTestId('zoom-pan-controls')).toBeInTheDocument();
    });
    
    // First zoom in a few times
    fireEvent.click(screen.getByTestId('zoom-in-button'));
    fireEvent.click(screen.getByTestId('zoom-in-button'));
    
    // Zoom should be 120%
    expect(screen.getByTestId('current-zoom')).toHaveTextContent('120%');
    
    // Click reset button
    fireEvent.click(screen.getByTestId('reset-zoom-button'));
    
    // Zoom should reset to 100%
    expect(screen.getByTestId('current-zoom')).toHaveTextContent('100%');
  });

  it('pans when pan buttons are clicked', async () => {
    render(<SequenceDiagramContainer 
      repositoryId="repo123" 
      functionName="test_function" 
    />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByTestId('zoom-pan-controls')).toBeInTheDocument();
    });
    
    // Get the content element to check transform style changes
    const contentElement = screen.getByClassName('sequence-diagram-content');
    
    // Initial transform should have 0 translation
    expect(contentElement).toHaveStyle('transform: scale(1) translate(0px, 0px)');
    
    // Click pan buttons
    fireEvent.click(screen.getByTestId('pan-right-button'));
    
    // Check that transform style changes (harder to test exactly due to style computation)
    // In real testing, we might use a more sophisticated approach to check computed styles
    expect(contentElement.style.transform).not.toBe('scale(1) translate(0px, 0px)');
  });

  it('handles error when loading diagram data fails', async () => {
    mockGetSequenceDiagramData.mockRejectedValue(new Error('Failed to load diagram'));
    
    render(<SequenceDiagramContainer 
      repositoryId="repo123" 
      functionName="test_function" 
    />);
    
    // Wait for error to be displayed
    await waitFor(() => {
      expect(screen.getByText(/Error loading diagram/i)).toBeInTheDocument();
    });
  });
}); 