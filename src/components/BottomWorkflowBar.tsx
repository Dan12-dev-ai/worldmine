import React from 'react'
import { 
  Search, 
  Eye, 
  Shield, 
  Coins,
  BrainCircuit,
  LayoutGrid
} from 'lucide-react'

const BottomWorkflowBar: React.FC = () => {
  const steps = [
    { icon: Search, label: 'Browse Categories & Mines' },
    { icon: LayoutGrid, label: 'AI-Powered Matching' },
    { icon: Eye, label: 'View Listings Form' },
    { icon: BrainCircuit, label: 'Fill Transaction with AI' },
    { icon: Shield, label: 'Secure Escrow' },
    { icon: Coins, label: 'Instant Commission Paid' }
  ]

  return (
    <div className="glass-morphism border-t border-glass-white/10 p-6">
      <div className="max-w-7xl mx-auto flex items-center justify-between overflow-x-auto scrollbar-hide space-x-8">
        {steps.map((step, index) => (
          <div key={index} className="flex flex-col items-center space-y-3 flex-shrink-0 group">
            {/* Step Icon */}
            <div className="w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center group-hover:border-neon-cyan/50 group-hover:bg-neon-cyan/5 transition-all duration-300">
              <step.icon className="w-5 h-5 text-white/70 group-hover:text-neon-cyan transition-colors" />
            </div>
            
            {/* Step Label */}
            <p className="text-xs font-bold text-white text-center max-w-[140px] leading-tight uppercase tracking-tight">
              {step.label}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}

export default BottomWorkflowBar
