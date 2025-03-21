import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Header } from './Header';

// Mock next/link
jest.mock('next/link', () => {
  return ({ children, href, className }) => {
    return (
      <a href={href} className={className} data-testid={`link-to-${href}`}>
        {children}
      </a>
    );
  };
});

describe('Header component', () => {
  test('renders logo and navigation links', () => {
    render(<Header />);
    
    expect(screen.getByText('RepoMind')).toBeInTheDocument();
    expect(screen.getByTestId('link-to-/')).toBeInTheDocument();
    expect(screen.getByTestId('link-to-/repositories')).toBeInTheDocument();
    expect(screen.getByTestId('link-to-/docs')).toBeInTheDocument();
  });
  
  test('shows login button when no username is provided', () => {
    render(<Header />);
    
    expect(screen.getByText('Login with GitHub')).toBeInTheDocument();
    expect(screen.getByTestId('link-to-/api/auth/github/login')).toBeInTheDocument();
  });
  
  test('shows username and logout button when username is provided', () => {
    const handleLogout = jest.fn();
    render(<Header username="testuser" onLogout={handleLogout} />);
    
    expect(screen.getByText('Welcome, testuser')).toBeInTheDocument();
    expect(screen.getByText('Logout')).toBeInTheDocument();
    expect(screen.queryByText('Login with GitHub')).not.toBeInTheDocument();
  });
  
  test('calls onLogout when logout button is clicked', () => {
    const handleLogout = jest.fn();
    render(<Header username="testuser" onLogout={handleLogout} />);
    
    fireEvent.click(screen.getByText('Logout'));
    expect(handleLogout).toHaveBeenCalledTimes(1);
  });
}); 