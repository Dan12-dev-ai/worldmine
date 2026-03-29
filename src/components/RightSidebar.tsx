import React, { useState, useEffect } from 'react'
import { Send, Shield, ShieldCheck, Activity, Terminal } from 'lucide-react'
import { Button } from './ui/button'
import { useMarketplaceStore } from '../store/marketplaceStore'

const RightSidebar: React.FC = () => {
  const { userProfile, securityLogs, walletBalance, pendingCommission } = useMarketplaceStore()
  const [chatInput, setChatInput] = useState('')
  const [chatMessages, setChatMessages] = useState<{role: 'user' | 'bot', content: string}[]>([])
  const [isScanning, setIsScanning] = useState(false)
  const [scanProgress, setScanProgress] = useState(0)
  const [stressTestStatus, setStressTestStatus] = useState<'idle' | 'running' | 'passed'>('idle')

  useEffect(() => {
    if (isScanning) {
      const interval = setInterval(() => {
        setScanProgress(prev => {
          if (prev >= 100) {
            setIsScanning(false)
            return 100
          }
          return prev + 1
        })
      }, 50)
      return () => clearInterval(interval)
    }
  }, [isScanning])

  const runStressTest = () => {
    setStressTestStatus('running')
    setTimeout(() => {
      setStressTestStatus('passed')
    }, 4000)
  }

  const handleSendMessage = () => {
    if (!chatInput.trim()) return
    
    const newMessages = [...chatMessages, { role: 'user' as const, content: chatInput }]
    setChatMessages(newMessages)
    setChatInput('')
    
    // Simulate AI Response
    setTimeout(() => {
      setChatMessages([...newMessages, { 
        role: 'bot', 
        content: `Analyzing market data for "${chatInput}"... Current trends suggest a 5.2% increase in ${userProfile?.userType === 'seller' ? 'demand' : 'supply'} over the next 48 hours.` 
      }])
    }, 1000)
  }

  return (
    <div className="w-full h-full glass-morphism p-6 space-y-6 overflow-y-auto scrollbar-hide">
      {/* Wallet Balance */}
      <div className="glass-morphism border border-neon-gold/20 rounded-xl p-5 bg-gradient-to-br from-neon-gold/5 to-transparent">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider">Secure Wallet Balance</span>
          <ShieldCheck className="w-4 h-4 text-neon-gold" />
        </div>
        <div className="text-3xl font-bold text-white mb-1">
          ${walletBalance.toLocaleString()}
        </div>
        <div className="flex justify-between items-center">
          <span className="text-[10px] text-neon-emerald font-bold">+{pendingCommission.toLocaleString()} PENDING</span>
          <Button variant="ghost" size="sm" className="h-6 px-2 text-[10px] border border-white/10">Withdraw</Button>
        </div>
      </div>

      {/* Security Logs Section */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-6 scrollbar-hide">
        <div className="glass-morphism border border-white/10 rounded-2xl p-4 bg-white/5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-[10px] font-bold text-white uppercase tracking-widest flex items-center">
              <Activity className="w-3 h-3 mr-2 text-neon-cyan" />
              Vulnerability Scanner
            </h3>
            {isScanning ? (
              <span className="text-[10px] text-neon-cyan font-mono">{scanProgress}%</span>
            ) : (
              <button 
                onClick={() => {
                  setIsScanning(true);
                  setScanProgress(0);
                }}
                className="text-[10px] text-neon-cyan hover:underline font-bold"
              >
                Start Scan
              </button>
            )}
          </div>
          <div className="h-1 bg-white/10 rounded-full overflow-hidden mb-3">
            <div 
              className="h-full bg-neon-cyan transition-all duration-300" 
              style={{ width: `${scanProgress}%` }}
            ></div>
          </div>
          <div className="space-y-2">
            <div className="flex items-center justify-between text-[10px]">
              <span className="text-gray-500 font-mono">XSS Detection:</span>
              <span className="text-neon-emerald font-bold">Secure</span>
            </div>
            <div className="flex items-center justify-between text-[10px]">
              <span className="text-gray-500 font-mono">SQL Injection:</span>
              <span className="text-neon-emerald font-bold">Protected</span>
            </div>
            <div className="flex items-center justify-between text-[10px]">
              <span className="text-gray-500 font-mono">CSRF Shield:</span>
              <span className="text-neon-emerald font-bold">Active</span>
            </div>
          </div>
        </div>

        {/* Database Stress Test Section */}
        <div className="glass-morphism border border-white/10 rounded-2xl p-4 bg-white/5">
          <h3 className="text-[10px] font-bold text-white uppercase tracking-widest flex items-center mb-4">
            <Terminal className="w-3 h-3 mr-2 text-neon-gold" />
            1M+ Stress Test
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-gray-500 uppercase">Load Capacity</span>
              <span className="text-[10px] text-neon-gold font-bold">1,000,000+ Transactions</span>
            </div>
            {stressTestStatus === 'idle' && (
              <Button 
                variant="ghost" 
                size="sm" 
                className="w-full h-8 text-[10px] border border-neon-gold/30 text-neon-gold hover:bg-neon-gold/10 uppercase font-black"
                onClick={runStressTest}
              >
                Run Scalability Test
              </Button>
            )}
            {stressTestStatus === 'running' && (
              <div className="flex flex-col items-center py-2">
                <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden mb-2">
                  <div className="h-full bg-neon-gold animate-[shimmer_2s_infinite] w-full" style={{ background: 'linear-gradient(90deg, transparent, #fbbf24, transparent)' }}></div>
                </div>
                <span className="text-[8px] text-neon-gold animate-pulse uppercase font-bold">Testing Concurrent Writes...</span>
              </div>
            )}
            {stressTestStatus === 'passed' && (
              <div className="bg-neon-emerald/10 border border-neon-emerald/30 p-3 rounded-xl flex items-center animate-in zoom-in duration-300">
                <ShieldCheck className="w-4 h-4 text-neon-emerald mr-2" />
                <div>
                  <p className="text-[9px] text-neon-emerald font-black uppercase">Test Passed</p>
                  <p className="text-[8px] text-gray-400">Database handled 1.2M writes in 420ms</p>
                </div>
              </div>
            )}
          </div>
        </div>

        <h3 className="text-[10px] font-bold text-gray-500 uppercase tracking-widest px-2">Network Security Logs</h3>

        <div className="space-y-3">
          {securityLogs.map((log: any) => (
            <div key={log.id} className="flex items-start space-x-3 group">
              <div className={`mt-1 w-2 h-2 rounded-full flex-shrink-0 ${
                log.status === 'secure' ? 'bg-neon-emerald' : 
                log.status === 'warning' ? 'bg-neon-gold' : 'bg-red-500'
              }`} />
              <div className="flex-1 min-w-0">
                <p className="text-[11px] text-gray-300 leading-tight group-hover:text-white transition-colors">{log.event}</p>
                <span className="text-[9px] text-gray-600 font-mono">{log.time}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Live Commission Earnings */}
      <div className="bg-[#0a1a1a] border border-neon-emerald/40 rounded-2xl p-6 shadow-[0_0_20px_rgba(16,185,129,0.1)] relative overflow-hidden group">
        <div className="absolute top-0 right-0 w-32 h-32 bg-neon-emerald/5 blur-3xl -mr-16 -mt-16 group-hover:bg-neon-emerald/10 transition-colors"></div>
        <div className="flex items-center justify-between mb-4 relative z-10">
          <div className="w-12 h-12 rounded-xl bg-neon-emerald/20 flex items-center justify-center border border-neon-emerald/40 shadow-[0_0_15px_rgba(16,185,129,0.3)]">
            <Shield className="w-7 h-7 text-neon-emerald" />
          </div>
          <div className="text-right">
            <div className="text-[10px] text-neon-emerald font-bold uppercase tracking-[0.2em] mb-1">Live Commission Earnings</div>
            <div className="text-3xl font-black text-white neon-text tracking-tighter">
              $18,742
            </div>
          </div>
        </div>
        <div className="text-[9px] text-gray-500 font-medium tracking-wide relative z-10">
          Instant Payment to Payoneer / MasterCard / Wallet
        </div>
      </div>

      {/* AI Chat Assistant */}
      <div className="glass-morphism border border-neon-cyan/20 rounded-xl p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-bold text-white font-orbitron uppercase tracking-wider">AI Security Assistant</h3>
          <ShieldCheck className="w-4 h-4 text-neon-cyan animate-pulse" />
        </div>
        
        <div className="bg-cyber-navy/50 rounded-lg p-3 mb-4 max-h-40 overflow-y-auto space-y-2 scrollbar-hide">
          <div className="text-[11px] text-gray-400">
            🤖 AI: Identity verified via 2FA. System is currently scanning for market anomalies.
          </div>
          {chatMessages.map((msg, i) => (
            <div key={i} className={`text-[11px] ${msg.role === 'user' ? 'text-neon-cyan text-right' : 'text-gray-300'}`}>
              {msg.role === 'user' ? 'You: ' : '🤖: '} {msg.content}
            </div>
          ))}
        </div>
        
        <div className="flex space-x-2">
          <input
            type="text"
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Ask Security AI..."
            className="flex-1 px-3 py-2 bg-cyber-dark/50 border border-glass-white/20 rounded-lg text-white placeholder-gray-600 text-[10px] focus:outline-none focus:border-neon-cyan/50"
          />
          <Button size="icon" variant="cyber" className="h-8 w-8" onClick={handleSendMessage}>
            <Send className="w-3 h-3" />
          </Button>
        </div>
      </div>
    </div>
  )
}

export default RightSidebar
