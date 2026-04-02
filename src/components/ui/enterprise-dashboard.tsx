import React from 'react'
import { cn } from '../../utils/cn'

interface EnterpriseDashboardProps {
  children: React.ReactNode
  className?: string
}

const EnterpriseDashboard: React.FC<EnterpriseDashboardProps> = ({
  children,
  className
}) => {
  return (
    <div className={cn('min-h-screen bg-gray-50', className)}>
      <div className="flex h-full">
        {children}
      </div>
    </div>
  )
}

interface DashboardHeaderProps {
  children: React.ReactNode
  className?: string
}

const DashboardHeader: React.FC<DashboardHeaderProps> = ({
  children,
  className
}) => {
  return (
    <header className={cn(
      'bg-white border-b border-gray-200 shadow-sm',
      className
    )}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {children}
        </div>
      </div>
    </header>
  )
}

interface DashboardSidebarProps {
  children: React.ReactNode
  className?: string
  width?: 'sm' | 'md' | 'lg'
}

const DashboardSidebar: React.FC<DashboardSidebarProps> = ({
  children,
  className,
  width = 'md'
}) => {
  const widthClasses = {
    sm: 'w-48',
    md: 'w-64',
    lg: 'w-80'
  }
  
  return (
    <aside className={cn(
      'bg-white border-r border-gray-200 h-full overflow-y-auto',
      widthClasses[width],
      className
    )}>
      {children}
    </aside>
  )
}

interface DashboardMainProps {
  children: React.ReactNode
  className?: string
}

const DashboardMain: React.FC<DashboardMainProps> = ({
  children,
  className
}) => {
  return (
    <main className={cn(
      'flex-1 overflow-y-auto bg-gray-50',
      className
    )}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </div>
    </main>
  )
}

interface DashboardSidebarNavProps {
  children: React.ReactNode
  className?: string
}

const DashboardSidebarNav: React.FC<DashboardSidebarNavProps> = ({
  children,
  className
}) => {
  return (
    <nav className={cn('space-y-1 p-4', className)}>
      {children}
    </nav>
  )
}

interface DashboardNavItemProps {
  children: React.ReactNode
  active?: boolean
  icon?: React.ReactNode
  onClick?: () => void
  className?: string
}

const DashboardNavItem: React.FC<DashboardNavItemProps> = ({
  children,
  active = false,
  icon,
  onClick,
  className
}) => {
  return (
    <button
      onClick={onClick}
      className={cn(
        'w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors duration-150',
        active
          ? 'bg-primary-blue text-white'
          : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900',
        className
      )}
    >
      {icon && (
        <span className="mr-3 h-5 w-5 flex items-center justify-center">
          {icon}
        </span>
      )}
      {children}
    </button>
  )
}

export {
  EnterpriseDashboard,
  DashboardHeader,
  DashboardSidebar,
  DashboardMain,
  DashboardSidebarNav,
  DashboardNavItem
}
