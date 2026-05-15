/**
 * ⌘K GLOBAL COMMAND PALETTE (V3.0)
 * Enterprise quick actions, AI search, navigation shortcuts
 */

import React, { useState, useEffect, useRef } from 'react'
import { 
  Search, 
  Command, 
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
  Globe,
  Zap,
  HelpCircle,
  ChevronRight
} from 'lucide-react'

interface CommandPaletteProps {
  isOpen: boolean
  onClose: () => void
  onNavigate: (moduleId: string) => void
}

const COMMANDS = [
  { id: 'dashboard', label: 'Go to Dashboard', icon: LayoutDashboard, category: 'Navigation', shortcut: 'G D' },
  { id: 'marketplace', label: 'Go to Marketplace', icon: ShoppingCart, category: 'Navigation', shortcut: 'G M' },
  { id: 'trading', label: 'Go to Trading', icon: TrendingUp, category: 'Navigation', shortcut: 'G T' },
  { id: 'logistics', label: 'Go to Logistics', icon: Truck, category: 'Navigation', shortcut: 'G L' },
  { id: 'ai-intelligence', label: 'Go to AI Center', icon: Brain, category: 'Navigation', shortcut: 'G A' },
  { id: 'news', label: 'Go to News', icon: Newspaper, category: 'Navigation', shortcut: 'G N' },
  { id: 'communication', label: 'Go to Communication', icon: Video, category: 'Navigation', shortcut: 'G C' },
  { id: 'contracts', label: 'Go to Contracts', icon: FileText, category: 'Navigation', shortcut: 'G K' },
  { id: 'user', label: 'Go to Profile', icon: User, category: 'Navigation', shortcut: 'G P' },
  { id: 'settings', label: 'Go to Settings', icon: Settings, category: 'Navigation', shortcut: 'G S' },
  
  { id: 'search-listings', label: 'Search Listings', icon: Search, category: 'Search', shortcut: '' },
  { id: 'search-contracts', label: 'Search Contracts', icon: FileText, category: 'Search', shortcut: '' },
  { id: 'search-users', label: 'Search Users', icon: User, category: 'Search', shortcut: '' },
  
  { id: 'new-listing', label: 'Create New Listing', icon: ShoppingCart, category: 'Actions', shortcut: 'N L' },
  { id: 'new-trade', label: 'New Trade', icon: TrendingUp, category: 'Actions', shortcut: 'N T' },
  { id: 'toggle-ai', label: 'Toggle AI Assistant', icon: Brain, category: 'Actions', shortcut: '' },
  
  { id: 'help-docs', label: 'View Documentation', icon: HelpCircle, category: 'Help', shortcut: 'H D' },
  { id: 'help-shortcuts', label: 'View Keyboard Shortcuts', icon: Command, category: 'Help', shortcut: '?' },
]

export const GlobalCommandPalette: React.FC<CommandPaletteProps> = ({
  isOpen,
  onClose,
  onNavigate
}) => {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)

  // Filter commands based on search
  const filteredCommands = COMMANDS.filter(cmd => 
    cmd.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
    cmd.category.toLowerCase().includes(searchQuery.toLowerCase())
  )

  // Reset state when opened
  useEffect(() => {
    if (isOpen) {
      setSearchQuery('')
      setSelectedIndex(0)
      setTimeout(() => inputRef.current?.focus(), 50)
    }
  }, [isOpen])

  // Keyboard navigation
  useEffect(() => {
    if (!isOpen) return

    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case 'Escape':
          onClose()
          break
        case 'ArrowDown':
          e.preventDefault()
          setSelectedIndex(i => 
            Math.min(i + 1, filteredCommands.length - 1)
          )
          break
        case 'ArrowUp':
          e.preventDefault()
          setSelectedIndex(i => Math.max(i - 1, 0))
          break
        case 'Enter':
          e.preventDefault()
          if (filteredCommands[selectedIndex]) {
            executeCommand(filteredCommands[selectedIndex])
          }
          break
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, filteredCommands, selectedIndex, onClose, onNavigate])

  const executeCommand = (command: any) => {
    // Navigation commands
    if (command.category === 'Navigation') {
      onNavigate(command.id)
    }
    
    // Clear and close
    setSearchQuery('')
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh]">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Command Palette */}
      <div className="relative w-full max-w-2xl mx-4 z-50">
        <div className="glass-elevated rounded-2xl border border-[var(--border-medium)] shadow-2xl overflow-hidden">
          {/* Search Input */}
          <div className="flex items-center px-4 border-b border-[var(--border-subtle)]">
            <Search className="w-5 h-5 text-[var(--text-tertiary)] flex-shrink-0" />
            <input
              ref={inputRef}
              type="text"
              placeholder="Type a command or search..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1 bg-transparent border-0 px-3 py-4 text-sm text-[var(--text-primary)] placeholder-[var(--text-tertiary)] focus:outline-none focus:ring-0"
            />
            <div className="flex items-center space-x-1">
              <span className="text-[10px] font-mono text-[var(--text-tertiary)] bg-[var(--bg-tertiary)] px-2 py-1 rounded border border-[var(--border-subtle)]">
                ESC
              </span>
            </div>
          </div>

          {/* Commands List */}
          <div className="max-h-[400px] overflow-y-auto p-2">
            {filteredCommands.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <Search className="w-10 h-10 text-[var(--text-tertiary)] mb-3" />
                <p className="text-sm text-[var(--text-secondary)]">No commands found</p>
                <p className="text-xs text-[var(--text-tertiary)] mt-1">Try a different search term</p>
              </div>
            ) : (
              <div className="space-y-0.5">
                {/* Group by category */}
                {Array.from(new Set(filteredCommands.map(c => c.category))).map(category => {
                  const categoryCommands = filteredCommands.filter(c => c.category === category)
                  
                  return (
                    <div key={category}>
                      <div className="px-3 py-2">
                        <p className="text-[10px] font-semibold text-[var(--text-muted)] uppercase tracking-widest">
                          {category}
                        </p>
                      </div>
                      
                      {categoryCommands.map((command, index) => {
                        const Icon = command.icon
                        const isSelected = filteredCommands.indexOf(command) === selectedIndex
                        
                        return (
                          <button
                            key={command.id}
                            onClick={() => executeCommand(command)}
                            className={`
                              w-full flex items-center justify-between px-3 py-2.5 rounded-lg
                              transition-all duration-150
                              ${isSelected 
                                ? 'bg-[var(--accent-cyan-soft)] border border-[var(--accent-cyan)]/30 text-[var(--accent-cyan)]' 
                                : 'text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)]'
                              }
                            `}
                          >
                            <div className="flex items-center space-x-3">
                              <Icon className={`w-4.5 h-4.5 ${isSelected ? 'text-[var(--accent-cyan)]' : 'text-[var(--text-tertiary)]'}`} />
                              <span className="text-sm font-medium">{command.label}</span>
                            </div>
                            
                            <div className="flex items-center space-x-2">
                              {command.shortcut && (
                                <div className="flex items-center space-x-1">
                                  {command.shortcut.split(' ').map((key, i) => (
                                    <span 
                                      key={i}
                                      className="text-[10px] font-mono text-[var(--text-tertiary)] bg-[var(--bg-tertiary)] px-1.5 py-0.5 rounded border border-[var(--border-subtle)]"
                                    >
                                      {key}
                                    </span>
                                  ))}
                                </div>
                              )}
                              <ChevronRight className={`w-3.5 h-3.5 ${isSelected ? 'text-[var(--accent-cyan)]' : 'text-[var(--text-tertiary)]'}`} />
                            </div>
                          </button>
                        )
                      })}
                    </div>
                  )
                })}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="px-4 py-3 border-t border-[var(--border-subtle)] flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-1.5">
                <span className="text-[10px] text-[var(--text-tertiary)]">Navigate</span>
                <div className="flex space-x-0.5">
                  <span className="text-[10px] font-mono text-[var(--text-tertiary)] bg-[var(--bg-tertiary)] px-1.5 py-0.5 rounded border border-[var(--border-subtle)]">↑</span>
                  <span className="text-[10px] font-mono text-[var(--text-tertiary)] bg-[var(--bg-tertiary)] px-1.5 py-0.5 rounded border border-[var(--border-subtle)]">↓</span>
                </div>
              </div>
              <div className="flex items-center space-x-1.5">
                <span className="text-[10px] text-[var(--text-tertiary)]">Select</span>
                <span className="text-[10px] font-mono text-[var(--text-tertiary)] bg-[var(--bg-tertiary)] px-1.5 py-0.5 rounded border border-[var(--border-subtle)]">Enter</span>
              </div>
            </div>
            
            <div className="flex items-center space-x-1.5">
              <Zap className="w-3.5 h-3.5 text-[var(--accent-gold)]" />
              <span className="text-[10px] text-[var(--text-tertiary)]">{filteredCommands.length} commands</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default GlobalCommandPalette
