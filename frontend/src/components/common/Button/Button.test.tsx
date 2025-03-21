import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button component', () => {
  test('renders button with correct text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });
  
  test('calls onClick handler when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
  
  test('applies correct variant classes', () => {
    const { rerender } = render(<Button variant="primary">Primary Button</Button>);
    expect(screen.getByText('Primary Button').className).toContain('bg-blue-500');
    
    rerender(<Button variant="secondary">Secondary Button</Button>);
    expect(screen.getByText('Secondary Button').className).toContain('bg-gray-200');
    
    rerender(<Button variant="danger">Danger Button</Button>);
    expect(screen.getByText('Danger Button').className).toContain('bg-red-500');
  });
  
  test('applies correct size classes', () => {
    const { rerender } = render(<Button size="small">Small Button</Button>);
    expect(screen.getByText('Small Button').className).toContain('py-1 px-2');
    
    rerender(<Button size="medium">Medium Button</Button>);
    expect(screen.getByText('Medium Button').className).toContain('py-2 px-4');
    
    rerender(<Button size="large">Large Button</Button>);
    expect(screen.getByText('Large Button').className).toContain('py-3 px-6');
  });
  
  test('disables button when disabled prop is true', () => {
    render(<Button disabled>Disabled Button</Button>);
    expect(screen.getByText('Disabled Button')).toBeDisabled();
    expect(screen.getByText('Disabled Button').className).toContain('opacity-50');
  });
}); 