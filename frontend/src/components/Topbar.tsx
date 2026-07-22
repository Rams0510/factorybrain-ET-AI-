import { Search, Bell, LogOut } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Topbar() {
  const [query, setQuery] = useState("");
  const navigate = useNavigate();
  const { backendUser, logout } = useAuth();

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (query.trim()) navigate(`/search?q=${encodeURIComponent(query)}`);
  }

  return (
    <header className="h-16 border-b border-industrial-border bg-industrial-panel/40 backdrop-blur-sm flex items-center justify-between px-6 sticky top-0 z-10">
      <form onSubmit={handleSearch} className="flex items-center gap-2 bg-industrial-bg border border-industrial-border rounded-lg px-3 py-1.5 w-96">
        <Search size={16} className="text-slate-500" />
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search equipment, documents, engineers..."
          className="bg-transparent outline-none text-sm w-full placeholder:text-slate-600"
        />
      </form>

      <div className="flex items-center gap-4">
        <button className="text-slate-400 hover:text-slate-100 transition">
          <Bell size={20} />
        </button>
        <div className="flex items-center gap-2">
          {backendUser?.photo_url ? (
            <img src={backendUser.photo_url} alt="avatar" className="w-8 h-8 rounded-full" />
          ) : (
            <div className="w-8 h-8 rounded-full bg-industrial-accent/20 flex items-center justify-center text-xs font-semibold text-industrial-accent">
              {backendUser?.name?.[0] ?? backendUser?.email?.[0]?.toUpperCase() ?? "U"}
            </div>
          )}
          <div className="text-sm leading-tight">
            <div className="font-medium">{backendUser?.name ?? backendUser?.email}</div>
            <div className="text-xs text-slate-500">{backendUser?.role}</div>
          </div>
        </div>
        <button onClick={() => logout()} className="text-slate-400 hover:text-industrial-danger transition" title="Sign out">
          <LogOut size={18} />
        </button>
      </div>
    </header>
  );
}
