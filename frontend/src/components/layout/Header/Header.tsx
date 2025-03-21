import React from 'react';
import Link from 'next/link';

interface HeaderProps {
  username?: string;
  onLogout?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ username, onLogout }) => {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center">
        <Link href="/" className="text-2xl font-bold text-blue-800">
          RepoMind
        </Link>
        <nav className="ml-10 hidden md:flex space-x-6">
          <Link href="/" className="text-gray-700 hover:text-blue-800">
            Home
          </Link>
          <Link href="/repositories" className="text-gray-700 hover:text-blue-800">
            Repositories
          </Link>
          <Link href="/docs" className="text-gray-700 hover:text-blue-800">
            Documentation
          </Link>
        </nav>
      </div>
      
      <div className="flex items-center">
        {username ? (
          <div className="flex items-center">
            <span className="text-gray-700 mr-4">Welcome, {username}</span>
            <button
              onClick={onLogout}
              className="bg-transparent hover:bg-gray-200 text-gray-700 px-3 py-1 rounded"
            >
              Logout
            </button>
          </div>
        ) : (
          <Link href="/api/auth/github/login" className="bg-gray-800 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded flex items-center">
            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 0C4.477 0 0 4.477 0 10c0 4.42 2.865 8.167 6.839 9.49.5.09.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.564 9.564 0 0110 4.844c.85.004 1.705.115 2.504.337 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.841-2.337 4.687-4.565 4.934.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C17.14 18.163 20 14.418 20 10 20 4.477 15.523 0 10 0z" clipRule="evenodd" />
            </svg>
            Login with GitHub
          </Link>
        )}
      </div>
    </div>
  );
}; 