import React from 'react';
import { render, screen } from '@testing-library/react';
import SequenceDiagram, { SequenceDiagramData } from './SequenceDiagram';

// Mock JointJS since it requires DOM manipulation that isn't available in the test environment
jest.mock('jointjs', () => {
  return {
    dia: {
      Graph: jest.fn().mockImplementation(() => ({
        clear: jest.fn(),
        addCell: jest.fn()
      })),
      Paper: jest.fn().mockImplementation(() => ({
        on: jest.fn(),
        remove: jest.fn(),
        setDimensions: jest.fn()
      })),
      Element: {
        extend: jest.fn().mockImplementation(() => function MockElement(config: any) {
          return { config, id: 'mock-element-id' };
        }),
        prototype: {
          defaults: {}
        }
      },
      Link: {
        extend: jest.fn().mockImplementation(() => function MockLink(config: any) {
          return { 
            config, 
            id: 'mock-link-id',
            attr: jest.fn(),
            set: jest.fn()
          };
        }),
        prototype: {
          defaults: {}
        }
      }
    },
    shapes: {
      sequence: {}
    },
    util: {
      defaultsDeep: jest.fn().mockImplementation((obj) => obj)
    }
  };
});

describe('SequenceDiagram Component', () => {
  const sampleData: SequenceDiagramData = {
    participants: ['Client', 'Server', 'Database'],
    messages: [
      {
        from: 'Client',
        to: 'Server',
        method: 'request',
        args: ['data']
      },
      {
        from: 'Server',
        to: 'Database',
        method: 'query',
        args: ['SELECT * FROM table']
      },
      {
        from: 'Database',
        to: 'Server',
        method: 'results',
        is_return: true
      },
      {
        from: 'Server',
        to: 'Client',
        method: 'response',
        is_return: true
      }
    ],
    title: 'Test Sequence Diagram'
  };

  it('renders the component with a title', () => {
    render(<SequenceDiagram data={sampleData} />);
    
    // Check that the title is rendered
    expect(screen.getByText('Test Sequence Diagram')).toBeInTheDocument();
    
    // Check that the container for the diagram is rendered
    expect(document.querySelector('.sequence-diagram-paper')).toBeInTheDocument();
  });

  it('renders without a title', () => {
    const dataWithoutTitle = { ...sampleData, title: undefined };
    render(<SequenceDiagram data={dataWithoutTitle} />);
    
    // Title should not be rendered
    expect(screen.queryByText('Test Sequence Diagram')).not.toBeInTheDocument();
    
    // Container should still be rendered
    expect(document.querySelector('.sequence-diagram-paper')).toBeInTheDocument();
  });

  it('handles click events', () => {
    // Create a mock function for the click handler
    const handleClick = jest.fn();
    
    render(<SequenceDiagram data={sampleData} onElementClick={handleClick} />);
    
    // The actual click testing is limited in JSDOM, but we can verify setup
    const container = document.querySelector('.sequence-diagram-container');
    expect(container).toBeInTheDocument();
    
    // Since we're mocking JointJS, we can't actually test the click behavior
    // In a real environment, this would be tested with integration tests
  });

  it('renders a diagram with asynchronous messages', () => {
    const asyncData: SequenceDiagramData = {
      participants: ['Client', 'Server', 'BackgroundJob'],
      messages: [
        {
          from: 'Client',
          to: 'Server',
          method: 'submitJob',
          args: ['data']
        },
        {
          from: 'Server',
          to: 'BackgroundJob',
          method: 'processAsync',
          args: ['data'],
          is_async: true
        },
        {
          from: 'Server',
          to: 'Client',
          method: 'jobSubmitted',
          is_return: true
        },
        {
          from: 'BackgroundJob',
          to: 'Server',
          method: 'jobComplete',
          is_async: true
        }
      ],
      title: 'Async Sequence Diagram'
    };

    render(<SequenceDiagram data={asyncData} />);
    
    expect(screen.getByText('Async Sequence Diagram')).toBeInTheDocument();
    expect(document.querySelector('.sequence-diagram-paper')).toBeInTheDocument();
    
    // Additional assertions would be specific to the JointJS rendering
    // which is mocked in this test environment
  });

  it('renders a diagram with conditional messages', () => {
    const conditionalData: SequenceDiagramData = {
      participants: ['User', 'AuthService', 'Database'],
      messages: [
        {
          from: 'User',
          to: 'AuthService',
          method: 'login',
          args: ['username', 'password']
        },
        {
          from: 'AuthService',
          to: 'Database',
          method: 'checkCredentials',
          args: ['username', 'password']
        },
        {
          from: 'Database',
          to: 'AuthService',
          method: 'result',
          is_return: true
        },
        {
          from: 'AuthService',
          to: 'User',
          method: 'success',
          is_conditional: true,
          condition: 'valid credentials'
        },
        {
          from: 'AuthService',
          to: 'User',
          method: 'failure',
          is_conditional: true,
          condition: 'invalid credentials'
        }
      ],
      title: 'Conditional Sequence Diagram'
    };

    render(<SequenceDiagram data={conditionalData} />);
    
    expect(screen.getByText('Conditional Sequence Diagram')).toBeInTheDocument();
    expect(document.querySelector('.sequence-diagram-paper')).toBeInTheDocument();
  });

  it('renders a complex diagram with multiple interactions', () => {
    const complexData: SequenceDiagramData = {
      participants: ['User', 'Frontend', 'API', 'AuthService', 'Database', 'CacheService'],
      messages: [
        {
          from: 'User',
          to: 'Frontend',
          method: 'submitForm',
          args: ['data']
        },
        {
          from: 'Frontend',
          to: 'API',
          method: 'postData',
          args: ['data', 'token']
        },
        {
          from: 'API',
          to: 'AuthService',
          method: 'validateToken',
          args: ['token']
        },
        {
          from: 'AuthService',
          to: 'CacheService',
          method: 'getToken',
          args: ['token']
        },
        {
          from: 'CacheService',
          to: 'AuthService',
          method: 'tokenData',
          is_return: true
        },
        {
          from: 'AuthService',
          to: 'API',
          method: 'tokenValid',
          is_return: true,
          is_conditional: true,
          condition: 'valid token'
        },
        {
          from: 'API',
          to: 'Database',
          method: 'saveData',
          args: ['data'],
          is_conditional: true,
          condition: 'valid token'
        },
        {
          from: 'Database',
          to: 'API',
          method: 'saveResult',
          is_return: true
        },
        {
          from: 'API',
          to: 'Frontend',
          method: 'response',
          is_return: true
        },
        {
          from: 'Frontend',
          to: 'User',
          method: 'showConfirmation',
          is_return: true
        }
      ],
      title: 'Complex Sequence Diagram'
    };

    render(<SequenceDiagram data={complexData} />);
    
    expect(screen.getByText('Complex Sequence Diagram')).toBeInTheDocument();
    expect(document.querySelector('.sequence-diagram-paper')).toBeInTheDocument();
  });

  it('handles custom dimensions', () => {
    const customWidth = 1200;
    const customHeight = 800;
    
    render(<SequenceDiagram data={sampleData} width={customWidth} height={customHeight} />);
    
    const container = document.querySelector('.sequence-diagram-container');
    expect(container).toHaveStyle(`width: ${customWidth}px`);
    expect(container).toHaveStyle(`height: ${customHeight}px`);
  });
}); 