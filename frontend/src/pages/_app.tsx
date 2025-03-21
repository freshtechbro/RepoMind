import React, { useState } from 'react';
import { AppProps } from 'next/app';
import { MainLayout } from '../components/layout/MainLayout';
import { Header } from '../components/layout/Header';
import { Sidebar } from '../components/layout/Sidebar';
import '../styles/globals.css';

function MyApp({ Component, pageProps, router }: AppProps) {
  const [user, setUser] = useState<{ username: string } | null>(null);
  
  const handleLogout = () => {
    setUser(null);
    // Additional logout logic here
  };
  
  const sidebarNavItems = [
    { id: 'home', label: 'Home', href: '/' },
    { id: 'repositories', label: 'Repositories', href: '/repositories' },
    { id: 'sequence-diagram', label: 'Sequence Diagram', href: '/sequence-diagram' },
    { id: 'repository-structure', label: 'Repository Structure', href: '/repository-structure' },
  ];
  
  // Determine active item based on current route
  const activeItemId = sidebarNavItems.find(
    item => item.href === router.pathname
  )?.id || 'home';
  
  return (
    <MainLayout
      header={<Header username={user?.username} onLogout={handleLogout} />}
      sidebar={
        <Sidebar
          navItems={sidebarNavItems}
          title="RepoMind"
          activeItemId={activeItemId}
        />
      }
    >
      <Component {...pageProps} />
    </MainLayout>
  );
}

export default MyApp; 