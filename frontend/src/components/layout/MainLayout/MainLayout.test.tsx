import React from 'react';
import { render, screen } from '@testing-library/react';
import { MainLayout } from './MainLayout';

describe('MainLayout component', () => {
  test('renders children content', () => {
    render(
      <MainLayout>
        <div data-testid="content">Content goes here</div>
      </MainLayout>
    );
    
    expect(screen.getByTestId('content')).toBeInTheDocument();
    expect(screen.getByText('Content goes here')).toBeInTheDocument();
  });
  
  test('renders header when provided', () => {
    render(
      <MainLayout
        header={<div data-testid="header">Header content</div>}
      >
        <div>Main content</div>
      </MainLayout>
    );
    
    expect(screen.getByTestId('header')).toBeInTheDocument();
    expect(screen.getByText('Header content')).toBeInTheDocument();
  });
  
  test('renders sidebar when provided', () => {
    render(
      <MainLayout
        sidebar={<div data-testid="sidebar">Sidebar content</div>}
      >
        <div>Main content</div>
      </MainLayout>
    );
    
    expect(screen.getByTestId('sidebar')).toBeInTheDocument();
    expect(screen.getByText('Sidebar content')).toBeInTheDocument();
  });
  
  test('renders full layout with header, sidebar and content', () => {
    render(
      <MainLayout
        header={<div data-testid="header">Header content</div>}
        sidebar={<div data-testid="sidebar">Sidebar content</div>}
      >
        <div data-testid="content">Main content</div>
      </MainLayout>
    );
    
    expect(screen.getByTestId('header')).toBeInTheDocument();
    expect(screen.getByTestId('sidebar')).toBeInTheDocument();
    expect(screen.getByTestId('content')).toBeInTheDocument();
  });
}); 