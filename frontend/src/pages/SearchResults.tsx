import { useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { FileText, Cpu, User as UserIcon, MapPin } from "lucide-react";
import AppLayout from "../components/AppLayout";
import { globalSearch } from "../lib/api";

export default function SearchResults() {
  const [params] = useSearchParams();
  const q = params.get("q") ?? "";

  const { data, isLoading } = useQuery({
    queryKey: ["search", q],
    queryFn: () => globalSearch(q),
    enabled: !!q,
  });

  return (
    <AppLayout>
      <h1 className="font-display text-2xl font-bold mb-6">Search results for "{q}"</h1>

      {isLoading ? (
        <div className="text-slate-500">Searching...</div>
      ) : !data ? (
        <div className="text-slate-500">Enter a search term above.</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="card p-5">
            <h2 className="font-semibold mb-3 flex items-center gap-2"><FileText size={16} /> Documents</h2>
            {data.documents?.length ? (
              <ul className="space-y-2 text-sm text-slate-300">
                {data.documents.map((d: any) => <li key={d.id}>{d.filename} <span className="text-slate-500 text-xs">({d.category})</span></li>)}
              </ul>
            ) : <p className="text-slate-500 text-sm">No matching documents.</p>}
          </div>

          <div className="card p-5">
            <h2 className="font-semibold mb-3 flex items-center gap-2"><Cpu size={16} /> Equipment</h2>
            {data.equipment?.length ? (
              <ul className="space-y-2 text-sm text-slate-300">
                {data.equipment.map((e: any) => <li key={e.tag}>{e.tag} — {e.type} ({e.plant ?? "—"})</li>)}
              </ul>
            ) : <p className="text-slate-500 text-sm">No matching equipment.</p>}
          </div>

          <div className="card p-5">
            <h2 className="font-semibold mb-3 flex items-center gap-2"><UserIcon size={16} /> Engineers</h2>
            {data.engineers?.length ? (
              <ul className="space-y-2 text-sm text-slate-300">
                {data.engineers.map((e: any, i: number) => <li key={i}>{e.name}</li>)}
              </ul>
            ) : <p className="text-slate-500 text-sm">No matching engineers.</p>}
          </div>

          <div className="card p-5">
            <h2 className="font-semibold mb-3 flex items-center gap-2"><MapPin size={16} /> Plants</h2>
            {data.plants?.length ? (
              <ul className="space-y-2 text-sm text-slate-300">
                {data.plants.map((p: string, i: number) => <li key={i}>{p}</li>)}
              </ul>
            ) : <p className="text-slate-500 text-sm">No matching plants.</p>}
          </div>
        </div>
      )}
    </AppLayout>
  );
}
