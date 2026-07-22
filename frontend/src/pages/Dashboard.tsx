import { useQuery } from "@tanstack/react-query";
import { FileText, Cpu, UploadCloud, ShieldCheck, AlertTriangle } from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";
import { fetchAnalytics } from "../lib/api";
import AppLayout from "../components/AppLayout";

const COLORS = ["#F59E0B", "#38BDF8", "#22C55E", "#EF4444", "#A78BFA", "#F472B6"];

function KpiCard({ icon: Icon, label, value, accent }: { icon: any; label: string; value: string | number; accent: string }) {
  return (
    <div className="card p-5 flex items-center gap-4">
      <div className="p-3 rounded-lg" style={{ backgroundColor: `${accent}1A`, color: accent }}>
        <Icon size={22} />
      </div>
      <div>
        <div className="text-2xl font-display font-bold">{value}</div>
        <div className="text-xs text-slate-500">{label}</div>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const { data, isLoading } = useQuery({ queryKey: ["analytics"], queryFn: fetchAnalytics });

  return (
    <AppLayout>
      <h1 className="font-display text-2xl font-bold mb-6">Dashboard</h1>

      {isLoading || !data ? (
        <div className="text-slate-500">Loading plant intelligence...</div>
      ) : (
        <div className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <KpiCard icon={FileText} label="Total Documents" value={data.total_documents} accent="#38BDF8" />
            <KpiCard icon={Cpu} label="Equipment Count" value={data.total_equipment} accent="#F59E0B" />
            <KpiCard icon={UploadCloud} label="Recent Uploads (7d)" value={data.recent_uploads} accent="#22C55E" />
            <KpiCard icon={ShieldCheck} label="Compliance Score" value={`${data.compliance_score}%`} accent="#A78BFA" />
            <KpiCard icon={AlertTriangle} label="Maintenance Alerts" value={data.open_maintenance_alerts} accent="#EF4444" />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="card p-5">
              <h2 className="font-semibold mb-4">Documents by Category</h2>
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie
                    data={Object.entries(data.documents_by_category).map(([name, value]) => ({ name, value }))}
                    dataKey="value"
                    nameKey="name"
                    outerRadius={90}
                    label
                  >
                    {Object.keys(data.documents_by_category).map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ background: "#111827", border: "1px solid #1F2937" }} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="card p-5">
              <h2 className="font-semibold mb-4">Maintenance Trend</h2>
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={data.maintenance_trend}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                  <XAxis dataKey="month" stroke="#64748B" fontSize={12} />
                  <YAxis stroke="#64748B" fontSize={12} />
                  <Tooltip contentStyle={{ background: "#111827", border: "1px solid #1F2937" }} />
                  <Line type="monotone" dataKey="count" stroke="#F59E0B" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="card p-5">
            <h2 className="font-semibold mb-4">Equipment Distribution</h2>
            <div className="flex flex-wrap gap-3">
              {Object.entries(data.equipment_by_type).map(([type, count]) => (
                <div key={type} className="badge border-industrial-border text-slate-300">
                  {type}: {count as number}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </AppLayout>
  );
}
