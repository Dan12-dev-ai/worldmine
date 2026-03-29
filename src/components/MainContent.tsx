import React from 'react'
import { listings } from '../data/commodities'
import ListingCard from './ListingCard'
import { Button } from './ui/button'
import { useMarketplaceStore } from '../store/marketplaceStore'
import { 
  LayoutGrid, 
  TrendingUp, 
  Wallet, 
  BrainCircuit, 
  Search, 
  ChevronDown, 
  ShieldCheck,
  Zap,
  DollarSign,
  ArrowRight,
  Mic,
  PenTool,
  Send,
  Plus,
  FileText,
  ChevronRight,
  Clock,
  Star,
  Gavel,
  Scale
} from 'lucide-react'

const MainContent: React.FC = () => {
  const { activeTab, setActiveTab, isLoading, transactions, pendingCommission, walletBalance, withdrawCommission } = useMarketplaceStore()
  const [showWithdrawSuccess, setShowWithdrawSuccess] = React.useState(false)

  const handleWithdraw = () => {
    if (pendingCommission > 0) {
      withdrawCommission()
      setShowWithdrawSuccess(true)
      setTimeout(() => setShowWithdrawSuccess(false), 3000)
    }
  }

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-neon-cyan/20 border-t-neon-cyan rounded-full animate-spin"></div>
      </div>
    )
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'Live Discussions':
        return (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold text-white font-orbitron tracking-tight">Live Negotiation Rooms</h2>
                <p className="text-gray-400 text-sm mt-1">Real-time WebRTC-secured communication channels</p>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-neon-emerald rounded-full animate-pulse"></div>
                <span className="text-xs text-neon-emerald font-bold">12 ACTIVE ROOMS</span>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {[
                { title: 'Iron Ore Bulk Purchase', party: 'Rio Tinto x Mitsui', status: 'Negotiating', color: 'neon-cyan' },
                { title: 'Lithium Supply Contract', party: 'Tesla x Albemarle', status: 'Drafting Contract', color: 'neon-emerald' },
                { title: 'Gold Bullion Export', party: 'Barrick x Dubai Gold', status: 'Verifying Escrow', color: 'neon-gold' },
              ].map((room, i) => (
                <div key={i} className="glass-morphism border border-white/10 rounded-2xl p-6 hover:border-neon-cyan/50 transition-all cursor-pointer group">
                  <div className="flex justify-between items-start mb-6">
                    <div>
                      <h3 className="text-xl font-bold text-white group-hover:text-neon-cyan transition-colors">{room.title}</h3>
                      <p className="text-sm text-gray-500 mt-1">{room.party}</p>
                    </div>
                    <div className={`px-3 py-1 rounded-full text-[10px] font-bold border border-${room.color}/30 bg-${room.color}/10 text-${room.color}`}>
                      {room.status}
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex -space-x-2">
                      {[1, 2, 3].map(n => (
                        <div key={n} className="w-8 h-8 rounded-full border-2 border-cyber-dark bg-gray-800 overflow-hidden">
                          <img src={`https://i.pravatar.cc/150?u=${n+i}`} />
                        </div>
                      ))}
                    </div>
                    <Button variant="cyber" size="sm" onClick={() => setActiveTab('Negotiation Room')}>Enter Room</Button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )
      case 'Negotiation Room':
        return (
          <div className="grid grid-cols-12 gap-6 h-[700px] animate-in zoom-in-95 duration-500">
            {/* Video Feeds */}
            <div className="col-span-12 lg:col-span-8 flex flex-col space-y-4">
              <div className="flex-1 grid grid-cols-2 gap-4">
                <div className="relative rounded-2xl overflow-hidden border border-white/10 bg-black">
                  <img src="https://images.unsplash.com/photo-1560250097-0b93528c311a?w=800" className="w-full h-full object-cover opacity-80" />
                  <div className="absolute bottom-4 left-4 bg-black/60 px-3 py-1 rounded-lg text-xs text-white">Buyer: John Chen</div>
                  <div className="absolute top-4 right-4 flex space-x-2">
                    <div className="w-8 h-8 rounded-full bg-red-500/20 flex items-center justify-center border border-red-500/50"><Mic className="w-4 h-4 text-red-500" /></div>
                  </div>
                </div>
                <div className="relative rounded-2xl overflow-hidden border border-white/10 bg-black">
                  <img src="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=800" className="w-full h-full object-cover opacity-80" />
                  <div className="absolute bottom-4 left-4 bg-black/60 px-3 py-1 rounded-lg text-xs text-white">Seller: Sarah Miller</div>
                  <div className="absolute top-4 right-4 flex space-x-2">
                    <div className="w-8 h-8 rounded-full bg-neon-emerald/20 flex items-center justify-center border border-neon-emerald/50"><Mic className="w-4 h-4 text-neon-emerald" /></div>
                  </div>
                </div>
              </div>
              
              {/* Shared Negotiation Canvas */}
              <div className="h-48 glass-morphism border border-neon-cyan/30 rounded-2xl p-6 relative">
                <div className="absolute top-4 left-6 flex items-center space-x-2">
                  <PenTool className="w-4 h-4 text-neon-cyan" />
                  <span className="text-xs font-bold text-neon-cyan uppercase tracking-widest">Shared Negotiation Canvas</span>
                </div>
                <div className="flex items-center justify-center h-full pt-6">
                  <div className="w-full max-w-xl space-y-4">
                    <div className="flex justify-between text-xs text-gray-400">
                      <span>Price Slider (USD/Ton)</span>
                      <span className="text-neon-cyan font-bold">$16,200</span>
                    </div>
                    <input type="range" className="w-full accent-neon-cyan" min="15000" max="18000" />
                    <div className="flex justify-between">
                      <Button variant="ghost" size="sm" className="text-[10px] border border-white/10">Counter Offer</Button>
                      <Button variant="cyber" size="sm" className="text-[10px]">Accept Terms</Button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* AI Drafting & Chat */}
            <div className="col-span-12 lg:col-span-4 flex flex-col space-y-4">
              <div className="flex-1 glass-morphism border border-white/10 rounded-2xl p-5 flex flex-col">
                <h3 className="text-sm font-bold text-white mb-4 flex items-center">
                  <BrainCircuit className="w-4 h-4 text-neon-emerald mr-2" />
                  AI Negotiation Agent
                </h3>
                <div className="flex-1 overflow-y-auto space-y-3 mb-4 scrollbar-hide">
                  <div className="bg-neon-emerald/10 border border-neon-emerald/20 p-3 rounded-xl">
                    <p className="text-[11px] text-gray-300">🤖 AI: Analysis suggests $16,200 is 5% above market average but includes premium shipping terms. Drafting Clause 4.2 now...</p>
                  </div>
                  <div className="bg-white/5 p-3 rounded-xl">
                    <p className="text-[11px] text-neon-cyan font-bold mb-1">DRAFT: DELIVERY SCHEDULE</p>
                    <p className="text-[10px] text-gray-500">Materials to be dispatched via Port of Durban by April 15th, 2026. FOB terms apply.</p>
                  </div>
                </div>
                <div className="flex space-x-2">
                  <input className="flex-1 bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-xs text-white" placeholder="Chat or command AI..." />
                  <Button size="icon" variant="cyber" className="h-9 w-9"><Send className="w-4 h-4" /></Button>
                </div>
              </div>
              <Button variant="cyber" className="h-12 font-bold bg-neon-emerald/20 border-neon-emerald/50 text-neon-emerald">
                <FileText className="w-4 h-4 mr-2" />
                GENERATE SMART CONTRACT
              </Button>
            </div>
          </div>
        )
      case 'My Deals':
        return (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold text-white font-orbitron tracking-tight">My Deals</h2>
                <p className="text-gray-400 text-sm mt-1">Manage your active contracts and historical trades</p>
              </div>
            </div>

            <div className="space-y-4">
              {[
                { id: 'DEAL-8821', material: 'Copper Cathodes', party: 'Chile Mining Corp', value: '$840,000', status: 'In Transit', progress: 65 },
                { id: 'DEAL-9104', material: 'Iron Ore Fines', party: 'Australian Metals', value: '$1,250,000', status: 'Contract Signed', progress: 30 },
                { id: 'DEAL-7245', material: 'Gold Bullion', party: 'Swiss Refinery', value: '$450,000', status: 'Delivered', progress: 100 },
              ].map((deal, i) => (
                <div key={i} className="glass-morphism border border-white/10 rounded-2xl p-6 flex flex-col md:flex-row items-center justify-between gap-6 hover:border-neon-cyan/30 transition-all cursor-pointer">
                  <div className="flex items-center space-x-6 w-full md:w-auto">
                    <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center flex-shrink-0">
                      <FileText className="w-6 h-6 text-neon-cyan" />
                    </div>
                    <div>
                      <div className="text-[10px] text-gray-500 font-bold uppercase">{deal.id}</div>
                      <h3 className="text-lg font-bold text-white">{deal.material}</h3>
                      <p className="text-xs text-gray-500">Counterparty: {deal.party}</p>
                    </div>
                  </div>
                  
                  <div className="flex-1 w-full max-w-xs space-y-2">
                    <div className="flex justify-between text-[10px]">
                      <span className="text-gray-500 uppercase">FULFILLMENT PROGRESS</span>
                      <span className="text-neon-emerald font-bold">{deal.progress}%</span>
                    </div>
                    <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                      <div className="bg-neon-emerald h-full transition-all duration-1000" style={{ width: `${deal.progress}%` }}></div>
                    </div>
                  </div>

                  <div className="text-right w-full md:w-auto">
                    <div className="text-lg font-bold text-white">{deal.value}</div>
                    <div className="text-[10px] text-neon-emerald font-bold uppercase">{deal.status}</div>
                  </div>
                  
                  <Button variant="ghost" size="icon" className="h-10 w-10 border border-white/10 hidden md:flex"><ChevronRight className="w-4 h-4" /></Button>
                </div>
              ))}
            </div>
          </div>
        )
      case 'Buy Materials':
        return (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold text-white font-orbitron tracking-tight">Buy Materials</h2>
                <p className="text-gray-400 text-sm mt-1">Connect with verified mines and secure high-quality supply</p>
              </div>
              <Button variant="cyber" size="sm" onClick={() => setActiveTab('Marketplace')}>Open Marketplace</Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { label: 'Bulk Orders', count: 42, icon: LayoutGrid },
                { label: 'Spot Deals', count: 128, icon: Zap },
                { label: 'Verified Mines', count: 86, icon: ShieldCheck },
                { label: 'Future Contracts', count: 15, icon: Clock },
              ].map((stat, i) => (
                <div key={i} className="glass-morphism border border-white/10 p-4 rounded-2xl flex items-center space-x-4">
                  <div className="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center">
                    <stat.icon className="w-5 h-5 text-neon-cyan" />
                  </div>
                  <div>
                    <div className="text-[10px] text-gray-500 font-bold uppercase">{stat.label}</div>
                    <div className="text-lg font-bold text-white">{stat.count}</div>
                  </div>
                </div>
              ))}
            </div>

            <div className="glass-morphism border border-white/10 rounded-3xl p-8">
              <h3 className="text-xl font-bold text-white mb-6">Request Specific Material</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div className="space-y-2">
                  <label className="text-[10px] text-gray-500 font-bold uppercase">Material Needed</label>
                  <input className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white" placeholder="e.g. Cobalt Hydroxide" />
                </div>
                <div className="space-y-2">
                  <label className="text-[10px] text-gray-500 font-bold uppercase">Estimated Monthly Volume</label>
                  <input className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white" placeholder="2,000 Tons" />
                </div>
              </div>
              <Button variant="cyber" className="w-full h-12 font-bold uppercase tracking-widest">Broadcast Request to Verified Mines</Button>
            </div>
          </div>
        )
      case 'Sell Materials':
        return (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold text-white font-orbitron tracking-tight">Sell Your Materials</h2>
                <p className="text-gray-400 text-sm mt-1">List commodities to our global network of verified buyers</p>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="glass-morphism border border-white/10 rounded-3xl p-8 space-y-6">
                <h3 className="text-lg font-bold text-white">Create New Listing</h3>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-[10px] text-gray-500 font-bold uppercase">Material Type</label>
                    <select className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white focus:border-neon-cyan transition-all">
                      <option>Copper Concentrate (Cu &gt; 25%)</option>
                      <option>Iron Ore (Fe &gt; 62%)</option>
                      <option>Lithium Carbonate (Li2CO3)</option>
                    </select>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-[10px] text-gray-500 font-bold uppercase">Quantity (Tons)</label>
                      <input className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white" placeholder="500" />
                    </div>
                    <div className="space-y-2">
                      <label className="text-[10px] text-gray-500 font-bold uppercase">Base Price (USD/T)</label>
                      <input className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white" placeholder="8500" />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="text-[10px] text-gray-500 font-bold uppercase">Origin Mine</label>
                    <input className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white" placeholder="Escondida Mine, Chile" />
                  </div>
                  <Button variant="cyber" className="w-full h-12 font-bold uppercase tracking-widest">Post Global Listing</Button>
                </div>
              </div>

              <div className="space-y-6">
                <div className="glass-morphism border border-neon-emerald/30 rounded-3xl p-8 bg-neon-emerald/5">
                  <h3 className="text-lg font-bold text-white mb-4">AI Seller Agent Active</h3>
                  <p className="text-xs text-gray-400 mb-6">Your agent is currently analyzing buyer intent for Copper. 14 potential matches found in the last 24 hours.</p>
                  <div className="flex items-center space-x-4">
                    <div className="w-2 h-2 bg-neon-emerald rounded-full animate-ping"></div>
                    <span className="text-[10px] text-neon-emerald font-bold uppercase">Automated Matching Enabled</span>
                  </div>
                </div>
                <div className="glass-morphism border border-white/10 rounded-3xl p-8 h-48 flex items-center justify-center border-dashed group cursor-pointer hover:border-neon-cyan/50 transition-all">
                  <div className="text-center">
                    <div className="w-12 h-12 bg-white/5 rounded-full flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform">
                      <Plus className="w-6 h-6 text-gray-500 group-hover:text-neon-cyan" />
                    </div>
                    <p className="text-[10px] text-gray-500 font-bold uppercase">Upload Inspection Certificates</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )
      case 'Analytics':
        return (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold text-white font-orbitron tracking-tight">Market Intelligence</h2>
                <p className="text-gray-400 text-sm mt-1">Predictive analytics and real-time commodity pricing</p>
              </div>
              <div className="flex items-center space-x-4 bg-white/5 border border-white/10 rounded-xl px-4 py-2">
                <div className="flex flex-col">
                  <span className="text-[10px] text-gray-500 uppercase">Copper (LME)</span>
                  <span className="text-sm font-bold text-neon-emerald">$8,942.50 (+1.2%)</span>
                </div>
                <div className="w-px h-8 bg-white/10"></div>
                <div className="flex flex-col">
                  <span className="text-[10px] text-gray-500 uppercase">Gold (COMEX)</span>
                  <span className="text-sm font-bold text-neon-gold">$2,145.20 (-0.4%)</span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 glass-morphism border border-white/10 rounded-3xl p-8 h-[400px] flex flex-col">
                <div className="flex justify-between items-center mb-8">
                  <h3 className="text-lg font-bold text-white">Global Demand Forecast</h3>
                  <div className="flex space-x-2">
                    <Button variant="ghost" size="sm" className="h-6 text-[10px] border border-white/10">1W</Button>
                    <Button variant="ghost" size="sm" className="h-6 text-[10px] bg-neon-cyan/20 text-neon-cyan">1M</Button>
                    <Button variant="ghost" size="sm" className="h-6 text-[10px] border border-white/10">1Y</Button>
                  </div>
                </div>
                <div className="flex-1 flex items-end justify-between space-x-4">
                  {[45, 60, 55, 80, 75, 90, 85, 95, 100, 90, 80, 85].map((h, i) => (
                    <div key={i} className="flex-1 group relative">
                      <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-cyber-dark border border-neon-cyan/50 px-2 py-1 rounded text-[8px] text-white opacity-0 group-hover:opacity-100 transition-opacity">
                        {h}%
                      </div>
                      <div 
                        className="w-full bg-gradient-to-t from-neon-cyan/20 to-neon-cyan rounded-t-sm transition-all duration-500 group-hover:brightness-125" 
                        style={{ height: `${h}%` }}
                      ></div>
                    </div>
                  ))}
                </div>
                <div className="flex justify-between mt-4 text-[10px] text-gray-500 font-mono">
                  {['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'].map(m => <span key={m}>{m}</span>)}
                </div>
              </div>

              <div className="glass-morphism border border-white/10 rounded-3xl p-8 flex flex-col">
                <h3 className="text-lg font-bold text-white mb-6">Market Sentiments</h3>
                <div className="space-y-6">
                  {[
                    { label: 'Supply Chain Reliability', val: 94, color: 'neon-emerald' },
                    { label: 'Price Volatility Index', val: 42, color: 'neon-gold' },
                    { label: 'Sustainability Rating', val: 88, color: 'neon-cyan' },
                  ].map((s, i) => (
                    <div key={i} className="space-y-2">
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-400">{s.label}</span>
                        <span className={`text-${s.color} font-bold`}>{s.val}%</span>
                      </div>
                      <div className="w-full bg-white/5 h-2 rounded-full overflow-hidden">
                        <div className={`bg-${s.color} h-full w-[${s.val}%]`}></div>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-auto pt-8 border-t border-white/10">
                  <div className="bg-neon-cyan/5 border border-neon-cyan/20 p-4 rounded-2xl">
                    <p className="text-[10px] text-neon-cyan font-bold mb-1 uppercase tracking-widest">AI Prediction</p>
                    <p className="text-xs text-gray-400 leading-relaxed">High probability of lithium supply shortage in Q3 due to mining restrictions in South America. Accumulation recommended.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )
      case 'AI Agents':
        return (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold text-white font-orbitron tracking-tight">Autonomous AI Agents</h2>
                <p className="text-gray-400 text-sm mt-1">Deploy and manage your fleet of specialized trading bots</p>
              </div>
              <Button variant="cyber" size="sm">Deploy New Agent</Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[
                { name: 'Copper Scout', type: 'Buyer Agent', task: 'Monitoring Chile Mines', status: 'Active', icon: Search, color: 'neon-cyan' },
                { name: 'Deal Closer v4', type: 'Negotiation Bot', task: 'Finalizing 12 Contracts', status: 'Negotiating', icon: BrainCircuit, color: 'neon-emerald' },
                { name: 'Risk Sentinel', type: 'Security Bot', task: 'Auditing Smart Contracts', status: 'Standby', icon: ShieldCheck, color: 'neon-gold' },
              ].map((agent, i) => (
                <div key={i} className="glass-morphism border border-white/10 rounded-2xl p-6 relative overflow-hidden group">
                  <div className={`absolute top-0 right-0 w-24 h-24 bg-${agent.color}/5 blur-2xl rounded-full -mr-12 -mt-12 transition-all group-hover:scale-150`}></div>
                  <div className="relative z-10">
                    <div className={`w-12 h-12 rounded-xl bg-${agent.color}/10 border border-${agent.color}/30 flex items-center justify-center mb-4`}>
                      <agent.icon className={`w-6 h-6 text-${agent.color}`} />
                    </div>
                    <h3 className="text-lg font-bold text-white mb-1">{agent.name}</h3>
                    <p className={`text-[10px] font-bold text-${agent.color} uppercase tracking-widest mb-4`}>{agent.type}</p>
                    <div className="space-y-2 mb-6">
                      <div className="flex justify-between text-[10px]">
                        <span className="text-gray-500">CURRENT TASK</span>
                        <span className="text-gray-300">{agent.task}</span>
                      </div>
                      <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden">
                        <div className={`bg-${agent.color} h-full w-2/3 animate-pulse`}></div>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className={`text-[10px] font-bold text-${agent.color} flex items-center`}>
                        <div className={`w-1.5 h-1.5 bg-${agent.color} rounded-full mr-2 animate-ping`}></div>
                        {agent.status}
                      </span>
                      <Button variant="ghost" size="sm" className="h-7 text-[10px] border border-white/10">Configure</Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )
      case 'Dispute Resolution':
        return (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold text-white font-orbitron tracking-tight">AI Dispute Resolution</h2>
                <p className="text-gray-400 text-sm mt-1">Autonomous neutral mediation for complex mining contracts</p>
              </div>
              <div className="flex items-center space-x-2 bg-neon-emerald/10 border border-neon-emerald/30 rounded-full px-4 py-1.5">
                <div className="w-2 h-2 bg-neon-emerald rounded-full animate-pulse"></div>
                <span className="text-[10px] text-neon-emerald font-bold uppercase tracking-widest">System Active</span>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2 space-y-6">
                <div className="glass-morphism border border-white/10 rounded-3xl p-8 relative overflow-hidden">
                  <div className="absolute top-0 right-0 p-8 opacity-10">
                    <Scale className="w-32 h-32 text-neon-cyan" />
                  </div>
                  <div className="relative z-10">
                    <h3 className="text-xl font-bold text-white mb-6 flex items-center">
                      <Gavel className="w-5 h-5 text-neon-cyan mr-3" />
                      Active Case: DISPUTE-4281
                    </h3>
                    <div className="space-y-6">
                      <div className="flex justify-between items-center p-4 bg-white/5 border border-white/10 rounded-2xl">
                        <div>
                          <p className="text-[10px] text-gray-500 uppercase font-bold mb-1">Parties Involved</p>
                          <p className="text-sm text-white font-bold">Zambia Copper Mines vs. Global Logistics Ltd</p>
                        </div>
                        <div className="text-right">
                          <p className="text-[10px] text-gray-500 uppercase font-bold mb-1">Amount at Stake</p>
                          <p className="text-sm text-neon-gold font-bold">$240,000.00</p>
                        </div>
                      </div>

                      <div className="space-y-4">
                        <div className="flex items-start space-x-4">
                          <div className="w-10 h-10 rounded-full bg-neon-cyan/20 flex items-center justify-center shrink-0">
                            <BrainCircuit className="w-5 h-5 text-neon-cyan" />
                          </div>
                          <div className="flex-1 bg-neon-cyan/5 border border-neon-cyan/20 p-4 rounded-2xl">
                            <p className="text-xs text-gray-300 leading-relaxed italic">
                              "AI Analysis: Clause 7.2 regarding Force Majeure is under review. Comparing current port congestion data in Durban with historical benchmarks..."
                            </p>
                          </div>
                        </div>
                        <div className="flex items-start space-x-4">
                          <div className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center shrink-0">
                            <ShieldCheck className="w-5 h-5 text-gray-500" />
                          </div>
                          <div className="flex-1 bg-white/5 border border-white/10 p-4 rounded-2xl">
                            <p className="text-xs text-gray-400">
                              Neutral Auditor: Verifying weight certificates from third-party inspection agent (SGS).
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Button variant="cyber" className="h-14 font-bold uppercase tracking-widest bg-neon-cyan/20 border-neon-cyan/50 text-neon-cyan">
                    Submit Evidence
                  </Button>
                  <Button variant="ghost" className="h-14 font-bold uppercase tracking-widest border border-white/10">
                    Request Human Mediator
                  </Button>
                </div>
              </div>

              <div className="space-y-6">
                <div className="glass-morphism border border-white/10 rounded-3xl p-6">
                  <h4 className="text-sm font-bold text-white mb-4 uppercase tracking-widest">Mediation Metrics</h4>
                  <div className="space-y-4">
                    {[
                      { label: 'AI Accuracy Rating', val: 99.4, color: 'neon-emerald' },
                      { label: 'Avg. Resolution Time', val: '4.2h', color: 'neon-cyan' },
                      { label: 'Settlement Success', val: 92, color: 'neon-gold' },
                    ].map((m, i) => (
                      <div key={i} className="flex items-center justify-between">
                        <span className="text-[10px] text-gray-500 font-bold uppercase">{m.label}</span>
                        <span className={`text-sm font-bold text-${m.color}`}>{m.val}{typeof m.val === 'number' ? '%' : ''}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="glass-morphism border border-neon-emerald/30 rounded-3xl p-6 bg-neon-emerald/5">
                  <h4 className="text-sm font-bold text-white mb-2 uppercase tracking-widest">Smart Settlement</h4>
                  <p className="text-[10px] text-gray-400 mb-4 leading-relaxed">
                    Once both parties accept the AI recommendation, funds are automatically released from escrow via smart contract execution.
                  </p>
                  <div className="flex items-center text-[10px] text-neon-emerald font-black uppercase tracking-widest">
                    <ShieldCheck className="w-3 h-3 mr-2" />
                    Guaranteed Payout
                  </div>
                </div>
              </div>
            </div>
          </div>
        )
      case 'Marketplace':
        return (
          <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
            {/* Top Row Marketplace Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {/* Iron Ore Card - Exact Design */}
              <div className="bg-[#0d1117] border border-white/5 rounded-[2.5rem] overflow-hidden group hover:border-neon-cyan/30 transition-all duration-500 shadow-2xl relative">
                <div className="absolute inset-0 bg-gradient-to-br from-neon-cyan/5 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
                <div className="relative h-52">
                  <img src="https://images.unsplash.com/photo-1590487817434-a35d1b7e7b85?w=600&h=400&fit=crop" className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-1000" />
                  <div className="absolute inset-0 bg-gradient-to-t from-[#0d1117] via-transparent to-transparent"></div>
                  
                  {/* Holographic Overlay Effect */}
                  <div className="absolute inset-0 bg-[linear-gradient(110deg,rgba(255,255,255,0.05)_20%,rgba(255,255,255,0.1)_40%,rgba(255,255,255,0.05)_60%)] bg-[length:200%_100%] animate-holographic opacity-0 group-hover:opacity-100 transition-opacity"></div>
                  
                  {/* Seller Info */}
                  <div className="absolute top-5 left-5 flex items-center space-x-3 bg-black/40 backdrop-blur-md rounded-full pl-1 pr-4 py-1 border border-white/10 hover:bg-black/60 transition-colors">
                    <div className="w-8 h-8 rounded-full border border-white/20 overflow-hidden">
                      <img src="https://i.pravatar.cc/150?u=seller1" />
                    </div>
                    <span className="text-[10px] font-bold text-white uppercase tracking-wider">Seller</span>
                  </div>

                  {/* Premium Badge */}
                  <div className="absolute top-5 right-5">
                    <div className="bg-neon-gold/20 backdrop-blur-md border border-neon-gold/50 rounded-full px-3 py-1 flex items-center space-x-1 shadow-[0_0_15px_rgba(255,215,0,0.2)]">
                      <Star className="w-3 h-3 text-neon-gold fill-current" />
                      <span className="text-[9px] text-neon-gold font-black tracking-widest uppercase">Premium</span>
                    </div>
                  </div>
                </div>

                <div className="p-7 relative z-10">
                  <div className="flex justify-between items-end mb-6">
                    <div>
                      <h3 className="text-2xl font-black text-white mb-1 font-orbitron tracking-tight group-hover:text-neon-cyan transition-colors">Iron Ore</h3>
                      <p className="text-[10px] text-gray-500 font-bold uppercase tracking-[0.2em]">Copper, Aluminium</p>
                      <p className="text-[10px] text-gray-600 mt-1 font-medium">Fe-Li-Lithium</p>
                    </div>
                    <div className="text-right">
                      <div className="text-neon-emerald text-[10px] font-black tracking-widest flex items-center justify-end mb-1">
                        <div className="w-1.5 h-1.5 bg-neon-emerald rounded-full animate-pulse mr-2"></div>
                        LIVE 38%
                      </div>
                      <div className="text-2xl font-black text-white tracking-tighter group-hover:scale-110 transition-transform origin-right">$16,200</div>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <Button variant="cyber" className="h-12 rounded-xl text-[10px] font-black uppercase tracking-[0.2em] shadow-[0_0_20px_rgba(0,255,255,0.2)] hover:shadow-[0_0_30px_rgba(0,255,255,0.4)]">Buy Now</Button>
                    <Button variant="ghost" className="h-12 rounded-xl text-[10px] font-black uppercase tracking-[0.2em] border border-white/10 hover:bg-white/5 hover:border-white/30">Make Offer</Button>
                  </div>
                </div>
              </div>

              {/* AI Best Match Card - Exact Design */}
              <div className="bg-[#0d1117] border border-white/5 rounded-[2.5rem] overflow-hidden group hover:border-neon-emerald/30 transition-all duration-500 shadow-2xl relative">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(16,185,129,0.05),transparent_70%)]"></div>
                <div className="relative h-52 flex items-center justify-center p-8">
                  <div className="absolute inset-0 overflow-hidden opacity-20">
                    <img src="https://images.unsplash.com/photo-1614850523296-d8c1af93d400?w=600" className="w-full h-full object-cover grayscale" />
                  </div>
                  <div className="relative z-10 w-24 h-24 rounded-full border-2 border-neon-emerald/30 flex items-center justify-center bg-neon-emerald/10 shadow-[0_0_40px_rgba(16,185,129,0.2)]">
                    <BrainCircuit className="w-12 h-12 text-neon-emerald" />
                  </div>
                  <div className="absolute top-5 right-5">
                    <div className="bg-neon-emerald/20 backdrop-blur-md border border-neon-emerald/50 rounded-full px-3 py-1">
                      <span className="text-[9px] text-neon-emerald font-black tracking-widest uppercase">Verified</span>
                    </div>
                  </div>
                  <div className="absolute top-5 left-5 flex items-center space-x-3 bg-black/40 backdrop-blur-md rounded-full pl-1 pr-4 py-1 border border-white/10">
                    <div className="w-8 h-8 rounded-full border border-white/20 overflow-hidden">
                      <img src="https://i.pravatar.cc/150?u=seller2" />
                    </div>
                    <span className="text-[10px] font-bold text-white uppercase tracking-wider">Seller Match</span>
                  </div>
                </div>

                <div className="p-7 relative z-10">
                  <div className="flex justify-between items-end mb-6">
                    <div>
                      <h3 className="text-2xl font-black text-white mb-1 font-orbitron tracking-tight">AI Best Match</h3>
                      <div className="text-2xl font-black text-white tracking-tighter">$1900</div>
                    </div>
                    <div className="text-right">
                      <div className="text-neon-emerald text-[10px] font-black tracking-widest flex items-center justify-end mb-1">
                        LIVE 30%
                      </div>
                      <div className="text-lg font-bold text-gray-500 line-through">$1640</div>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <Button variant="cyber" className="h-12 rounded-xl text-[10px] font-black uppercase tracking-[0.2em] bg-neon-emerald/20 border-neon-emerald/50 text-neon-emerald">Buy Now</Button>
                    <Button variant="ghost" className="h-12 rounded-xl text-[10px] font-black uppercase tracking-[0.2em] border border-white/10 hover:bg-white/5">Make Offer</Button>
                  </div>
                </div>
              </div>

              {/* Best Match Card - Exact Design */}
              <div className="bg-[#0d1117] border border-white/5 rounded-[2.5rem] overflow-hidden group hover:border-neon-cyan/30 transition-all duration-500 shadow-2xl relative">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(0,255,255,0.05),transparent_70%)]"></div>
                <div className="relative h-52 flex items-center justify-center p-8">
                  <div className="absolute inset-0 overflow-hidden opacity-20">
                    <img src="https://images.unsplash.com/photo-1639322537228-f710d846310a?w=600" className="w-full h-full object-cover grayscale" />
                  </div>
                  <div className="relative z-10 w-24 h-24 rounded-full border-2 border-neon-cyan/30 flex items-center justify-center bg-neon-cyan/10 shadow-[0_0_40px_rgba(0,255,255,0.2)]">
                    <div className="text-neon-cyan text-4xl font-black font-orbitron">A</div>
                  </div>
                  <div className="absolute top-5 right-5">
                    <div className="bg-neon-emerald/20 backdrop-blur-md border border-neon-emerald/50 rounded-full px-3 py-1">
                      <span className="text-[9px] text-neon-emerald font-black tracking-widest uppercase">Verified</span>
                    </div>
                  </div>
                  <div className="absolute top-5 left-5 flex items-center space-x-3 bg-black/40 backdrop-blur-md rounded-full pl-1 pr-4 py-1 border border-white/10">
                    <div className="w-8 h-8 rounded-full border border-white/20 overflow-hidden">
                      <img src="https://i.pravatar.cc/150?u=seller3" />
                    </div>
                    <span className="text-[10px] font-bold text-white uppercase tracking-wider">Best Match</span>
                  </div>
                </div>

                <div className="p-7 relative z-10">
                  <div className="flex justify-between items-end mb-6">
                    <div>
                      <h3 className="text-2xl font-black text-white mb-1 font-orbitron tracking-tight">Best Match</h3>
                      <div className="text-2xl font-black text-white tracking-tighter">$1360</div>
                    </div>
                    <div className="text-right">
                      <div className="text-neon-emerald text-[10px] font-black tracking-widest flex items-center justify-end mb-1">
                        LIVE 10%
                      </div>
                      <div className="text-lg font-bold text-gray-500 line-through">$1840</div>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <Button variant="cyber" className="h-12 rounded-xl text-[10px] font-black uppercase tracking-[0.2em]">Buy Now</Button>
                    <Button variant="ghost" className="h-12 rounded-xl text-[10px] font-black uppercase tracking-[0.2em] border border-white/10 hover:bg-white/5">Make Offer</Button>
                  </div>
                </div>
              </div>
            </div>

            {/* Second Row Marketplace Cards */}
            <div className="flex items-center justify-between mt-12 mb-8">
              <h2 className="text-3xl font-black text-white font-orbitron tracking-tight">Featured Marketplace</h2>
              <div className="flex items-center space-x-4">
                <Button variant="ghost" className="text-[10px] font-black uppercase tracking-widest border border-white/10">Feature V</Button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {/* Lithium Card */}
              <div className="bg-[#0d1117] border border-white/5 rounded-[2.5rem] overflow-hidden group hover:border-neon-cyan/30 transition-all duration-500 shadow-2xl">
                <div className="relative h-52">
                  <img src="https://images.unsplash.com/photo-1590487817434-a35d1b7e7b85?w=600&h=400&fit=crop" className="w-full h-full object-cover" />
                  <div className="absolute inset-0 bg-gradient-to-t from-[#0d1117] via-transparent to-transparent"></div>
                  <div className="absolute top-5 left-5 flex items-center space-x-3 bg-black/40 backdrop-blur-md rounded-full pl-1 pr-4 py-1 border border-white/10">
                    <div className="w-8 h-8 rounded-full border border-white/20 overflow-hidden">
                      <img src="https://i.pravatar.cc/150?u=seller4" />
                    </div>
                    <span className="text-[10px] font-bold text-white uppercase tracking-wider">Calet Match</span>
                  </div>
                  <div className="absolute top-5 right-5">
                    <div className="bg-neon-emerald/20 backdrop-blur-md border border-neon-emerald/50 rounded-full px-3 py-1">
                      <span className="text-[9px] text-neon-emerald font-black tracking-widest uppercase">Verified</span>
                    </div>
                  </div>
                </div>
                <div className="p-7">
                  <div className="flex justify-between items-end mb-6">
                    <div>
                      <h3 className="text-2xl font-black text-white mb-1 font-orbitron tracking-tight">Lithium</h3>
                      <p className="text-[10px] text-gray-500 font-bold uppercase tracking-[0.2em]">Austro/Lithium</p>
                      <div className="text-2xl font-black text-white tracking-tighter mt-2">$1500</div>
                    </div>
                    <div className="text-right">
                      <div className="text-neon-emerald text-[10px] font-black tracking-widest flex items-center justify-end mb-1">
                        LIVE 20%
                      </div>
                      <div className="text-lg font-bold text-gray-500">$1884</div>
                    </div>
                  </div>
                  <Button variant="ghost" className="w-full h-12 rounded-xl text-[10px] font-black uppercase tracking-[0.2em] border border-white/10 hover:bg-white/5">View Full Marketplace</Button>
                </div>
              </div>

              {/* Negotiator Card */}
              <div className="bg-[#0d1117] border border-white/5 rounded-[2.5rem] overflow-hidden group hover:border-neon-emerald/30 transition-all duration-500 shadow-2xl relative">
                <div className="absolute inset-0 bg-gradient-to-b from-neon-emerald/5 to-transparent"></div>
                <div className="relative h-52 flex items-center justify-center">
                  <div className="relative z-10 w-28 h-28 rounded-2xl border-2 border-neon-emerald/30 flex items-center justify-center bg-neon-emerald/5 shadow-[0_0_50px_rgba(16,185,129,0.15)]">
                    <div className="grid grid-cols-2 gap-2 p-4">
                      {[1, 2, 3, 4].map(i => <div key={i} className="w-6 h-6 border border-neon-emerald/40 rounded-sm"></div>)}
                    </div>
                  </div>
                  <div className="absolute top-5 right-5">
                    <div className="bg-neon-emerald/20 backdrop-blur-md border border-neon-emerald/50 rounded-full px-3 py-1">
                      <span className="text-[9px] text-neon-emerald font-black tracking-widest uppercase">Verified</span>
                    </div>
                  </div>
                  <div className="absolute top-5 left-5 flex items-center space-x-3 bg-black/40 backdrop-blur-md rounded-full pl-1 pr-4 py-1 border border-white/10">
                    <div className="w-8 h-8 rounded-full border border-white/20 overflow-hidden">
                      <img src="https://i.pravatar.cc/150?u=seller5" />
                    </div>
                    <span className="text-[10px] font-bold text-white uppercase tracking-wider">Best Match</span>
                  </div>
                </div>
                <div className="p-7">
                  <h3 className="text-2xl font-black text-white mb-1 font-orbitron tracking-tight">Negotiator</h3>
                  <p className="text-[10px] text-gray-500 font-bold uppercase tracking-[0.1em] mb-4">Earn Commission Instantly<br/>Autonomous</p>
                  <div className="flex items-center space-x-2 mb-6">
                    <div className="px-2 py-1 rounded bg-white/5 border border-white/10 text-[8px] text-gray-400 font-black uppercase">Smart</div>
                    <div className="px-2 py-1 rounded bg-white/5 border border-white/10 text-[8px] text-gray-400 font-black uppercase">Contract</div>
                    <div className="px-2 py-1 rounded bg-white/5 border border-white/10 text-[8px] text-gray-400 font-black uppercase">Escrow</div>
                  </div>
                  <p className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Agentic AI Agents</p>
                </div>
              </div>

              {/* Chat Match Card */}
              <div className="bg-[#0d1117] border border-white/5 rounded-[2.5rem] overflow-hidden group hover:border-neon-gold/30 transition-all duration-500 shadow-2xl relative">
                <div className="absolute inset-0 bg-gradient-to-b from-neon-gold/5 to-transparent"></div>
                <div className="relative h-52 flex items-center justify-center">
                  <div className="flex space-x-4">
                    <div className="w-16 h-16 rounded-full bg-neon-cyan/20 blur-xl animate-pulse"></div>
                    <div className="w-16 h-16 rounded-full bg-neon-emerald/20 blur-xl animate-pulse delay-75"></div>
                    <div className="w-16 h-16 rounded-full bg-neon-gold/20 blur-xl animate-pulse delay-150"></div>
                  </div>
                  <div className="absolute top-5 right-5">
                    <div className="bg-neon-emerald/20 backdrop-blur-md border border-neon-emerald/50 rounded-full px-3 py-1">
                      <span className="text-[9px] text-neon-emerald font-black tracking-widest uppercase">Verified</span>
                    </div>
                  </div>
                  <div className="absolute top-5 left-5 flex items-center space-x-3 bg-black/40 backdrop-blur-md rounded-full pl-1 pr-4 py-1 border border-white/10">
                    <div className="w-8 h-8 rounded-full border border-white/20 overflow-hidden">
                      <img src="https://i.pravatar.cc/150?u=seller6" />
                    </div>
                    <span className="text-[10px] font-bold text-white uppercase tracking-wider">Chat Match</span>
                  </div>
                </div>
                <div className="p-7">
                  <div className="bg-neon-cyan/10 border border-neon-cyan/20 p-4 rounded-2xl mb-6">
                    <p className="text-[10px] text-neon-cyan font-bold uppercase tracking-widest mb-2">AI Suggestion</p>
                    <p className="text-xs text-gray-400 leading-relaxed italic">"Verified buyers from Dubai are looking for Gold. 14 matches ready."</p>
                  </div>
                  <Button variant="cyber" className="w-full h-12 rounded-xl text-[10px] font-black uppercase tracking-[0.2em]">Start Negotiation</Button>
                </div>
              </div>
            </div>
          </div>
        )
      case 'Wallet':
        return (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold text-white font-orbitron tracking-tight">DEDAN Smart Wallet</h2>
                <p className="text-gray-400 text-sm mt-1">Multi-currency institutional bridge with instant payouts</p>
              </div>
              <div className="flex space-x-2">
                <Button variant="ghost" size="sm" className="border border-white/10 text-[10px]">PAYONEER</Button>
                <Button variant="ghost" size="sm" className="border border-white/10 text-[10px]">MASTERCARD</Button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="glass-morphism border border-neon-gold/30 rounded-3xl p-8 bg-gradient-to-br from-neon-gold/5 to-transparent relative overflow-hidden">
                <div className="absolute top-0 right-0 p-4"><Wallet className="w-12 h-12 text-neon-gold opacity-10" /></div>
                <div className="relative z-10">
                  <p className="text-[10px] font-bold text-neon-gold uppercase tracking-widest mb-2">Total Balance</p>
                  <h3 className="text-4xl font-bold text-white mb-4">${walletBalance.toLocaleString()}</h3>
                  <div className="flex items-center space-x-2 text-neon-emerald text-xs">
                    <TrendingUp className="w-3 h-3" />
                    <span>+12.5% this month</span>
                  </div>
                </div>
              </div>
              <div className="glass-morphism border border-neon-emerald/30 rounded-3xl p-8 bg-gradient-to-br from-neon-emerald/5 to-transparent relative overflow-hidden">
                <div className="absolute top-0 right-0 p-4"><ShieldCheck className="w-12 h-12 text-neon-emerald opacity-10" /></div>
                <div className="relative z-10">
                  <p className="text-[10px] font-bold text-neon-emerald uppercase tracking-widest mb-2">Escrow Funds</p>
                  <h3 className="text-4xl font-bold text-white mb-4">$28,150.00</h3>
                  <p className="text-[10px] text-gray-500">Secured in multi-sig contract</p>
                </div>
              </div>
              <div className="glass-morphism border border-neon-cyan/30 rounded-3xl p-8 bg-gradient-to-br from-neon-cyan/5 to-transparent relative overflow-hidden">
                <div className="absolute top-0 right-0 p-4"><Zap className="w-12 h-12 text-neon-cyan opacity-10" /></div>
                <div className="relative z-10">
                  <p className="text-[10px] font-bold text-neon-cyan uppercase tracking-widest mb-2">Pending Commissions</p>
                  <h3 className="text-4xl font-bold text-white mb-4">${pendingCommission.toLocaleString()}</h3>
                  
                  {showWithdrawSuccess && (
                    <div className="absolute top-0 left-0 w-full h-full bg-cyber-dark/90 backdrop-blur-sm flex flex-center items-center justify-center animate-in fade-in zoom-in duration-300 z-20">
                      <div className="text-center">
                        <ShieldCheck className="w-10 h-10 text-neon-emerald mx-auto mb-2" />
                        <p className="text-xs font-bold text-neon-emerald uppercase tracking-widest">Withdrawal Success!</p>
                      </div>
                    </div>
                  )}

                  <Button 
                    variant="cyber" 
                    className={`w-full mt-4 h-9 text-[10px] uppercase font-bold transition-all ${pendingCommission <= 0 ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105 active:scale-95'}`}
                    onClick={handleWithdraw}
                    disabled={pendingCommission <= 0}
                  >
                    {pendingCommission > 0 ? 'Withdraw Now' : 'No Funds Available'}
                  </Button>
                </div>
              </div>
            </div>

            <div className="glass-morphism border border-white/10 rounded-2xl overflow-hidden">
              <div className="p-6 border-b border-white/10 flex justify-between items-center">
                <h3 className="text-lg font-bold text-white">Recent Transactions</h3>
                <Button variant="ghost" size="sm" className="text-[10px] uppercase">Export PDF</Button>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead>
                    <tr className="text-[10px] text-gray-500 border-b border-white/5 uppercase">
                      <th className="px-6 py-4">Transaction ID</th>
                      <th className="px-6 py-4">Commodity</th>
                      <th className="px-6 py-4">Amount</th>
                      <th className="px-6 py-4">Commission</th>
                      <th className="px-6 py-4">Status</th>
                    </tr>
                  </thead>
                  <tbody className="text-xs text-gray-300">
                    {transactions.length > 0 ? (
                      transactions.map((txn) => (
                        <tr key={txn.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                          <td className="px-6 py-4 font-mono">{txn.id}</td>
                          <td className="px-6 py-4">{txn.listingTitle}</td>
                          <td className="px-6 py-4">${txn.amount.toLocaleString()}</td>
                          <td className="px-6 py-4 text-neon-emerald">+${txn.commission.toLocaleString()}</td>
                          <td className="px-6 py-4">
                            <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${
                              txn.status === 'Completed' 
                                ? 'bg-neon-emerald/10 border-neon-emerald/30 text-neon-emerald' 
                                : txn.status === 'Pending'
                                ? 'bg-neon-gold/10 border-neon-gold/30 text-neon-gold'
                                : 'bg-neon-cyan/10 border-neon-cyan/30 text-neon-cyan'
                            }`}>
                              {txn.status.toUpperCase()}
                            </span>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                          <div className="flex flex-col items-center">
                            <Clock className="w-8 h-8 mb-2 opacity-20" />
                            <p>No transaction history found in secure database.</p>
                          </div>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )
      case 'Home':
      default:
        return (
          <div className="space-y-12 animate-in fade-in duration-1000">
            {/* Earning Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="glass-morphism border border-neon-cyan/20 rounded-3xl p-8 bg-gradient-to-br from-neon-cyan/5 to-transparent relative group">
                <div className="absolute inset-0 bg-neon-cyan/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
                <div className="relative z-10">
                  <div className="w-12 h-12 bg-neon-cyan/20 rounded-2xl flex items-center justify-center mb-6 shadow-[0_0_20px_rgba(0,255,255,0.2)]">
                    <Zap className="w-6 h-6 text-neon-cyan" />
                  </div>
                  <h2 className="text-3xl font-bold text-white font-orbitron mb-4 leading-tight">
                    How to Earn <br/><span className="text-neon-cyan">with DEDAN AI</span>
                  </h2>
                  <div className="space-y-4 mb-8">
                    {[
                      'Register as a verified agent (Seller or Buyer)',
                      'AI matches you with high-value mining contracts',
                      'Execute smart contracts via secure escrow',
                      'Earn 2% instant commission on every deal'
                    ].map((text, i) => (
                      <div key={i} className="flex items-start space-x-3">
                        <ShieldCheck className="w-5 h-5 text-neon-emerald mt-0.5" />
                        <p className="text-gray-300 text-sm leading-relaxed">{text}</p>
                      </div>
                    ))}
                  </div>
                  <Button variant="cyber" className="w-full h-12 font-bold group" onClick={() => setActiveTab('Marketplace')}>
                    Start Trading Now
                    <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                  </Button>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="glass-morphism border border-white/10 rounded-2xl p-6 flex flex-col justify-between hover:border-neon-gold/50 transition-all cursor-pointer group">
                  <div className="w-10 h-10 bg-neon-gold/20 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <DollarSign className="w-5 h-5 text-neon-gold" />
                  </div>
                  <div>
                    <h3 className="text-white font-bold mb-1">Instant Payouts</h3>
                    <p className="text-xs text-gray-500">Commission is paid directly to your wallet upon contract fulfillment.</p>
                  </div>
                </div>
                <div className="glass-morphism border border-white/10 rounded-2xl p-6 flex flex-col justify-between hover:border-neon-emerald/50 transition-all cursor-pointer group">
                  <div className="w-10 h-10 bg-neon-emerald/20 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <ShieldCheck className="w-5 h-5 text-neon-emerald" />
                  </div>
                  <div>
                    <h3 className="text-white font-bold mb-1">Escrow Protection</h3>
                    <p className="text-xs text-gray-500">Zero-risk environment with multi-sig smart contract protection.</p>
                  </div>
                </div>
                <div className="glass-morphism border border-white/10 rounded-2xl p-6 flex flex-col justify-between col-span-1 sm:col-span-2 hover:border-neon-cyan/50 transition-all cursor-pointer group">
                  <div className="w-10 h-10 bg-neon-cyan/20 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <BrainCircuit className="w-5 h-5 text-neon-cyan" />
                  </div>
                  <div className="flex justify-between items-end">
                    <div>
                      <h3 className="text-white font-bold mb-1">AI-Powered Optimization</h3>
                      <p className="text-xs text-gray-500">Let our agents find the best prices and reliable partners for you.</p>
                    </div>
                    <Button variant="ghost" size="sm" className="h-8 text-[10px] border border-white/10 hover:bg-neon-cyan/10">Configure AI</Button>
                  </div>
                </div>
              </div>
            </div>

            {/* Marketplace Preview */}
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-white font-orbitron">Trending Deals</h2>
                <Button variant="ghost" className="text-xs text-gray-500 hover:text-white" onClick={() => setActiveTab('Marketplace')}>View All Deals</Button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {listings.slice(0, 3).map((listing) => (
                  <ListingCard key={listing.id} listing={listing} />
                ))}
              </div>
            </div>
          </div>
        )
    }
  }

  return (
    <div className="flex-1 p-6 overflow-y-auto scrollbar-hide">
      {/* Hero Section */}
      <div className="mb-12 animate-in fade-in zoom-in-95 duration-1000">
        <div className="glass-morphism border border-glass-white/20 rounded-3xl p-10 text-left relative overflow-hidden bg-gradient-to-r from-cyber-navy to-transparent">
          <div className="relative z-10">
            <div className="flex items-center space-x-2 mb-6">
              <h1 className="text-6xl font-bold text-white font-orbitron tracking-tighter drop-shadow-2xl">
                Agentic
              </h1>
              <div className="flex items-center space-x-2 bg-cyber-dark/60 border border-glass-white/20 rounded-xl px-4 py-2 cursor-pointer hover:border-neon-cyan/50 transition-colors group">
                <Search className="w-4 h-4 text-gray-400 group-hover:text-neon-cyan" />
                <span className="text-sm text-gray-400">Search Mines...</span>
                <ChevronDown className="w-4 h-4 text-gray-400" />
              </div>
            </div>
            <p className="text-xl text-gray-300 max-w-2xl leading-relaxed mb-8">
              AI Autonomous Marketplace — Buyers & Sellers Matched 24/7<br />
              <span className="text-gray-500 text-lg">• Smart Contracts • Secure Escrow • Instant Commissions</span>
            </p>
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-2 bg-neon-emerald/10 border border-neon-emerald/30 rounded-full px-4 py-1.5">
                <div className="w-2 h-2 bg-neon-emerald rounded-full animate-pulse"></div>
                <span className="text-xs text-neon-emerald font-bold uppercase tracking-widest">Network Secure</span>
              </div>
              <div className="flex items-center space-x-4 text-gray-500 text-sm">
                <div className="flex items-center space-x-1"><ShieldCheck className="w-4 h-4" /> <span>Verified Partners: 1.2k+</span></div>
                <span className="w-1 h-1 bg-gray-700 rounded-full"></span>
                <div className="flex items-center space-x-1"><LayoutGrid className="w-4 h-4" /> <span>Active Nodes: 124</span></div>
              </div>
            </div>
          </div>
          
          {/* Decorative background element */}
          <div className="absolute top-0 right-0 w-2/3 h-full bg-[radial-gradient(circle_at_70%_50%,rgba(0,255,255,0.1),transparent_70%)] pointer-events-none animate-pulse"></div>
        </div>
      </div>

      {renderContent()}
    </div>
  )
}

export default MainContent
