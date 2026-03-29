import React from 'react'
import { cn } from '../utils/cn'

interface DedanLogoProps {
  className?: string
}

const DedanLogo: React.FC<DedanLogoProps> = ({ className }) => {
  return (
    <div className={cn("flex items-center space-x-5", className)}>
      {/* High-End 3D Metallic Shield Logo */}
      <div className="relative w-16 h-16 group">
        <div className="absolute inset-0 bg-neon-cyan/10 blur-2xl rounded-full animate-pulse"></div>
        <svg viewBox="0 0 100 100" className="w-full h-full drop-shadow-[0_10px_20px_rgba(0,0,0,0.5)]">
          <defs>
            <linearGradient id="shieldSilver" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#ffffff" />
              <stop offset="25%" stopColor="#e2e8f0" />
              <stop offset="50%" stopColor="#94a3b8" />
              <stop offset="75%" stopColor="#475569" />
              <stop offset="100%" stopColor="#1e293b" />
            </linearGradient>
            <linearGradient id="shieldGold" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#fde047" />
              <stop offset="50%" stopColor="#ca8a04" />
              <stop offset="100%" stopColor="#854d0e" />
            </linearGradient>
            <filter id="bevel" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur in="SourceAlpha" stdDeviation="3" result="blur" />
              <feSpecularLighting in="blur" surfaceScale="5" specularConstant="0.75" specularExponent="20" lightingColor="#ffffff" result="specOut">
                <fePointLight x="-5000" y="-10000" z="20000" />
              </feSpecularLighting>
              <feComposite in="specOut" in2="SourceAlpha" operator="in" result="specOut" />
              <feComposite in="SourceGraphic" in2="specOut" operator="arithmetic" k1="0" k2="1" k3="1" k4="0" />
            </filter>
            <filter id="glow">
              <feGaussianBlur stdDeviation="2.5" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
          
          {/* Base Shield with high-contrast metallic effect */}
          <path d="M50 5 L85 20 L85 55 C85 75 70 90 50 95 C30 90 15 75 15 55 L15 20 Z" fill="url(#shieldSilver)" filter="url(#bevel)" />
          
          {/* Gold Border with glow */}
          <path d="M50 8 L82 22 L82 54 C82 72 69 87 50 92 C31 87 18 72 18 54 L18 22 Z" fill="none" stroke="url(#shieldGold)" strokeWidth="4" filter="url(#glow)" />
          
          {/* Pickaxe and Excavator Icon Simplified for 3D feel */}
          <g transform="translate(35, 30) scale(0.6)">
            <path d="M25 0 L30 0 L30 50 L25 50 Z" fill="url(#shieldGold)" transform="rotate(-45 25 25)" />
            <path d="M0 10 Q 25 -5 50 10 L 45 15 Q 25 5 5 15 Z" fill="url(#shieldGold)" transform="rotate(-45 25 25)" />
            <path d="M40 20 L60 10 L70 15 L50 25 Z" fill="#495057" />
          </g>
          
          {/* Golden Sparkles */}
          <circle cx="25" cy="20" r="1.5" fill="#FFD700" className="animate-pulse" />
          <circle cx="75" cy="25" r="1" fill="#FFD700" className="animate-pulse delay-75" />
          <circle cx="50" cy="40" r="1.2" fill="#FFD700" className="animate-pulse delay-150" />
        </svg>
      </div>
      
      {/* 3D Silver Text DEDAN */}
      <div className="flex flex-col">
        <h1 className="font-orbitron text-5xl font-black tracking-tighter leading-none">
          <span className="bg-clip-text text-transparent bg-gradient-to-b from-white via-gray-300 to-gray-600 drop-shadow-[0_5px_10px_rgba(0,0,0,0.8)]">
            DEDAN
          </span>
        </h1>
        <p className="text-xs font-black tracking-[0.3em] text-neon-gold drop-shadow-[0_0_8px_rgba(255,215,0,0.4)] mt-1 ml-1 uppercase">
          — QUALITY IN ACTION —
        </p>
      </div>
    </div>
  )
}

export default DedanLogo
