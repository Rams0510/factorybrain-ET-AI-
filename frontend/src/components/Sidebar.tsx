import { NavLink } from "react-router-dom";
import {
  LayoutDashboard, UploadCloud, FileText, Cpu, Share2, MessageSquare,
  Wrench, ShieldCheck, BarChart3, User, Settings, Factory,
} from "lucide-react";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/upload", label: "Upload Documents", icon: UploadCloud },
  { to: "/documents", label: "Documents", icon: FileText },
  { to: "/equipment", label: "Equipment", icon: Cpu },
  { to: "/graph", label: "Knowledge Graph", icon: Share2 },
  { to: "/chat", label: "AI Chat", icon: MessageSquare },
  { to: "/maintenance", label: "Maintenance", icon: Wrench },
  { to: "/compliance", label: "Compliance", icon: ShieldCheck },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/profile", label: "Profile", icon: User },
  { to: "/settings", label: "Settings", icon: Settings },
];

export default function Sidebar() {
  return (
    <aside className="w-64 shrink-0 h-screen sticky top-0 border-r border-industrial-border bg-industrial-panel/60 backdrop-blur-sm flex flex-col">
      <div className="flex items-center gap-2 px-5 py-5 border-b border-industrial-border">
        <Factory className="text-industrial-accent" size={26} />
        <div>
          <div className="font-display font-bold text-lg leading-none">FactoryBrain</div>
          <div className="text-[10px] font-mono text-slate-500 tracking-widest">AI PLATFORM</div>
        </div>
      </div>
      <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition ${
                isActive
                  ? "bg-industrial-accent/10 text-industrial-accent border border-industrial-accent/30"
                  : "text-slate-400 hover:text-slate-100 hover:bg-white/5 border border-transparent"
              }`
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="px-5 py-4 border-t border-industrial-border text-[11px] font-mono text-slate-600">
        v1.0.0 — Industrial Knowledge Intelligence
      </div>
    </aside>
  );
}
