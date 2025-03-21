import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Input } from './Input';

describe('Input component', () => {
  test('renders input with label', () => {
    render(
      <Input 
        id="username" 
        label="Username" 
        value="" 
        onChange={() => {}} 
      />
    );
    
    expect(screen.getByText('Username')).toBeInTheDocument();
    expect(screen.getByTestId('input-username')).toBeInTheDocument();
  });
  
  test('shows required asterisk when required is true', () => {
    render(
      <Input 
        id="email" 
        label="Email" 
        value="" 
        onChange={() => {}} 
        required 
      />
    );
    
    const label = screen.getByText('Email');
    expect(label.parentElement).toHaveTextContent('*');
  });
  
  test('calls onChange handler when input value changes', () => {
    const handleChange = jest.fn();
    render(
      <Input 
        id="search" 
        label="Search" 
        value="" 
        onChange={handleChange} 
      />
    );
    
    fireEvent.change(screen.getByTestId('input-search'), { target: { value: 'test query' } });
    expect(handleChange).toHaveBeenCalledTimes(1);
  });
  
  test('displays error message when error prop is provided', () => {
    render(
      <Input 
        id="password" 
        label="Password" 
        value="" 
        onChange={() => {}} 
        error="Password is required" 
      />
    );
    
    expect(screen.getByText('Password is required')).toBeInTheDocument();
    expect(screen.getByTestId('input-password').className).toContain('border-red-500');
  });
  
  test('disables input when disabled prop is true', () => {
    render(
      <Input 
        id="disabled-input" 
        label="Disabled Input" 
        value="" 
        onChange={() => {}} 
        disabled 
      />
    );
    
    expect(screen.getByTestId('input-disabled-input')).toBeDisabled();
    expect(screen.getByTestId('input-disabled-input').className).toContain('bg-gray-100');
  });
}); 