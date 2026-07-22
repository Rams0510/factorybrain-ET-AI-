import { useEffect, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import AppLayout from "../components/AppLayout";
import { fetchGraph } from "../lib/api";

interface GNode { id: string; label: string; type: string; x?: number; y?: number; vx?: number; vy?: number; }
interface GEdge { source: string; target: string; relationship: string; }

const TYPE_COLORS: Record<string, string> = {
  Equipment: "#F59E0B",
  Engineer: "#38BDF8",
  Document: "#A78BFA",
  Incident: "#EF4444",
  Plant: "#22C55E",
  Inspection: "#F472B6",
  Regulation: "#FBBF24",
};

/**
 * Lightweight force-directed layout computed client-side (no extra graph
 * library dependency) — good enough for a few hundred nodes, which is the
 * scale Neo4j returns via GET /api/graph.
 */
function useForceLayout(nodes: GNode[], edges: GEdge[], width: number, height: number) {
  const [positioned, setPositioned] = useState<GNode[]>([]);

  useEffect(() => {
    if (nodes.length === 0) return;
    const sim = nodes.map((n) => ({
      ...n,
      x: width / 2 + (Math.random() - 0.5) * 200,
      y: height / 2 + (Math.random() - 0.5) * 200,
      vx: 0,
      vy: 0,
    }));
    const byId = new Map(sim.map((n) => [n.id, n]));

    for (let iter = 0; iter < 250; iter++) {
      // repulsion
      for (let i = 0; i < sim.length; i++) {
        for (let j = i + 1; j < sim.length; j++) {
          const a = sim[i], b = sim[j];
          const dx = a.x! - b.x!, dy = a.y! - b.y!;
          const dist = Math.max(Math.sqrt(dx * dx + dy * dy), 1);
          const force = 1200 / (dist * dist);
          a.vx! += (dx / dist) * force;
          a.vy! += (dy / dist) * force;
          b.vx! -= (dx / dist) * force;
          b.vy! -= (dy / dist) * force;
        }
      }
      // attraction along edges
      for (const e of edges) {
        const a = byId.get(e.source), b = byId.get(e.target);
        if (!a || !b) continue;
        const dx = b.x! - a.x!, dy = b.y! - a.y!;
        const dist = Math.max(Math.sqrt(dx * dx + dy * dy), 1);
        const force = dist * 0.01;
        a.vx! += (dx / dist) * force;
        a.vy! += (dy / dist) * force;
        b.vx! -= (dx / dist) * force;
        b.vy! -= (dy / dist) * force;
      }
      for (const n of sim) {
        n.x! += n.vx! * 0.1;
        n.y! += n.vy! * 0.1;
        n.vx! *= 0.85;
        n.vy! *= 0.85;
        n.x = Math.min(Math.max(n.x!, 30), width - 30);
        n.y = Math.min(Math.max(n.y!, 30), height - 30);
      }
    }
    setPositioned(sim);
  }, [nodes, edges, width, height]);

  return positioned;
}

export default function KnowledgeGraph() {
  const { data, isLoading } = useQuery({ queryKey: ["graph"], queryFn: fetchGraph });
  const containerRef = useRef<HTMLDivElement>(null);
  const width = 1000, height = 600;

  const nodes: GNode[] = data?.nodes ?? [];
  const edges: GEdge[] = data?.edges ?? [];
  const positioned = useForceLayout(nodes, edges, width, height);
  const byId = new Map(positioned.map((n) => [n.id, n]));

  return (
    <AppLayout>
      <h1 className="font-display text-2xl font-bold mb-6">Knowledge Graph</h1>
      <div className="card p-4" ref={containerRef}>
        {isLoading ? (
          <div className="text-slate-500 p-10 text-center">Loading Neo4j graph...</div>
        ) : nodes.length === 0 ? (
          <div className="text-slate-500 p-10 text-center">
            No graph data yet — upload documents to populate Equipment, Engineer, and Document nodes.
          </div>
        ) : (
          <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-[600px]">
            {edges.map((e, i) => {
              const s = byId.get(e.source), t = byId.get(e.target);
              if (!s || !t) return null;
              return (
                <g key={i}>
                  <line x1={s.x} y1={s.y} x2={t.x} y2={t.y} stroke="#1F2937" strokeWidth={1.5} />
                  <text
                    x={(s.x! + t.x!) / 2}
                    y={(s.y! + t.y!) / 2}
                    fill="#475569"
                    fontSize={9}
                    textAnchor="middle"
                  >
                    {e.relationship}
                  </text>
                </g>
              );
            })}
            {positioned.map((n) => (
              <g key={n.id} transform={`translate(${n.x},${n.y})`}>
                <circle r={16} fill={TYPE_COLORS[n.type] ?? "#64748B"} fillOpacity={0.85} />
                <text y={30} textAnchor="middle" fontSize={10} fill="#CBD5E1">
                  {n.label}
                </text>
              </g>
            ))}
          </svg>
        )}
      </div>
      <div className="flex flex-wrap gap-3 mt-4">
        {Object.entries(TYPE_COLORS).map(([type, color]) => (
          <div key={type} className="flex items-center gap-2 text-xs text-slate-400">
            <span className="w-3 h-3 rounded-full inline-block" style={{ backgroundColor: color }} />
            {type}
          </div>
        ))}
      </div>
    </AppLayout>
  );
}
