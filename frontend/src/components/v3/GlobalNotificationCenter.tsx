/**
 * 🔔 GLOBAL NOTIFICATION CENTER (V3.0)
 * Unified alerts, logistics updates, AI insights, negotiations, market warnings
 */

import React, { useState } from 'react'
import { 
  Bell, 
  AlertTriangle, 
  TrendingUp, 
  Truck, 
  Brain, 
  MessageSquare,
  Check,
  X,
  Clock,
  Zap,
  ShieldCheck,
  Settings
} from 'lucide-react'

interface Notification {
  id: string
  type: 'alert' | 'market' | 'logistics' | 'ai' | 'negotiation' | 'security'
  title: string
  message: string
  timestamp: string
  read: boolean
  priority: 'low' | 'medium' | 'high' | 'urgent'
}

const MOCK_NOTIFICATIONS: Notification[] = [
  {
    id: '1',
    type: 'alert',
    title: 'Supply Chain Risk Detected',
    message: 'Copper shipment from Zambia may be delayed due to port congestion',
    timestamp: '2 min ago',
    read: false,
    priority: 'high'
  },
  {
    id: '2',
    type: 'market',
    title: 'Gold Price Alert',
    message: 'Gold price increased by 1.2% - consider reviewing your positions',
    timestamp: '15 min ago',
    read: false,
    priority: 'medium'
  },
  {
    id: '3',
    type: 'logistics',
    title: 'Shipment Delivered',
    message: 'Your lithium shipment has arrived in Singapore warehouse',
    timestamp: '1 hour ago',
    read: true,
    priority: 'low'
  },
  {
    id: '4',
    type: 'ai',
    title: 'New AI Insight',
    message: 'Market Intelligence Agent detected undervalued copper listing',
    timestamp: '2 hours ago',
    read: true,
    priority: 'medium'
  },
  {
    id: '5',
    type: 'negotiation',
    title: 'New Negotiation Request',
    message: 'GoldMaster Trading wants to negotiate your offer',
    timestamp: '3 hours ago',
    read: true,
    priority: 'medium'
  },
  {
    id: '6',
    type: 'security',
    title: 'Login from New Device',
    message: 'New login detected from Singapore - verify if this was you',
    timestamp: '5 hours ago',
    read: true,
    priority: 'urgent'
  }
]

const NOTIFICATION_ICONS = {
  alert: AlertTriangle,
  market: TrendingUp,
  logistics: Truck,
  ai: Brain,
  negotiation: MessageSquare,
  security: ShieldCheck
}

const NOTIFICATION_COLORS = {
  low: 'text-[var(--text-tertiary)]',
  medium: 'text-[var(--accent-cyan)]',
  high: 'text-[var(--trust-warning)]',
  urgent: 'text-[var(--trust-danger)]'
}

const NOTIFICATION_BG_COLORS = {
  low: 'bg-[var(--bg-tertiary)]',
  medium: 'bg-[var(--accent-cyan-soft)]',
  high: 'bg-[var(--trust-warning-soft)]',
  urgent: 'bg-[var(--trust-danger-soft)]'
}

interface GlobalNotificationCenterProps {
  isOpen: boolean
  onClose: () => void
}

export const GlobalNotificationCenter: React.FC<GlobalNotificationCenterProps> = ({
  isOpen,
  onClose
}) => {
  const [notifications, setNotifications] = useState<Notification[]>(MOCK_NOTIFICATIONS)
  const [filter, setFilter] = useState<'all' | 'unread' | 'alert' | 'market' | 'logistics' | 'ai'>('all')

  const unreadCount = notifications.filter(n => !n.read).length

  const filteredNotifications = notifications.filter(n => {
    if (filter === 'all') return true
    if (filter === 'unread') return !n.read
    return n.type === filter
  })

  const markAllAsRead = () => {
    setNotifications(notifications.map(n => ({ ...n, read: true })))
  }

  const markAsRead = (id: string) => {
    setNotifications(notifications.map(n => 
      n.id === id ? { ...n, read: true } : n
    ))
  }

  const deleteNotification = (id: string) => {
    setNotifications(notifications.filter(n => n.id !== id))
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-end pt-16 pr-4">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/40"
        onClick={onClose}
      />

      {/* Notification Panel */}
      <div className="relative w-full max-w-md z-50">
        <div className="glass-elevated rounded-2xl border border-[var(--border-medium)] shadow-2xl overflow-hidden max-h-[80vh] flex flex-col">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-[var(--border-subtle)]">
            <div className="flex items-center space-x-3">
              <div className="relative">
                <Bell className="w-5 h-5 text-[var(--accent-cyan)]" />
                {unreadCount > 0 && (
                  <div className="absolute -top-1 -right-1 w-4 h-4 bg-[var(--trust-danger)] rounded-full flex items-center justify-center border border-[var(--bg-secondary)]">
                    <span className="text-[9px] font-bold text-white">{unreadCount}</span>
                  </div>
                )}
              </div>
              <div>
                <h2 className="text-sm font-bold text-[var(--text-primary)]">Notifications</h2>
                <p className="text-[10px] text-[var(--text-tertiary)]">{unreadCount} unread</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              {unreadCount > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="text-xs text-[var(--accent-cyan)] hover:text-[var(--accent-cyan)]/80 font-medium"
                >
                  Mark all read
                </button>
              )}
              <button
                onClick={onClose}
                className="p-1.5 rounded hover:bg-[var(--bg-tertiary)] text-[var(--text-tertiary)]"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Filter Tabs */}
          <div className="flex items-center space-x-1 px-4 py-2 border-b border-[var(--border-subtle)] overflow-x-auto">
            {[
              { id: 'all', label: 'All' },
              { id: 'unread', label: 'Unread' },
              { id: 'alert', label: 'Alerts' },
              { id: 'market', label: 'Market' },
              { id: 'logistics', label: 'Logistics' },
              { id: 'ai', label: 'AI' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setFilter(tab.id as any)}
                className={`
                  px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap
                  transition-all
                  ${filter === tab.id 
                    ? 'bg-[var(--accent-cyan-soft)] text-[var(--accent-cyan)] border border-[var(--accent-cyan)]/30' 
                    : 'text-[var(--text-tertiary)] hover:text-[var(--text-secondary)]'
                  }
                `}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Notifications List */}
          <div className="flex-1 overflow-y-auto">
            {filteredNotifications.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <Bell className="w-10 h-10 text-[var(--text-tertiary)] mb-3" />
                <p className="text-sm text-[var(--text-secondary)]">No notifications</p>
                <p className="text-xs text-[var(--text-tertiary)] mt-1">You're all caught up!</p>
              </div>
            ) : (
              <div className="divide-y divide-[var(--border-subtle)]">
                {filteredNotifications.map(notification => {
                  const Icon = NOTIFICATION_ICONS[notification.type as keyof typeof NOTIFICATION_ICONS]
                  
                  return (
                    <div
                      key={notification.id}
                      onClick={() => markAsRead(notification.id)}
                      className={`
                        p-4 cursor-pointer transition-all
                        ${notification.read ? 'opacity-75' : 'opacity-100'}
                        ${NOTIFICATION_BG_COLORS[notification.priority]}
                        hover:bg-[var(--bg-tertiary)]
                      `}
                    >
                      <div className="flex items-start space-x-3">
                        <div className={`
                          w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0
                          ${notification.priority === 'urgent' ? 'bg-[var(--trust-danger-soft)]' : ''}
                          ${notification.priority === 'high' ? 'bg-[var(--trust-warning-soft)]' : ''}
                          ${notification.priority === 'medium' ? 'bg-[var(--accent-cyan-soft)]' : ''}
                          ${notification.priority === 'low' ? 'bg-[var(--bg-tertiary)]' : ''}
                        `}>
                          <Icon className={`w-4.5 h-4.5 ${NOTIFICATION_COLORS[notification.priority]}`} />
                        </div>
                        
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-2">
                                <h4 className={`text-sm font-semibold ${notification.read ? 'text-[var(--text-secondary)]' : 'text-[var(--text-primary)]'}`}>
                                  {notification.title}
                                </h4>
                                {!notification.read && (
                                  <div className="w-2 h-2 bg-[var(--accent-cyan)] rounded-full flex-shrink-0"></div>
                                )}
                              </div>
                              <p className="text-xs text-[var(--text-tertiary)] mt-1 line-clamp-2">
                                {notification.message}
                              </p>
                              <div className="flex items-center space-x-2 mt-2">
                                <Clock className="w-3 h-3 text-[var(--text-tertiary)]" />
                                <span className="text-[10px] text-[var(--text-tertiary)] font-mono">
                                  {notification.timestamp}
                                </span>
                              </div>
                            </div>
                            
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                deleteNotification(notification.id)
                              }}
                              className="p-1 rounded hover:bg-[var(--bg-secondary)] text-[var(--text-tertiary)] hover:text-[var(--trust-danger)] ml-2"
                            >
                              <X className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="p-3 border-t border-[var(--border-subtle)] flex items-center justify-between">
            <button className="flex items-center space-x-2 px-3 py-1.5 text-xs text-[var(--text-tertiary)] hover:text-[var(--text-secondary)]">
              <Settings className="w-3.5 h-3.5" />
              <span>Notification Settings</span>
            </button>
            <div className="text-[10px] text-[var(--text-tertiary)]">
              {notifications.length} total
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default GlobalNotificationCenter
