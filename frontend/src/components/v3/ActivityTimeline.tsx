/**
 * 🕐 ACTIVITY TIMELINE (V3.0)
 * Global operational history: transactions, negotiations, AI decisions, logistics events
 */

import React, { useState } from 'react'
import { 
  Clock, 
  TrendingUp, 
  Zap, 
  MessageSquare, 
  Truck, 
  FileText,
  ShieldCheck,
  Brain,
  Filter,
  ChevronDown
} from 'lucide-react'

interface TimelineEvent {
  id: string
  type: 'transaction' | 'negotiation' | 'ai-decision' | 'logistics' | 'contract' | 'security'
  title: string
  description: string
  timestamp: string
  metadata: Record<string, any>
  icon: React.ElementType
  color: string
  bgColor: string
}

const MOCK_TIMELINE: TimelineEvent[] = [
  {
    id: '1',
    type: 'transaction',
    title: 'Transaction Completed',
    description: 'Copper purchase - 500 MT @ $8,400/MT',
    timestamp: '14 May 2026, 14:32:18',
    metadata: { amount: '$4,200,000', status: 'completed' },
    icon: TrendingUp,
    color: 'text-[var(--trust-success)]',
    bgColor: 'bg-[var(--trust-success-soft)]'
  },
  {
    id: '2',
    type: 'ai-decision',
    title: 'AI Recommendation Generated',
    description: 'Market Intelligence Agent suggested undervalued lithium listing',
    timestamp: '14 May 2026, 12:15:44',
    metadata: { confidence: 0.87, agent: 'market_intelligence' },
    icon: Brain,
    color: 'text-[var(--accent-purple)]',
    bgColor: 'bg-[var(--accent-purple-soft)]'
  },
  {
    id: '3',
    type: 'negotiation',
    title: 'Negotiation Started',
    description: 'Video call with GoldMaster Trading Ltd initiated',
    timestamp: '14 May 2026, 10:08:22',
    metadata: { participants: 3, duration: '24min' },
    icon: MessageSquare,
    color: 'text-[var(--accent-cyan)]',
    bgColor: 'bg-[var(--accent-cyan-soft)]'
  },
  {
    id: '4',
    type: 'logistics',
    title: 'Shipment in Transit',
    description: 'Lithium shipment departed from Chile warehouse',
    timestamp: '13 May 2026, 22:47:11',
    metadata: { carrier: 'Maersk', eta: '28 May 2026' },
    icon: Truck,
    color: 'text-[var(--accent-gold)]',
    bgColor: 'bg-[var(--accent-gold-soft)]'
  },
  {
    id: '5',
    type: 'contract',
    title: 'Contract Signed',
    description: 'Copper supply agreement signed by both parties',
    timestamp: '13 May 2026, 16:22:05',
    metadata: { parties: 2, escrow: 'locked' },
    icon: FileText,
    color: 'text-[var(--accent-cyan)]',
    bgColor: 'bg-[var(--accent-cyan-soft)]'
  },
  {
    id: '6',
    type: 'security',
    title: 'KYC Verification Approved',
    description: 'New seller verification completed successfully',
    timestamp: '13 May 2026, 09:15:33',
    metadata: { entity: 'Zambia Copper Mines', level: 'Tier 1' },
    icon: ShieldCheck,
    color: 'text-[var(--trust-success)]',
    bgColor: 'bg-[var(--trust-success-soft)]'
  }
]

interface ActivityTimelineProps {
  className?: string
}

export const ActivityTimeline: React.FC<ActivityTimelineProps> = ({ className = '' }) => {
  const [filter, setFilter] = useState<'all' | 'transaction' | 'negotiation' | 'ai-decision' | 'logistics' | 'contract' | 'security'>('all')
  const [showFilters, setShowFilters] = useState(false)

  const filteredTimeline = filter === 'all' 
    ? MOCK_TIMELINE 
    : MOCK_TIMELINE.filter(event => event.type === filter)

  return (
    <div className={`glass rounded-xl border border-[var(--border-subtle)] p-5 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center space-x-3">
          <Clock className="w-5 h-5 text-[var(--accent-cyan)]" />
          <div>
            <h2 className="text-sm font-bold text-[var(--text-primary)]">Activity Timeline</h2>
            <p className="text-[10px] text-[var(--text-tertiary)]">Global operational history</p>
          </div>
        </div>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="flex items-center space-x-1.5 px-3 py-1.5 bg-[var(--bg-tertiary)] rounded-lg text-xs text-[var(--text-secondary)] hover:bg-[var(--bg-elevated)]"
        >
          <Filter className="w-3.5 h-3.5" />
          <span>Filter</span>
          <ChevronDown className="w-3 h-3" />
        </button>
      </div>

      {/* Filter Options */}
      {showFilters && (
        <div className="mb-4 p-3 bg-[var(--bg-tertiary)] rounded-lg border border-[var(--border-subtle)]">
          <p className="text-[10px] font-semibold text-[var(--text-muted)] uppercase tracking-widest mb-2">
            EVENT TYPE
          </p>
          <div className="flex flex-wrap gap-1.5">
            {[
              { id: 'all', label: 'All' },
              { id: 'transaction', label: 'Transactions' },
              { id: 'negotiation', label: 'Negotiations' },
              { id: 'ai-decision', label: 'AI Decisions' },
              { id: 'logistics', label: 'Logistics' },
              { id: 'contract', label: 'Contracts' },
              { id: 'security', label: 'Security' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setFilter(tab.id as any)}
                className={`
                  px-2.5 py-1 rounded-full text-[10px] font-medium
                  transition-all
                  ${filter === tab.id 
                    ? 'bg-[var(--accent-cyan-soft)] text-[var(--accent-cyan)] border border-[var(--accent-cyan)]/30' 
                    : 'text-[var(--text-tertiary)] hover:text-[var(--text-secondary)] bg-[var(--bg-secondary)]'
                  }
                `}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Timeline */}
      <div className="relative">
        {/* Vertical Line */}
        <div className="absolute left-5 top-2 bottom-2 w-px bg-gradient-to-b from-[var(--accent-cyan)] via-[var(--accent-purple)] to-[var(--accent-gold)] opacity-30"></div>

        {/* Timeline Events */}
        <div className="space-y-6">
          {filteredTimeline.map((event, index) => {
            const Icon = event.icon
            
            return (
              <div key={event.id} className="relative pl-12">
                {/* Event Dot */}
                <div className={`
                  absolute left-3.5 top-1.5 w-3 h-3 rounded-full border-2 border-[var(--bg-secondary)]
                  ${event.bgColor}
                  shadow-lg shadow-current/20
                `}>
                  <div className={`w-full h-full rounded-full ${event.color} animate-pulse-glow`}></div>
                </div>

                {/* Event Card */}
                <div className="glass p-4 rounded-lg border border-[var(--border-subtle)] hover:border-[var(--accent-cyan)]/30 transition-all">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1.5">
                        <div className={`
                          w-7 h-7 rounded-lg flex items-center justify-center
                          ${event.bgColor}
                        `}>
                          <Icon className={`w-3.5 h-3.5 ${event.color}`} />
                        </div>
                        <h3 className="text-sm font-semibold text-[var(--text-primary)]">
                          {event.title}
                        </h3>
                      </div>
                      <p className="text-xs text-[var(--text-secondary)] mb-2">
                        {event.description}
                      </p>
                      <div className="flex items-center justify-between">
                        <p className="text-[10px] font-mono text-[var(--text-tertiary)]">
                          {event.timestamp}
                        </p>
                        <div className="flex items-center space-x-2">
                          {Object.entries(event.metadata).map(([key, value]) => (
                            <span 
                              key={key} 
                              className="text-[10px] text-[var(--text-tertiary)] bg-[var(--bg-tertiary)] px-2 py-0.5 rounded-full"
                            >
                              {key}: {typeof value === 'string' ? value : JSON.stringify(value)}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        {/* Load More */}
        <div className="mt-6 pt-4 border-t border-[var(--border-subtle)]">
          <button className="w-full py-2.5 text-xs text-[var(--accent-cyan)] hover:text-[var(--accent-cyan)]/80 font-medium">
            Load More Activity
          </button>
        </div>
      </div>
    </div>
  )
}

export default ActivityTimeline
