import { useEffect, useRef } from "react";

type Node = { ax: number; ay: number; r: number; a: number; phase: number; speed: number };

type Layer = {
  cx: number;
  cy: number;
  rings: number;
  spokes: number;
  scale: number;
  alpha: number;
  width: number;
  speed: number;
  nodes: Node[][];
};

/**
 * Layered spiderweb background.
 * Layer 1 (foreground): a cleanly shaped web that expands and compresses as one
 * coherent breath. Layer 2 (underneath): a slower, wider counter-web.
 * Both are drawn with constant opacity so the pattern reads uniformly across
 * the whole viewport instead of fading toward the edges.
 */
export function WebBackground() {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let width = 0;
    let height = 0;
    let raf = 0;
    let dpr = 1;

    const layerDefs = [
      { cxf: 0.5, cyf: 0.5, rings: 8, spokes: 20, scale: 1.15, alpha: 0.5, width: 1.1, speed: 0.5 },
      { cxf: 0.5, cyf: 0.5, rings: 6, spokes: 14, scale: 1.7, alpha: 0.26, width: 0.9, speed: 0.3 },
    ];
    let layers: Layer[] = [];

    const build = () => {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      width = canvas.clientWidth;
      height = canvas.clientHeight;
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      const maxR = Math.hypot(width, height) * 0.72;

      layers = layerDefs.map((def, li) => {
        const nodes: Node[][] = [];
        for (let r = 0; r < def.rings; r++) {
          const ring: Node[] = [];
          const baseR = (maxR * def.scale * (r + 1)) / def.rings;
          for (let s = 0; s < def.spokes; s++) {
            const a = (s / def.spokes) * Math.PI * 2 + li * 0.22;
            ring.push({
              ax: 0,
              ay: 0,
              r: baseR,
              a,
              phase: (r / def.rings) * Math.PI, // ring-coherent breath = clean shape
              speed: def.speed,
            });
          }
          nodes.push(ring);
        }
        return {
          cx: width * def.cxf,
          cy: height * def.cyf,
          rings: def.rings,
          spokes: def.spokes,
          scale: def.scale,
          alpha: def.alpha,
          width: def.width,
          speed: def.speed,
          nodes,
        };
      });
    };

    const drawLayer = (layer: Layer, time: number, dir: number) => {
      const { cx, cy, nodes, spokes, rings } = layer;

      for (const ring of nodes) {
        for (const n of ring) {
          const breathe = 1 + 0.12 * Math.sin(time * n.speed * dir + n.phase);
          n.ax = cx + Math.cos(n.a) * n.r * breathe;
          n.ay = cy + Math.sin(n.a) * n.r * breathe;
        }
      }

      ctx.lineCap = "round";
      ctx.strokeStyle = `oklch(0.6 0.08 342 / ${layer.alpha})`;
      ctx.lineWidth = layer.width;

      // Radial spokes
      for (let s = 0; s < spokes; s++) {
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        for (let r = 0; r < rings; r++) {
          const n = nodes[r]![s]!;
          ctx.lineTo(n.ax, n.ay);
        }
        ctx.stroke();
      }

      // Concentric strands with a gentle, even sag
      for (let r = 0; r < rings; r++) {
        const ring = nodes[r]!;
        ctx.beginPath();
        ctx.moveTo(ring[0]!.ax, ring[0]!.ay);
        for (let s = 0; s <= spokes; s++) {
          const a = ring[s % spokes]!;
          const b = ring[(s + 1) % spokes]!;
          const mx = (a.ax + b.ax) / 2;
          const my = (a.ay + b.ay) / 2;
          const sag = 0.93;
          ctx.quadraticCurveTo(cx + (mx - cx) * sag, cy + (my - cy) * sag, b.ax, b.ay);
        }
        ctx.stroke();
      }
    };

    const draw = (t: number) => {
      const time = t / 1000;
      ctx.clearRect(0, 0, width, height);
      drawLayer(layers[1]!, time, -1);
      drawLayer(layers[0]!, time, 1);
      raf = requestAnimationFrame(draw);
    };

    build();
    raf = requestAnimationFrame(draw);
    window.addEventListener("resize", build);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", build);
    };
  }, []);

  return (
    <div className="pointer-events-none fixed inset-0 -z-10 bg-background">
      <canvas ref={ref} className="h-full w-full" />
    </div>
  );
}
