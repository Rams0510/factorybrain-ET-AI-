import { useQuery } from "@tanstack/react-query";
import { ShieldCheck, AlertCircle, XCircle } from "lucide-react";
import AppLayout from "../components/AppLayout";
import { fetchCompliance } from "../lib/api";

interface ComplianceItem {
  standard: string;
  requirement: string;
  status: string;
  expiry_date: string | null;
}
interface ComplianceReport {
  overall_score: number;
  items: ComplianceItem[];
  missing_reports: string[];
  expired_certificates: string[];
}

export default function Compliance() {
  const { data, isLoading } = useQuery<ComplianceReport>({ queryKey: ["compliance"], queryFn: fetchCompliance });

  return (
    <AppLayout>
      <h1 className="font-display text-2xl font-bold mb-6">Compliance Intelligence</h1>

      {isLoading || !data ? (
        <div className="text-slate-500">Running compliance checks...</div>
      ) : (
        <div className="space-y-6">
          <div className="card p-6 flex items-center gap-6">
            <ShieldCheck size={40} className="text-industrial-success" />
            <div>
              <div className="text-3xl font-display font-bold">{data.overall_score}%</div>
              <div className="text-slate-500 text-sm">Overall Compliance Score (Factory Act, OISD, PESO, ISO, Environmental)</div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="card p-5">
              <h2 className="font-semibold mb-4 flex items-center gap-2"><AlertCircle size={16} className="text-industrial-danger" /> Missing Reports</h2>
              {data.missing_reports.length === 0 ? (
                <p className="text-slate-500 text-sm">No missing reports detected.</p>
              ) : (
                <ul className="text-sm text-slate-400 space-y-1">
                  {data.missing_reports.map((r, i) => <li key={i}>• {r}</li>)}
                </ul>
              )}
            </div>
            <div className="card p-5">
              <h2 className="font-semibold mb-4 flex items-center gap-2"><XCircle size={16} className="text-industrial-warning" /> Expired Certificates</h2>
              {data.expired_certificates.length === 0 ? (
                <p className="text-slate-500 text-sm">No expired certificates detected.</p>
              ) : (
                <ul className="text-sm text-slate-400 space-y-1">
                  {data.expired_certificates.map((r, i) => <li key={i}>• {r}</li>)}
                </ul>
              )}
            </div>
          </div>

          <div className="card overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-white/5 text-slate-400 text-xs uppercase">
                <tr>
                  <th className="text-left px-4 py-3">Standard</th>
                  <th className="text-left px-4 py-3">Requirement</th>
                  <th className="text-left px-4 py-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((item, i) => (
                  <tr key={i} className="border-t border-industrial-border">
                    <td className="px-4 py-3">{item.standard}</td>
                    <td className="px-4 py-3 text-slate-400">{item.requirement}</td>
                    <td className="px-4 py-3">
                      <span className={`badge ${
                        item.status === "compliant" ? "border-industrial-success/40 text-industrial-success" :
                        item.status === "expired" ? "border-industrial-warning/40 text-industrial-warning" :
                        "border-industrial-danger/40 text-industrial-danger"
                      }`}>
                        {item.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </AppLayout>
  );
}
