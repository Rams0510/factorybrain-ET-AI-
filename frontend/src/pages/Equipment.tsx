import { useQuery } from "@tanstack/react-query";
import { Cpu, AlertTriangle } from "lucide-react";
import AppLayout from "../components/AppLayout";
import { fetchEquipment } from "../lib/api";

function riskColor(score: number) {
  if (score >= 0.7) return "text-industrial-danger border-industrial-danger/40";
  if (score >= 0.4) return "text-industrial-accent border-industrial-accent/40";
  return "text-industrial-success border-industrial-success/40";
}

export default function Equipment() {
  const { data, isLoading } = useQuery({ queryKey: ["equipment"], queryFn: fetchEquipment });

  return (
    <AppLayout>
      <h1 className="font-display text-2xl font-bold mb-6">Equipment</h1>

      {isLoading ? (
        <div className="text-slate-500">Loading equipment registry...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {(data ?? []).map((eq) => (
            <div key={eq.id} className="card p-5">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2 font-display font-bold text-lg">
                  <Cpu size={20} className="text-industrial-accent2" />
                  {eq.tag}
                </div>
                {eq.risk_score >= 0.7 && <AlertTriangle size={18} className="text-industrial-danger" />}
              </div>
              <div className="text-sm text-slate-400 space-y-1">
                <div>Type: <span className="text-slate-200">{eq.equipment_type}</span></div>
                <div>Plant: <span className="text-slate-200">{eq.plant ?? "—"}</span></div>
                <div>Status: <span className="text-slate-200">{eq.status}</span></div>
                <div>Last maintenance: <span className="text-slate-200">{eq.last_maintenance ? new Date(eq.last_maintenance).toLocaleDateString() : "—"}</span></div>
              </div>
              <div className={`badge mt-4 inline-block ${riskColor(eq.risk_score)}`}>
                Risk: {(eq.risk_score * 100).toFixed(0)}%
              </div>
            </div>
          ))}
          {(data ?? []).length === 0 && (
            <div className="text-slate-500 col-span-full text-center py-10">
              No equipment detected yet — upload maintenance reports or P&ID drawings to populate this registry.
            </div>
          )}
        </div>
      )}
    </AppLayout>
  );
}
