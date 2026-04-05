/**
 * Adaptive Guardian Orb Component - DEDAN Mine
 * 3D gold orb animation that adapts to bandwidth constraints
 * Maintains ZK-Auth functionality while optimizing performance
 */

import React, { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useBandwidthAdaptive } from './BandwidthAdaptiveUI';

interface GuardianOrbProps {
  state: 'idle' | 'scanning' | 'verified' | 'alert';
  size?: number;
  className?: string;
}

const AdaptiveGuardianOrb: React.FC<GuardianOrbProps> = ({
  state,
  size = 120,
  className = ''
}) => {
  const { uiConfig, isHighEfficiency } = useBandwidthAdaptive();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();
  const [isClient, setIsClient] = useState(false);

  // Guardian orb states configuration
  const orbStates = {
    idle: {
      color: '#FFD700',      // Gold
      pulse: 'slow',
      rotation: 'steady',
      glow: 0.3,
      particles: isHighEfficiency ? 0 : 20
    },
    scanning: {
      color: '#FFA500',      // Orange
      pulse: 'medium',
      rotation: 'clockwise',
      glow: 0.6,
      particles: isHighEfficiency ? 5 : 30
    },
    verified: {
      color: '#00FF00',      // Green
      pulse: 'fast',
      rotation: 'burst',
      glow: 0.9,
      particles: isHighEfficiency ? 10 : 50
    },
    alert: {
      color: '#FF0000',      // Red
      pulse: 'rapid',
      rotation: 'erratic',
      glow: 1.0,
      particles: isHighEfficiency ? 15 : 40
    }
  };

  const currentConfig = orbStates[state];

  // Animation variants for different bandwidth modes
  const getAnimationVariants = () => {
    if (isHighEfficiency) {
      return {
        initial: { scale: 1, opacity: 1 },
        animate: { 
          scale: [1, 1.05, 1], 
          opacity: [0.8, 1, 0.8],
          transition: { 
            duration: 2, 
            repeat: Infinity,
            ease: "easeInOut"
          }
        }
      };
    }

    return {
      initial: { scale: 0.8, opacity: 0 },
      animate: { 
        scale: 1, 
        opacity: 1,
        transition: { 
          duration: 0.5,
          ease: "easeOut"
        }
      }
    };
  };

  // Canvas-based 3D rendering (only in full mode)
  useEffect(() => {
    setIsClient(true);
    
    if (isHighEfficiency || !canvasRef.current) {
      return;
    }

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let time = 0;
    const particles: Array<{
      x: number;
      y: number;
      vx: number;
      vy: number;
      size: number;
      life: number;
    }> = [];

    // Initialize particles
    for (let i = 0; i < currentConfig.particles; i++) {
      particles.push({
        x: Math.random() * size,
        y: Math.random() * size,
        vx: (Math.random() - 0.5) * 2,
        vy: (Math.random() - 0.5) * 2,
        size: Math.random() * 3 + 1,
        life: 1
      });
    }

    const animate = () => {
      ctx.clearRect(0, 0, size, size);
      
      // Draw orb
      const gradient = ctx.createRadialGradient(size/2, size/2, 0, size/2, size/2, size/2);
      gradient.addColorStop(0, currentConfig.color + 'FF');
      gradient.addColorStop(0.5, currentConfig.color + '88');
      gradient.addColorStop(1, currentConfig.color + '00');
      
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(size/2, size/2, size/2, 0, Math.PI * 2);
      ctx.fill();

      // Draw glow effect
      ctx.shadowBlur = 20 * currentConfig.glow;
      ctx.shadowColor = currentConfig.color;
      ctx.beginPath();
      ctx.arc(size/2, size/2, size/2 * 0.8, 0, Math.PI * 2);
      ctx.fill();

      // Draw particles
      particles.forEach((particle, index) => {
        particle.x += particle.vx;
        particle.y += particle.vy;
        particle.life -= 0.01;

        if (particle.life <= 0) {
          particles[index] = {
            x: size/2,
            y: size/2,
            vx: (Math.random() - 0.5) * 4,
            vy: (Math.random() - 0.5) * 4,
            size: Math.random() * 3 + 1,
            life: 1
          };
        }

        ctx.fillStyle = currentConfig.color + Math.floor(particle.life * 255).toString(16).padStart(2, '0');
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
        ctx.fill();
      });

      time += 0.016;
      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [state, size, isHighEfficiency, currentConfig]);

  // High-efficiency mode (CSS-based animation)
  const renderHighEfficiencyOrb = () => {
    const pulseAnimation = {
      idle: { scale: [1, 1.02, 1], opacity: [0.9, 1, 0.9] },
      scanning: { scale: [1, 1.05, 1], opacity: [0.8, 1, 0.8] },
      verified: { scale: [1, 1.1, 1], opacity: [0.7, 1, 0.7] },
      alert: { scale: [1, 1.08, 1], opacity: [0.6, 1, 0.6] }
    };

    return (
      <motion.div
        className={`guardian-orb high-efficiency ${state}`}
        style={{
          width: size,
          height: size,
          backgroundColor: currentConfig.color,
          borderRadius: '50%',
          boxShadow: `0 0 ${20 * currentConfig.glow}px ${currentConfig.color}`,
          position: 'relative'
        }}
        animate={pulseAnimation[state]}
        transition={{
          duration: state === 'verified' ? 1 : 2,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      >
        {/* Simple pulse ring */}
        <motion.div
          className="pulse-ring"
          style={{
            position: 'absolute',
            top: -10,
            left: -10,
            right: -10,
            bottom: -10,
            border: `2px solid ${currentConfig.color}`,
            borderRadius: '50%',
            opacity: 0.5
          }}
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.5, 0, 0.5]
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeOut"
          }}
        />
      </motion.div>
    );
  };

  // Full 3D mode (Canvas-based)
  const renderFullOrb = () => {
    if (!isClient) {
      // Fallback for SSR
      return (
        <div
          className={`guardian-orb ssr-fallback ${state}`}
          style={{
            width: size,
            height: size,
            backgroundColor: currentConfig.color,
            borderRadius: '50%',
            boxShadow: `0 0 20px ${currentConfig.color}`
          }}
        />
      );
    }

    return (
      <motion.div
        className={`guardian-orb full-3d ${state}`}
        variants={getAnimationVariants()}
        initial="initial"
        animate="animate"
        style={{
          width: size,
          height: size,
          position: 'relative'
        }}
      >
        <canvas
          ref={canvasRef}
          width={size}
          height={size}
          style={{
            borderRadius: '50%',
            position: 'absolute',
            top: 0,
            left: 0
          }}
        />
        
        {/* ZK-Auth indicator (always visible) */}
        <motion.div
          className="zk-auth-indicator"
          style={{
            position: 'absolute',
            top: size - 20,
            left: size - 20,
            width: 16,
            height: 16,
            backgroundColor: '#00FF00',
            borderRadius: '50%',
            boxShadow: '0 0 10px #00FF00'
          }}
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.8, 1, 0.8]
          }}
          transition={{
            duration: 1,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      </motion.div>
    );
  };

  return (
    <AnimatePresence mode="wait">
      <motion.div
        className={`adaptive-guardian-orb ${className}`}
        style={{
          width: size,
          height: size,
          position: 'relative'
        }}
        key={`${state}-${uiConfig.mode}`}
      >
        {isHighEfficiency ? renderHighEfficiencyOrb() : renderFullOrb()}
        
        {/* Status label */}
        <motion.div
          className="orb-status"
          style={{
            position: 'absolute',
            bottom: -25,
            left: 0,
            right: 0,
            textAlign: 'center',
            fontSize: '12px',
            color: currentConfig.color,
            fontWeight: 'bold',
            textTransform: 'uppercase'
          }}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          {state}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default AdaptiveGuardianOrb;
