import { useQuery } from "@tanstack/react-query";
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, LineChart, Line } from "recharts";
import AppLayout from "../components/AppLayout";
import { fetchAnalytics } from "../lib/api";

export default function Analytics() {
  const { data, isLoading } = useQuery({ queryKey: ["analytics"], queryFn: fetchAnalytics });

  return (
    <AppLayout>
      <h1 className="font-display text-2xl font-bold mb-6">Analytics</h1>

      {isLoading || !data ? (
        <div className="text-slate-500">Crunching plant-wide numbers...</div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card p-5">
            <h2 className="font-semibold mb-4">Maintenance Trend (6 months)</h2>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={data.maintenance_trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                <XAxis dataKey="month" stroke="#64748B" fontSize={12} />
                <YAxis stroke="#64748B" fontSize={12} />
                <Tooltip contentStyle={{ background: "#111827", border: "1px solid #1F2937" }} />
                <Bar dataKey="count" fill="#F59E0B" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="card p-5">
            <h2 className="font-semibold mb-4">Failure Trend (6 months)</h2>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={data.failure_trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                <XAxis dataKey="month" stroke="#64748B" fontSize={12} />
                <YAxis stroke="#64748B" fontSize={12} />
                <Tooltip contentStyle={{ background: "#111827", border: "1px solid #1F2937" }} />
                <Bar dataKey="count" fill="#EF4444" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="card p-5 lg:col-span-2">
            <h2 className="font-semibold mb-4">Compliance Score Trend</h2>
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={data.compliance_trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                <XAxis dataKey="month" stroke="#64748B" fontSize={12} />
                <YAxis stroke="#64748B" fontSize={12} domain={[0, 100]} />
                <Tooltip contentStyle={{ background: "#111827", border: "1px solid #1F2937" }} />
                <Line type="monotone" dataKey="score" stroke="#A78BFA" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </AppLayout>
  );
}
