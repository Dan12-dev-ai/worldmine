import React, { useEffect, useRef } from 'react'

const BackgroundParticles: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    canvas.width = window.innerWidth
    canvas.height = window.innerHeight

    const particles: Array<{
      x: number
      y: number
      vx: number
      vy: number
      size: number
      opacity: number
    }> = []

    // Create particles
    for (let i = 0; i < 150; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() + 0.1) * 0.8, // Wind-swept effect to the right
        vy: (Math.random() - 0.5) * 0.2,
        size: Math.random() * 1.5 + 0.5,
        opacity: Math.random() * 0.4 + 0.1
      })
    }

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      
      // Draw volumetric glow spots
      const gradients = [
        { x: canvas.width * 0.2, y: canvas.height * 0.3, r: 300, c: 'rgba(0, 255, 255, 0.03)' },
        { x: canvas.width * 0.8, y: canvas.height * 0.7, r: 400, c: 'rgba(16, 185, 129, 0.03)' },
        { x: canvas.width * 0.5, y: canvas.height * 0.5, r: 500, c: 'rgba(255, 160, 0, 0.02)' }
      ]

      gradients.forEach(g => {
        const rad = ctx.createRadialGradient(g.x, g.y, 0, g.x, g.y, g.r)
        rad.addColorStop(0, g.c)
        rad.addColorStop(1, 'transparent')
        ctx.fillStyle = rad
        ctx.fillRect(0, 0, canvas.width, canvas.height)
      })

      particles.forEach((particle) => {
        // Update position
        particle.x += particle.vx
        particle.y += particle.vy

        // Wrap around edges
        if (particle.x > canvas.width) particle.x = 0
        if (particle.y < 0) particle.y = canvas.height
        if (particle.y > canvas.height) particle.y = 0

        // Draw particle with trail effect
        ctx.beginPath()
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(0, 255, 255, ${particle.opacity})`
        ctx.shadowBlur = 5
        ctx.shadowColor = '#00ffff'
        ctx.fill()
        ctx.shadowBlur = 0
      })

      // Draw connections
      particles.forEach((particle, i) => {
        particles.slice(i + 1).forEach((otherParticle) => {
          const dx = particle.x - otherParticle.x
          const dy = particle.y - otherParticle.y
          const distance = Math.sqrt(dx * dx + dy * dy)

          if (distance < 100) {
            ctx.beginPath()
            ctx.moveTo(particle.x, particle.y)
            ctx.lineTo(otherParticle.x, otherParticle.y)
            ctx.strokeStyle = `rgba(0, 255, 255, ${0.1 * (1 - distance / 100)})`
            ctx.stroke()
          }
        })
      })

      requestAnimationFrame(animate)
    }

    animate()

    const handleResize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-0"
      style={{ background: 'transparent' }}
    />
  )
}

export default BackgroundParticles
