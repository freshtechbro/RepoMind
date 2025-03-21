# RepoMind

RepoMind is a tool for analyzing GitHub repositories and visualizing their architecture through various diagram types. It helps developers quickly understand codebases by providing visual representations of code structure and interactions.

## Features

- **GitHub Repository Analysis**: Analyze repositories via URL with support for private repos
- **Sequence Diagrams**: Visualize function calls and object interactions
- **File/Module Structure Visualization**: Understand codebase organization at a glance
- **Class Diagrams**: See relationships between classes including inheritance and composition
- **Flowcharts**: Visualize control flow within functions
- **Interactive UI**: Zoom, pan, and navigate between different diagram types
- **Codebase Search**: Find specific elements within the codebase
- **Security Scanning**: Identify potential security issues such as hardcoded credentials
- **Language Support**: Currently supports Python and JavaScript/TypeScript

## Tech Stack

### Backend
- FastAPI
- SQLAlchemy
- PyGithub
- Various code analysis libraries

### Frontend
- Next.js
- React
- TypeScript
- D3.js for visualizations
- Material UI components

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git
- PostgreSQL (optional, for production)

### Backend Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/repomind.git
   cd repomind
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with the following content:
   ```
   DATABASE_URL=sqlite:///./repomind.db  # For development
   GITHUB_CLIENT_ID=your_github_client_id
   GITHUB_CLIENT_SECRET=your_github_client_secret
   SECRET_KEY=your_secret_key_for_jwt
   ```

5. Run the backend:
   ```
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Create a `.env.local` file with:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. Run the development server:
   ```
   npm run dev
   ```

5. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Development

### Project Structure

```
repomind/
├── app/                # Backend FastAPI application
│   ├── api/            # API endpoints
│   ├── core/           # Core business logic
│   ├── models/         # Database models
│   ├── services/       # Service implementations
│   └── utils/          # Utility functions
├── frontend/           # Next.js frontend
│   ├── components/     # React components
│   ├── pages/          # Next.js pages
│   ├── public/         # Static files
│   ├── services/       # API client services
│   ├── styles/         # CSS styles
│   └── utils/          # Utility functions
├── tests/              # Test directory
│   ├── api/            # API tests
│   ├── services/       # Service tests
│   └── utils/          # Utility tests
├── docs/               # Documentation
└── scripts/            # Utility scripts
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 