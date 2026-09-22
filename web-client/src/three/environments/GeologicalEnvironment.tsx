/**
 * World Mine — shared 3D environment (§9/§10).
 * Layered canvases: slow particle field + abstract mineral terrain + vignette.
 * NEVER blocks first paint (lazy-loaded), capability-gated, reduced-motion
 * aware, pauses on hidden tab, disposes on unmount.
 * Falls back to a pure-CSS/canvas atmosphere when WebGL is unavailable (§9 fallback chain).
 */
import { useEffect, useMemo, useRef, useState } from 'react';

type Quality = 'high' | 'medium' | 'low';

function detectQuality(): Quality {
  if (typeof window === 'undefined') return 'low';
  if (window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) return 'low';
  const cores = navigator.hardwareConcurrency ?? 4;
  if (cores >= 8 && window.innerWidth > 900) return 'high';
  if (cores >= 4) return 'medium';
  return 'low';
}

/* CSS atmosphere — the always-available fallback layer (also the pre-3D base). */
function GeologicalAtmosphere() {
  return (
    <div className="wm-geo-atmosphere" aria-hidden="true">
      <div className="wm-geo-layer wm-geo-layer--far" />
      <div style={{
        position: 'absolute', inset: 0,
        background: 'radial-gradient(1000px 480px at 78% 18%, rgba(201,162,39,0.14), transparent 60%)',
      }} />
    </div>
  );
}

function ParticleField({ quality }: { quality: Quality }) {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    let raf = 0;
    let running = true;

    const resize = () => {
      canvas.width = canvas.clientWidth * dpr;
      canvas.height = canvas.clientHeight * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    resize();

    const counts: Record<Quality, number> = { high: 60, medium: 30, low: 12 };
    const COUNT = counts[quality];
    const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;

    const particles = Array.from({ length: COUNT }, () => ({
      x: Math.random() * canvas.clientWidth,
      y: Math.random() * canvas.clientHeight,
      r: 0.7 + Math.random() * 1.9,
      vy: 0.03 + Math.random() * 0.12,
      drift: (Math.random() - 0.5) * 0.06,
      tw: Math.random() * Math.PI * 2,
      hue: Math.random() > 0.82 ? '201, 162, 39' : '168, 178, 191',
    }));

    const draw = () => {
      if (!running) return;
      ctx.clearRect(0, 0, canvas.clientWidth, canvas.clientHeight);
      const t = performance.now() / 1000;
      for (const p of particles) {
        if (!reduce) {
          p.y -= p.vy;
          p.x += p.drift + Math.sin(t * 0.3 + p.tw) * 0.03;
          if (p.y < -6) { p.y = canvas.clientHeight + 6; p.x = Math.random() * canvas.clientWidth; }
          if (p.x < -6) p.x = canvas.clientWidth + 6;
          if (p.x > canvas.clientWidth + 6) p.x = -6;
        }
        const twinkle = reduce ? 0.5 : 0.45 + 0.35 * Math.sin(t * 0.8 + p.tw);
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${p.hue}, ${p.r > 1.6 ? 0.5 * twinkle : 0.28 * twinkle})`;
        ctx.fill();
      }
      raf = requestAnimationFrame(draw);
    };
    draw();

    const onVis = () => {
      if (document.hidden) { running = false; cancelAnimationFrame(raf); }
      else if (!running) { running = true; draw(); }
    };
    document.addEventListener('visibilitychange', onVis);
    window.addEventListener('resize', resize);
    return () => {
      running = false;
      cancelAnimationFrame(raf);
      document.removeEventListener('visibilitychange', onVis);
      window.removeEventListener('resize', resize);
    };
  }, [quality]);

  return (
    <canvas
      ref={ref}
      style={{
        position: 'absolute', inset: 0, width: '100%', height: '100%',
        mixBlendMode: 'screen', opacity: 0.8, pointerEvents: 'none',
      }}
      aria-hidden="true"
    />
  );
}

/* Abstract geological ridge on 2D canvas — zero WebGL dependency,
   deliberately "slow, controlled, premium" (§9). */
function MineralRidge({ quality }: { quality: Quality }) {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    let raf = 0;
    let running = true;
    const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
    const SPEED = reduce ? 0 : 1;

    const resize = () => {
      canvas.width = canvas.clientWidth * dpr;
      canvas.height = canvas.clientHeight * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    resize();

    const layers = quality === 'low' ? 2 : 3;
    const draw = () => {
      if (!running) return;
      const w = canvas.clientWidth;
      const h = canvas.clientHeight;
      ctx.clearRect(0, 0, w, h);
      const t = performance.now() / 1000;

      for (let l = 0; l < layers; l++) {
        const depth = (l + 1) / layers;
        const baseY = h * (0.62 + l * 0.12);
        const amp = 26 - l * 6;
        ctx.beginPath();
        ctx.moveTo(0, h);
        for (let x = 0; x <= w; x += 14) {
          const y = baseY
            + Math.sin(x * 0.006 + t * 0.05 * SPEED + l * 2.1) * amp
            + Math.sin(x * 0.017 + l * 4.7) * (amp * 0.35);
          ctx.lineTo(x, y);
        }
        ctx.lineTo(w, h);
        ctx.closePath();
        const g = ctx.createLinearGradient(0, baseY - amp, 0, h);
        const shade = l === layers - 1
          ? `rgba(17, 20, 24, ${0.55 + depth * 0.3})`
          : `rgba(23, 27, 33, ${0.4 + depth * 0.25})`;
        g.addColorStop(0, shade);
        g.addColorStop(1, 'rgba(11, 13, 16, 0.92)');
        ctx.fillStyle = g;
        ctx.fill();
      }

      // faint gold seam through the middle ridge — geological intelligence accent
      ctx.beginPath();
      for (let x = 0; x <= w; x += 14) {
        const y = h * 0.62
          + Math.sin(x * 0.006 + t * 0.05 * SPEED + 2.1) * 26
          + Math.sin(x * 0.017 + 4.7) * 9 + 8;
        x === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
      }
      ctx.strokeStyle = 'rgba(201, 162, 39, 0.18)';
      ctx.lineWidth = 1.2;
      ctx.stroke();

      raf = requestAnimationFrame(draw);
    };
    draw();

    const onVis = () => {
      if (document.hidden) { running = false; cancelAnimationFrame(raf); }
      else if (!running) { running = true; draw(); }
    };
    document.addEventListener('visibilitychange', onVis);
    window.addEventListener('resize', resize);
    return () => {
      running = false;
      cancelAnimationFrame(raf);
      document.removeEventListener('visibilitychange', onVis);
      window.removeEventListener('resize', resize);
    };
  }, [quality]);

  return (
    <canvas
      ref={ref}
      style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', pointerEvents: 'none' }}
      aria-hidden="true"
    />
  );
}

export function GeologicalEnvironment() {
  const [mounted, setMounted] = useState(false);
  const [quality, setQuality] = useState<Quality>('low');

  useEffect(() => {
    setQuality(detectQuality());
    // mount after first paint — never block LCP (§10, §51)
    const id = window.setTimeout(() => setMounted(true), 350);
    return () => window.clearTimeout(id);
  }, []);

  const detail = useMemo(() => quality, [quality]);

  if (!mounted) return <GeologicalAtmosphere />;
  if (quality === 'low') {
    return (
      <div className="wm-geo-atmosphere" aria-hidden="true">
        <GeologicalAtmosphere />
        <MineralRidge quality="low" />
      </div>
    );
  }
  return (
    <div className="wm-geo-atmosphere" aria-hidden="true">
      <GeologicalAtmosphere />
      <MineralRidge quality={detail} />
      <ParticleField quality={detail} />
    </div>
  );
}
