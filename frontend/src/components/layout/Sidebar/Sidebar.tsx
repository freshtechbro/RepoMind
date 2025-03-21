import React from 'react';
import Link from 'next/link';

interface NavItem {
  id: string;
  label: string;
  href: string;
  icon?: React.ReactNode;
}

interface SidebarProps {
  navItems: NavItem[];
  activeItemId?: string;
  title?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  navItems,
  activeItemId,
  title,
}) => {
  return (
    <div className="h-full flex flex-col py-4">
      {title && (
        <div className="px-4 mb-6">
          <h2 className="text-lg font-medium text-gray-900">{title}</h2>
        </div>
      )}
      
      <nav className="flex-1 space-y-1 px-2">
        {navItems.map((item) => (
          <Link
            key={item.id}
            href={item.href}
            className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
              activeItemId === item.id
                ? 'bg-blue-100 text-blue-800'
                : 'text-gray-700 hover:bg-gray-100'
            }`}
            data-testid={`nav-item-${item.id}`}
          >
            {item.icon && <div className="mr-3 flex-shrink-0 h-6 w-6">{item.icon}</div>}
            {item.label}
          </Link>
        ))}
      </nav>
    </div>
  );
}; 