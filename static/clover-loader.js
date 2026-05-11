// Shared clover loading animation.
// Usage: add data-clover to any element; optionally data-size (px) and data-hue (0-360).
// CloverLoader.mountAll(root?) scans root for unmounted [data-clover] elements.
// CloverLoader.createLoader(container, size, hue) mounts directly on a container element.

const CloverLoader = (() => {
  const TOTAL     = 600;
  const TRAIL_MAX = Math.floor(TOTAL * 0.80); // max trail length (80% of path)
  const FADE_FRAC = 0.65;                     // fraction of trail that is fully opaque

  // Pre-compute the rose curve once at unit scale; each instance multiplies by its own scale.
  const unitPts = [];
  for (let i = 0; i < TOTAL; i++) {
    const t = (i / TOTAL) * Math.PI * 2;
    const r = Math.cos(2 * t);
    unitPts.push({ x: r * Math.cos(t), y: r * Math.sin(t) });
  }

  function createLoader(container, size, hue) {
    const dpr   = Math.min(window.devicePixelRatio || 1, 2);
    const px    = size * dpr;    // physical canvas dimension
    const scale = px * 0.42;
    const cx    = px / 2;
    const cy    = px / 2;

    const canvas = document.createElement('canvas');
    canvas.width  = px;
    canvas.height = px;
    canvas.style.width  = size + 'px';
    canvas.style.height = size + 'px';
    canvas.style.display = 'block';
    container.appendChild(canvas);

    const ctx   = canvas.getContext('2d');
    const lineW = Math.max(1.5, px * 0.022);
    const dotR  = Math.max(2,   px * 0.046);
    const glowR = dotR * 3.5;

    let pos        = 0;
    let trailGrown = TRAIL_MAX;
    let alive      = true;

    function draw() {
      // Canvas disconnects automatically when its parent is replaced via innerHTML.
      if (!alive || !canvas.isConnected) { alive = false; return; }
      ctx.clearRect(0, 0, px, px);

      const head     = Math.floor(pos) % TOTAL;
      const trailLen = Math.floor(trailGrown);
      const solidLen = Math.floor(trailGrown * FADE_FRAC);

      for (let age = trailLen; age >= 1; age--) {
        const a = (head - age + TOTAL * 8) % TOTAL;
        const b = (a + 1) % TOTAL;

        let alpha;
        if (age <= solidLen) {
          alpha = 1;
        } else {
          const denom = (trailLen - solidLen) || 1;
          alpha = 1 - (age - solidLen) / denom;
        }
        if (alpha < 0.01) continue;

        const recency   = 1 - age / TRAIL_MAX;
        const lightness = 22 + recency * 42;
        const sat       = 55 + recency * 30;

        ctx.save();
        ctx.globalAlpha = alpha;
        ctx.beginPath();
        ctx.moveTo(cx + unitPts[a].x * scale, cy + unitPts[a].y * scale);
        ctx.lineTo(cx + unitPts[b].x * scale, cy + unitPts[b].y * scale);
        ctx.strokeStyle = `hsl(${hue}, ${sat}%, ${lightness}%)`;
        ctx.lineWidth   = lineW;
        ctx.lineCap     = 'round';
        ctx.stroke();
        ctx.restore();
      }

      // Glowing dot at the head
      const hx = cx + unitPts[head].x * scale;
      const hy = cy + unitPts[head].y * scale;

      const glow = ctx.createRadialGradient(hx, hy, 0, hx, hy, glowR);
      glow.addColorStop(0,   `hsla(${hue - 10}, 100%, 88%, 0.55)`);
      glow.addColorStop(0.4, `hsla(${hue},       70%,  65%, 0.22)`);
      glow.addColorStop(1,   `hsla(${hue},       70%,  60%, 0)`);
      ctx.beginPath();
      ctx.arc(hx, hy, glowR, 0, Math.PI * 2);
      ctx.fillStyle = glow;
      ctx.fill();

      ctx.beginPath();
      ctx.arc(hx, hy, dotR, 0, Math.PI * 2);
      ctx.fillStyle = `hsl(${hue - 5}, 80%, 90%)`;
      ctx.fill();

      pos = (pos + 2.5) % TOTAL;
      requestAnimationFrame(draw);
    }

    requestAnimationFrame(draw);
    return { canvas, stop() { alive = false; } };
  }

  function mountAll(root) {
    const scope = root || document;
    scope.querySelectorAll('[data-clover]').forEach(el => {
      if (el._cloverLoader) return;
      const size = parseInt(el.dataset.size || '48', 10);
      const hue  = parseInt(el.dataset.hue  || '142', 10);
      el._cloverLoader = createLoader(el, size, hue);
    });
  }

  document.addEventListener('DOMContentLoaded', () => mountAll());

  return { mountAll, createLoader };
})();
