import { useQuery } from "@tanstack/react-query";
import { Wrench, TrendingUp } from "lucide-react";
import AppLayout from "../components/AppLayout";
import { fetchMaintenance } from "../lib/api";

interface Insight {
  equipment_tag: string;
  root_cause_analysis: string;
  recommendations: string[];
  risk_score: number;
  predicted_next_failure_window_days: number | null;
}

function riskColor(score: number) {
  if (score >= 0.7) return "border-industrial-danger/40 text-industrial-danger";
  if (score >= 0.4) return "border-industrial-accent/40 text-industrial-accent";
  return "border-industrial-success/40 text-industrial-success";
}

export default function Maintenance() {
  const { data, isLoading } = useQuery<Insight[]>({ queryKey: ["maintenance"], queryFn: fetchMaintenance });

  return (
    <AppLayout>
      <h1 className="font-display text-2xl font-bold mb-6">Maintenance Intelligence</h1>

      {isLoading ? (
        <div className="text-slate-500">Analyzing maintenance history...</div>
      ) : (
        <div className="space-y-4">
          {(data ?? []).map((item) => (
            <div key={item.equipment_tag} className="card p-5">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2 font-display font-bold text-lg">
                  <Wrench size={18} className="text-industrial-accent" />
                  {item.equipment_tag}
                </div>
                <span className={`badge ${riskColor(item.risk_score)}`}>
                  Risk Score: {(item.risk_score * 100).toFixed(0)}%
                </span>
              </div>
              <p className="text-sm text-slate-400 mb-3">
                <span className="text-slate-300 font-medium">Root Cause Analysis: </span>
                {item.root_cause_analysis}
              </p>
              <ul className="text-sm text-slate-400 list-disc pl-5 space-y-1 mb-3">
                {item.recommendations.map((r, i) => <li key={i}>{r}</li>)}
              </ul>
              {item.predicted_next_failure_window_days && (
                <div className="flex items-center gap-2 text-xs text-industrial-accent2">
                  <TrendingUp size={14} />
                  Predicted next failure window: ~{item.predicted_next_failure_window_days} days
                </div>
              )}
            </div>
          ))}
          {(data ?? []).length === 0 && (
            <div className="text-slate-500 text-center py-10">
              No equipment with maintenance history yet.
            </div>
          )}
        </div>
      )}
    </AppLayout>
  );
}
