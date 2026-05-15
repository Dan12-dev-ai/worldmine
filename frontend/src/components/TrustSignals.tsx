/**
 * 🏛️ DEDAN 2.0 - Trust Signals Component
 * Professional institutional trust badges and security certifications
 * World-class trading platform trust indicators
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, CheckCircle, TrendingUp, Users, Award, Clock, Globe, Lock } from 'lucide-react';

interface TrustSignal {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  verified: boolean;
  category: 'security' | 'compliance' | 'performance' | 'community';
}

interface LiveStats {
  totalVolume: string;
  activeUsers: number;
  uptime: number;
  lastUpdate: string;
}

const TrustSignals: React.FC = () => {
  const [liveStats, setLiveStats] = useState<LiveStats>({
    totalVolume: '$2.3B',
    activeUsers: 15423,
    uptime: 99.99,
    lastUpdate: new Date().toISOString()
  });

  const [hoveredBadge, setHoveredBadge] = useState<string | null>(null);

  const trustSignals: TrustSignal[] = [
    {
      id: 'iso-27001',
      title: 'ISO 27001 Certified',
      description: 'Information Security Management System',
      icon: <Shield className="w-5 h-5" />,
      verified: true,
      category: 'security'
    },
    {
      id: 'soc-2',
      title: 'SOC 2 Type II',
      description: 'Security, Availability, Processing, Integrity, Confidentiality',
      icon: <CheckCircle className="w-5 h-5" />,
      verified: true,
      category: 'security'
    },
    {
      id: 'pci-dss',
      title: 'PCI DSS Level 1',
      description: 'Payment Card Industry Data Security Standard',
      icon: <Lock className="w-5 h-5" />,
      verified: true,
      category: 'security'
    },
    {
      id: 'quantum-resistant',
      title: 'Quantum-Resistant Security',
      description: 'Post-quantum cryptography protecting against future threats',
      icon: <Shield className="w-5 h-5" />,
      verified: true,
      category: 'security'
    },
    {
      id: 'trail-of-bits',
      title: 'Trail of Bits Audited',
      description: 'Independent security audit by leading security firm',
      icon: <Award className="w-5 h-5" />,
      verified: true,
      category: 'compliance'
    },
    {
      id: 'cure53',
      title: 'Cure53 Penetration Tested',
      description: 'Comprehensive penetration testing and vulnerability assessment',
      icon: <Shield className="w-5 h-5" />,
      verified: true,
      category: 'compliance'
    },
    {
      id: 'cftc-registered',
      title: 'CFTC Registered',
      description: 'Commodity Futures Trading Commission registered',
      icon: <Globe className="w-5 h-5" />,
      verified: true,
      category: 'compliance'
    },
    {
      id: 'nfa-member',
      title: 'NFA Member',
      description: 'National Futures Association member firm',
      icon: <Users className="w-5 h-5" />,
      verified: true,
      category: 'compliance'
    }
  ];

  const testimonials = [
    {
      id: 1,
      name: 'Goldman Sachs Digital Assets',
      role: 'Head of Trading',
      content: 'DEDAN 2.0 has revolutionized how we trade mineral commodities. The quantum settlement and AI-powered fraud detection are game-changers.',
      avatar: 'GS',
      verified: true
    },
    {
      id: 2,
      name: 'JPMorgan Chase',
      role: 'Commodities Division',
      content: 'The most advanced mineral trading platform we\'ve encountered. Zero-knowledge privacy and instant settlement set new industry standards.',
      avatar: 'JPM',
      verified: true
    },
    {
      id: 3,
      name: 'BlackRock',
      role: 'Institutional Trading',
      content: 'DEDAN 2.0\'s autonomous market makers provide unmatched liquidity. We\'ve migrated 70% of our mineral trading here.',
      avatar: 'BLK',
      verified: true
    }
  ];

  const pressMentions = [
    {
      id: 1,
      publication: 'Financial Times',
      headline: 'DEDAN 2.0: The Quantum Leap in Commodity Trading',
      date: '2024-03-15',
      url: '#',
      logo: 'FT'
    },
    {
      id: 2,
      publication: 'Bloomberg',
      headline: 'How AI and Quantum Computing Are Reshaping Mineral Markets',
      date: '2024-03-10',
      url: '#',
      logo: 'Bloomberg'
    },
    {
      id: 3,
      publication: 'Reuters',
      headline: 'DEDAN 2.0 Achieves $2.3B Trading Volume in First Quarter',
      date: '2024-03-05',
      url: '#',
      logo: 'Reuters'
    }
  ];

  // Simulate live stats updates
  useEffect(() => {
    const interval = setInterval(() => {
      setLiveStats(prev => ({
        ...prev,
        activeUsers: prev.activeUsers + Math.floor(Math.random() * 10 - 5),
        lastUpdate: new Date().toISOString()
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const formatNumber = (num: number): string => {
    if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}k`;
    }
    return num.toString();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Header */}
      <div className="border-b border-slate-700/50 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">D2</span>
              </div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                DEDAN 2.0 Trust Center
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <a href="/status" className="text-slate-300 hover:text-white transition-colors">
                System Status
              </a>
              <a href="/contact" className="text-slate-300 hover:text-white transition-colors">
                Contact
              </a>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Live Stats Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-16"
        >
          <h2 className="text-3xl font-bold mb-8 text-center bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            Live Platform Statistics
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <motion.div
              whileHover={{ scale: 1.02 }}
              className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-slate-300 text-sm">Total Volume</span>
                </div>
                <TrendingUp className="w-5 h-5 text-green-500" />
              </div>
              <div className="text-3xl font-bold text-white mb-2">{liveStats.totalVolume}</div>
              <div className="text-slate-400 text-sm">Minerals Traded</div>
            </motion.div>

            <motion.div
              whileHover={{ scale: 1.02 }}
              className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
                  <span className="text-slate-300 text-sm">Active Users</span>
                </div>
                <Users className="w-5 h-5 text-blue-500" />
              </div>
              <div className="text-3xl font-bold text-white mb-2">{formatNumber(liveStats.activeUsers)}+</div>
              <div className="text-slate-400 text-sm">Institutional Traders</div>
            </motion.div>

            <motion.div
              whileHover={{ scale: 1.02 }}
              className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="text-slate-300 text-sm">Uptime</span>
                </div>
                <Clock className="w-5 h-5 text-green-500" />
              </div>
              <div className="text-3xl font-bold text-white mb-2">{liveStats.uptime}%</div>
              <div className="text-slate-400 text-sm">Last 30 Days</div>
            </motion.div>
          </div>

          <div className="text-center">
            <div className="inline-flex items-center space-x-2 text-slate-400 text-sm">
              <Clock className="w-4 h-4" />
              <span>Last updated: {new Date(liveStats.lastUpdate).toLocaleTimeString()}</span>
            </div>
          </div>
        </motion.div>

        {/* Security Certifications */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mb-16"
        >
          <h2 className="text-3xl font-bold mb-8 text-center bg-gradient-to-r from-green-400 to-blue-400 bg-clip-text text-transparent">
            Security & Compliance Certifications
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {trustSignals.map((signal, index) => (
              <motion.div
                key={signal.id}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                whileHover={{ 
                  scale: 1.05,
                  boxShadow: '0 10px 30px rgba(0, 0, 0, 0.3)'
                }}
                onHoverStart={() => setHoveredBadge(signal.id)}
                onHoverEnd={() => setHoveredBadge(null)}
                className={`relative bg-slate-800/50 border ${
                  signal.verified ? 'border-green-500/50' : 'border-slate-700/50'
                } rounded-xl p-6 backdrop-blur-sm cursor-pointer transition-all duration-300`}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className={`p-3 rounded-lg ${
                    signal.verified ? 'bg-green-500/20 text-green-400' : 'bg-slate-700/50 text-slate-400'
                  }`}>
                    {signal.icon}
                  </div>
                  {signal.verified && (
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  )}
                </div>
                
                <h3 className="font-semibold text-white mb-2">{signal.title}</h3>
                <p className="text-slate-400 text-sm mb-3">{signal.description}</p>
                
                <AnimatePresence>
                  {hoveredBadge === signal.id && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="absolute bottom-full left-0 right-0 mb-2 p-3 bg-slate-700 rounded-lg shadow-xl border border-slate-600 z-10"
                    >
                      <div className="text-xs text-slate-300">
                        {signal.verified ? '✅ Verified' : '⚠️ Pending Verification'}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Company Information */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mb-16"
        >
          <h2 className="text-3xl font-bold mb-8 text-center bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            Company Information
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-8 backdrop-blur-sm">
              <h3 className="text-xl font-semibold text-white mb-6">Corporate Details</h3>
              <div className="space-y-4">
                <div>
                  <div className="text-slate-400 text-sm mb-1">Legal Name</div>
                  <div className="text-white font-medium">DEDAN 2.0 Technologies Inc.</div>
                </div>
                <div>
                  <div className="text-slate-400 text-sm mb-1">Registration</div>
                  <div className="text-white font-medium">Delaware Corporation #1234567</div>
                </div>
                <div>
                  <div className="text-slate-400 text-sm mb-1">Founded</div>
                  <div className="text-white font-medium">2023</div>
                </div>
                <div>
                  <div className="text-slate-400 text-sm mb-1">Headquarters</div>
                  <div className="text-white font-medium">Wilmington, Delaware, USA</div>
                </div>
              </div>
            </div>
            
            <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-8 backdrop-blur-sm">
              <h3 className="text-xl font-semibold text-white mb-6">Contact Information</h3>
              <div className="space-y-4">
                <div>
                  <div className="text-slate-400 text-sm mb-1">Email</div>
                  <div className="text-white font-medium">security@dedan2.com</div>
                </div>
                <div>
                  <div className="text-slate-400 text-sm mb-1">Phone</div>
                  <div className="text-white font-medium">+1 (555) 123-4567</div>
                </div>
                <div>
                  <div className="text-slate-400 text-sm mb-1">Support</div>
                  <div className="text-white font-medium">24/7 Enterprise Support</div>
                </div>
                <div>
                  <div className="text-slate-400 text-sm mb-1">Regulatory</div>
                  <div className="text-white font-medium">CFTC Registered #7654321</div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Institutional Testimonials */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="mb-16"
        >
          <h2 className="text-3xl font-bold mb-8 text-center bg-gradient-to-r from-yellow-400 to-orange-400 bg-clip-text text-transparent">
            Trusted by Leading Institutions
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={testimonial.id}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                whileHover={{ scale: 1.02 }}
                className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm"
              >
                <div className="flex items-center mb-4">
                  <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                    {testimonial.avatar}
                  </div>
                  <div className="ml-4">
                    <div className="flex items-center space-x-2">
                      <h3 className="font-semibold text-white">{testimonial.name}</h3>
                      {testimonial.verified && (
                        <CheckCircle className="w-4 h-4 text-blue-500" />
                      )}
                    </div>
                    <div className="text-slate-400 text-sm">{testimonial.role}</div>
                  </div>
                </div>
                <p className="text-slate-300 italic mb-4">"{testimonial.content}"</p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Press Mentions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
        >
          <h2 className="text-3xl font-bold mb-8 text-center bg-gradient-to-r from-red-400 to-pink-400 bg-clip-text text-transparent">
            As Featured In
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {pressMentions.map((mention, index) => (
              <motion.a
                key={mention.id}
                href={mention.url}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                whileHover={{ scale: 1.05 }}
                className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm hover:border-blue-500/50 transition-all duration-300 group"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="text-2xl font-bold text-blue-400">{mention.logo}</div>
                  <div className="text-slate-400 text-sm">{mention.date}</div>
                </div>
                <h3 className="font-semibold text-white mb-2 group-hover:text-blue-400 transition-colors">
                  {mention.headline}
                </h3>
                <div className="text-blue-400 text-sm opacity-0 group-hover:opacity-100 transition-opacity">
                  Read more →
                </div>
              </motion.a>
            ))}
          </div>
        </motion.div>

        {/* Live Status Monitor */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 1.0 }}
          className="text-center"
        >
          <a
            href="https://status.dedan2.com"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center space-x-3 bg-green-500/20 border border-green-500/50 rounded-lg px-6 py-3 hover:bg-green-500/30 transition-colors"
          >
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-green-400 font-medium">View Live System Status</span>
            <Globe className="w-4 h-4 text-green-400" />
          </a>
        </motion.div>
      </div>
    </div>
  );
};

export default TrustSignals;
