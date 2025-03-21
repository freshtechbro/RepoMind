import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ZoomPanControls from './ZoomPanControls';

describe('ZoomPanControls Component', () => {
  const defaultProps = {
    zoomLevel: 1.0,
    onZoom: jest.fn(),
    onPan: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders zoom controls correctly', () => {
    render(<ZoomPanControls {...defaultProps} />);
    
    expect(screen.getByLabelText('Zoom In')).toBeInTheDocument();
    expect(screen.getByLabelText('Zoom Out')).toBeInTheDocument();
    expect(screen.getByLabelText('Reset Zoom')).toBeInTheDocument();
    
    // Should display current zoom level as percentage
    expect(screen.getByText('100%')).toBeInTheDocument();
  });

  it('renders pan controls when onPan is provided', () => {
    render(<ZoomPanControls {...defaultProps} />);
    
    expect(screen.getByLabelText('Pan Up')).toBeInTheDocument();
    expect(screen.getByLabelText('Pan Down')).toBeInTheDocument();
    expect(screen.getByLabelText('Pan Left')).toBeInTheDocument();
    expect(screen.getByLabelText('Pan Right')).toBeInTheDocument();
  });

  it('does not render pan controls when onPan is not provided', () => {
    render(<ZoomPanControls {...defaultProps} onPan={undefined} />);
    
    expect(screen.queryByLabelText('Pan Up')).not.toBeInTheDocument();
    expect(screen.queryByLabelText('Pan Down')).not.toBeInTheDocument();
    expect(screen.queryByLabelText('Pan Left')).not.toBeInTheDocument();
    expect(screen.queryByLabelText('Pan Right')).not.toBeInTheDocument();
  });

  it('calls onZoom with correct action when zoom buttons are clicked', () => {
    render(<ZoomPanControls {...defaultProps} />);
    
    // Test zoom in
    fireEvent.click(screen.getByLabelText('Zoom In'));
    expect(defaultProps.onZoom).toHaveBeenCalledWith('in');
    
    // Test zoom out
    fireEvent.click(screen.getByLabelText('Zoom Out'));
    expect(defaultProps.onZoom).toHaveBeenCalledWith('out');
    
    // Test reset zoom
    fireEvent.click(screen.getByLabelText('Reset Zoom'));
    expect(defaultProps.onZoom).toHaveBeenCalledWith('reset');
    
    // Verify total calls
    expect(defaultProps.onZoom).toHaveBeenCalledTimes(3);
  });

  it('calls onPan with correct direction when pan buttons are clicked', () => {
    render(<ZoomPanControls {...defaultProps} />);
    
    // Test pan up
    fireEvent.click(screen.getByLabelText('Pan Up'));
    expect(defaultProps.onPan).toHaveBeenCalledWith('up');
    
    // Test pan down
    fireEvent.click(screen.getByLabelText('Pan Down'));
    expect(defaultProps.onPan).toHaveBeenCalledWith('down');
    
    // Test pan left
    fireEvent.click(screen.getByLabelText('Pan Left'));
    expect(defaultProps.onPan).toHaveBeenCalledWith('left');
    
    // Test pan right
    fireEvent.click(screen.getByLabelText('Pan Right'));
    expect(defaultProps.onPan).toHaveBeenCalledWith('right');
    
    // Verify total calls
    expect(defaultProps.onPan).toHaveBeenCalledTimes(4);
  });

  it('disables zoom in button when at max zoom', () => {
    const maxZoom = 2.0;
    render(<ZoomPanControls {...defaultProps} zoomLevel={maxZoom} maxZoom={maxZoom} />);
    
    const zoomInButton = screen.getByLabelText('Zoom In');
    expect(zoomInButton).toBeDisabled();
    
    // Other buttons should still be enabled
    expect(screen.getByLabelText('Zoom Out')).not.toBeDisabled();
    expect(screen.getByLabelText('Reset Zoom')).not.toBeDisabled();
  });

  it('disables zoom out button when at min zoom', () => {
    const minZoom = 0.5;
    render(<ZoomPanControls {...defaultProps} zoomLevel={minZoom} minZoom={minZoom} />);
    
    const zoomOutButton = screen.getByLabelText('Zoom Out');
    expect(zoomOutButton).toBeDisabled();
    
    // Other buttons should still be enabled
    expect(screen.getByLabelText('Zoom In')).not.toBeDisabled();
    expect(screen.getByLabelText('Reset Zoom')).not.toBeDisabled();
  });

  it('rounds zoom level percentage correctly', () => {
    // Test with different zoom levels
    const testCases = [
      { zoomLevel: 0.25, expected: '25%' },
      { zoomLevel: 1.75, expected: '175%' },
      { zoomLevel: 0.333, expected: '33%' }, // Should round to nearest integer
      { zoomLevel: 2.999, expected: '300%' }
    ];
    
    for (const testCase of testCases) {
      render(<ZoomPanControls {...defaultProps} zoomLevel={testCase.zoomLevel} />);
      expect(screen.getByText(testCase.expected)).toBeInTheDocument();
      // Cleanup for next test case
      screen.unmount();
    }
  });

  it('applies correct accessibility attributes', () => {
    render(<ZoomPanControls {...defaultProps} />);
    
    // All interactive elements should have aria-labels
    const buttons = screen.getAllByRole('button');
    buttons.forEach(button => {
      expect(button).toHaveAttribute('aria-label');
    });
  });
}); 