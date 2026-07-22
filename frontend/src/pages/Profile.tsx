import { useAuth } from "../context/AuthContext";
import AppLayout from "../components/AppLayout";
import { User as UserIcon, Mail, Building2, MapPin } from "lucide-react";

export default function Profile() {
  const { backendUser } = useAuth();

  return (
    <AppLayout>
      <h1 className="font-display text-2xl font-bold mb-6">Profile</h1>

      <div className="card p-6 max-w-lg">
        <div className="flex items-center gap-4 mb-6">
          {backendUser?.photo_url ? (
            <img src={backendUser.photo_url} alt="avatar" className="w-16 h-16 rounded-full" />
          ) : (
            <div className="w-16 h-16 rounded-full bg-industrial-accent/20 flex items-center justify-center text-xl font-semibold text-industrial-accent">
              {backendUser?.name?.[0] ?? backendUser?.email?.[0]?.toUpperCase()}
            </div>
          )}
          <div>
            <div className="font-display font-bold text-lg">{backendUser?.name ?? "Unnamed User"}</div>
            <div className="text-slate-500 text-sm">{backendUser?.role}</div>
          </div>
        </div>

        <div className="space-y-3 text-sm">
          <div className="flex items-center gap-3 text-slate-300">
            <Mail size={16} className="text-slate-500" /> {backendUser?.email}
          </div>
          <div className="flex items-center gap-3 text-slate-300">
            <Building2 size={16} className="text-slate-500" /> {backendUser?.department ?? "No department set"}
          </div>
          <div className="flex items-center gap-3 text-slate-300">
            <MapPin size={16} className="text-slate-500" /> {backendUser?.plant ?? "No plant assigned"}
          </div>
          <div className="flex items-center gap-3 text-slate-300">
            <UserIcon size={16} className="text-slate-500" /> User ID: <span className="font-mono text-xs text-slate-500">{backendUser?.id}</span>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
