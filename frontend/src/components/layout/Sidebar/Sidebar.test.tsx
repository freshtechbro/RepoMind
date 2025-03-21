import React from 'react';
import { render, screen } from '@testing-library/react';
import { Sidebar } from './Sidebar';

// Mock next/link
jest.mock('next/link', () => {
  return ({ children, href, className, 'data-testid': dataTestId }) => {
    return (
      <a href={href} className={className} data-testid={dataTestId}>
        {children}
      </a>
    );
  };
});

describe('Sidebar component', () => {
  const mockNavItems = [
    { id: 'home', label: 'Home', href: '/' },
    { id: 'repos', label: 'Repositories', href: '/repositories' },
    { id: 'diagrams', label: 'Diagrams', href: '/diagrams' },
  ];
  
  test('renders all navigation items', () => {
    render(<Sidebar navItems={mockNavItems} />);
    
    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Repositories')).toBeInTheDocument();
    expect(screen.getByText('Diagrams')).toBeInTheDocument();
    
    expect(screen.getByTestId('nav-item-home')).toHaveAttribute('href', '/');
    expect(screen.getByTestId('nav-item-repos')).toHaveAttribute('href', '/repositories');
    expect(screen.getByTestId('nav-item-diagrams')).toHaveAttribute('href', '/diagrams');
  });
  
  test('highlights active item', () => {
    render(<Sidebar navItems={mockNavItems} activeItemId="repos" />);
    
    expect(screen.getByTestId('nav-item-repos').className).toContain('bg-blue-100');
    expect(screen.getByTestId('nav-item-home').className).toContain('text-gray-700');
    expect(screen.getByTestId('nav-item-diagrams').className).toContain('text-gray-700');
  });
  
  test('renders title when provided', () => {
    render(<Sidebar navItems={mockNavItems} title="Navigation" />);
    
    expect(screen.getByText('Navigation')).toBeInTheDocument();
  });
  
  test('does not render title when not provided', () => {
    render(<Sidebar navItems={mockNavItems} />);
    
    expect(screen.queryByRole('heading')).not.toBeInTheDocument();
  });
}); 