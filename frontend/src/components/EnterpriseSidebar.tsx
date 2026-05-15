/**
 * 🔷 ENTERPRISE SIDEBAR - GLOBAL NAVIGATION HUB
 * Multi-layer operating system navigation with 12 modules
 */

import React, { useState } from 'react'
import { 
  ChevronLeft, 
  ChevronRight,
  LayoutDashboard, 
  ShoppingCart, 
  TrendingUp, 
  Truck, 
  Brain, 
  Newspaper, 
  Video, 
  FileText, 
  User, 
  Settings, 
  Code, 
  HelpCircle 
} from 'lucide-react'

interface NavigationModule {
  id: string
  label: string
  icon: React.ElementType
  category: string
}

interface EnterpriseSidebarProps {
  activeModule: string
  setActiveModule: (id: string) => void
  modules: NavigationModule[]
  collapsed: boolean
  setCollapsed: (collapsed: boolean) => void
}

export const EnterpriseSidebar: React.FC<EnterpriseSidebarProps> = ({
  activeModule,
  setActiveModule,
  modules,
  collapsed,
  setCollapsed
}) => {
  const [hoveredModule, setHoveredModule] = useState<string | null>(null)

  // Group modules by category
  const groupedModules = modules.reduce((acc, module) => {
    if (!acc[module.category]) {
      acc[module.category] = []
    }
    acc[module.category].push(module)
    return acc
  }, {} as Record<string, NavigationModule[]>)

  return (
    <aside 
      className={`
        bg-[var(--bg-secondary)] 
        border-r border-[var(--border-subtle)]
        flex flex-col
        transition-all duration-300 ease-in-out
        ${collapsed ? 'w-16' : 'w-64'}
      `}
    >
      {/* LOGO & COLLAPSE BUTTON */}
      <div className="flex items-center justify-between p-4 border-b border-[var(--border-subtle)]">
        {!collapsed && (
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-br from-[var(--accent-cyan)] to-[var(--accent-gold)] rounded-lg flex items-center justify-center">
              <LayoutDashboard className="w-4 h-4 text-white" />
            </div>
            <div>
              <h1 className="text-sm font-bold text-[var(--text-primary)] font-display">WORLD-MINE</h1>
              <p className="text-[10px] text-[var(--text-tertiary)]">Enterprise Platform</p>
            </div>
          </div>
        )}
        {collapsed && (
          <div className="w-8 h-8 bg-gradient-to-br from-[var(--accent-cyan)] to-[var(--accent-gold)] rounded-lg flex items-center justify-center mx-auto">
            <LayoutDashboard className="w-4 h-4 text-white" />
          </div>
        )}
        <button 
          onClick={() => setCollapsed(!collapsed)}
          className="p-1.5 rounded-md hover:bg-[var(--bg-tertiary)] text-[var(--text-tertiary)] hover:text-[var(--text-secondary)] transition-colors"
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* NAVIGATION MODULES */}
      <nav className="flex-1 overflow-y-auto p-2">
        {Object.entries(groupedModules).map(([category, categoryModules]) => (
          <div key={category} className="mb-4">
            {!collapsed && (
              <div className="px-3 py-2">
                <p className="text-[10px] font-semibold text-[var(--text-muted)] uppercase tracking-widest">
                  {category}
                </p>
              </div>
            )}
            <div className="space-y-1">
              {categoryModules.map((module) => {
                const Icon = module.icon
                const isActive = activeModule === module.id
                const isHovered = hoveredModule === module.id

                return (
                  <button
                    key={module.id}
                    onClick={() => setActiveModule(module.id)}
                    onMouseEnter={() => setHoveredModule(module.id)}
                    onMouseLeave={() => setHoveredModule(null)}
                    className={`
                      w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg
                      transition-all duration-200
                      ${isActive 
                        ? 'bg-gradient-to-r from-[var(--accent-cyan-soft)] to-transparent border-l-2 border-[var(--accent-cyan)] text-[var(--accent-cyan)]'
                        : 'text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)] hover:text-[var(--text-primary)]'
                      }
                      ${isHovered && !isActive ? 'pl-4' : ''}
                    `}
                  >
                    <Icon className={`w-4.5 h-4.5 ${isActive ? 'text-[var(--accent-cyan)]' : ''}`} />
                    {!collapsed && (
                      <span className="text-sm font-medium">{module.label}</span>
                    )}
                  </button>
                )
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* SIDEBAR FOOTER */}
      <div className="p-3 border-t border-[var(--border-subtle)]">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[var(--trust-success)] to-[var(--accent-cyan)] flex items-center justify-center">
            <User className="w-4 h-4 text-white" />
          </div>
          {!collapsed && (
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-[var(--text-primary)] truncate">Enterprise User</p>
              <p className="text-xs text-[var(--text-tertiary)] truncate">Premium Plan</p>
            </div>
          )}
        </div>
      </div>
    </aside>
  )
}

export default EnterpriseSidebar
