import { useState } from "react";
import AppLayout from "../components/AppLayout";

export default function Settings() {
  const [darkMode, setDarkMode] = useState(true);
  const [notifications, setNotifications] = useState(true);

  return (
    <AppLayout>
      <h1 className="font-display text-2xl font-bold mb-6">Settings</h1>

      <div className="card p-6 max-w-lg space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="font-medium">Dark Mode</div>
            <div className="text-xs text-slate-500">FactoryBrain AI is designed dark-first for control-room use.</div>
          </div>
          <button
            onClick={() => setDarkMode((v) => !v)}
            className={`w-11 h-6 rounded-full transition ${darkMode ? "bg-industrial-accent" : "bg-industrial-border"}`}
          >
            <span className={`block w-5 h-5 bg-white rounded-full transition transform ${darkMode ? "translate-x-5" : "translate-x-0.5"}`} />
          </button>
        </div>

        <div className="flex items-center justify-between">
          <div>
            <div className="font-medium">Maintenance Alert Notifications</div>
            <div className="text-xs text-slate-500">Get notified when equipment risk score crosses 70%.</div>
          </div>
          <button
            onClick={() => setNotifications((v) => !v)}
            className={`w-11 h-6 rounded-full transition ${notifications ? "bg-industrial-accent" : "bg-industrial-border"}`}
          >
            <span className={`block w-5 h-5 bg-white rounded-full transition transform ${notifications ? "translate-x-5" : "translate-x-0.5"}`} />
          </button>
        </div>

        <div className="pt-4 border-t border-industrial-border text-xs text-slate-500">
          Environment variables (API keys, database connections) are configured server-side via the
          backend's <code className="font-mono text-slate-400">.env</code> file — see the README for setup instructions.
        </div>
      </div>
    </AppLayout>
  );
}
