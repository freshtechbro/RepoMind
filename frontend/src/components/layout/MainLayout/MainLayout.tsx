import React from 'react';

interface MainLayoutProps {
  children: React.ReactNode;
  sidebar?: React.ReactNode;
  header?: React.ReactNode;
}

export const MainLayout: React.FC<MainLayoutProps> = ({
  children,
  sidebar,
  header,
}) => {
  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      {header && (
        <header className="bg-white shadow-sm z-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            {header}
          </div>
        </header>
      )}
      
      <div className="flex flex-1 overflow-hidden">
        {sidebar && (
          <aside className="w-64 border-r border-gray-200 bg-white hidden md:block overflow-y-auto">
            {sidebar}
          </aside>
        )}
        
        <main className="flex-1 overflow-auto p-4 sm:p-6 lg:p-8">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}; 