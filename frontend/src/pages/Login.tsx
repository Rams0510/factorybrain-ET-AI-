import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Factory, Mail, Lock } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [mode, setMode] = useState<"login" | "register">("login");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const { loginGoogle, loginEmail, registerEmail } = useAuth();
  const navigate = useNavigate();

  async function handleGoogle() {
    setError(null);
    try {
      await loginGoogle();
      navigate("/");
    } catch (err: any) {
      setError(err.message ?? "Google sign-in failed");
    }
  }

  async function handleEmailSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      if (mode === "login") await loginEmail(email, password);
      else await registerEmail(email, password);
      navigate("/");
    } catch (err: any) {
      setError(err.message ?? "Authentication failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-industrial-bg px-4">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="card w-full max-w-md p-8"
      >
        <div className="flex flex-col items-center mb-8">
          <Factory className="text-industrial-accent mb-2" size={40} />
          <h1 className="font-display font-bold text-2xl">FactoryBrain AI</h1>
          <p className="text-slate-500 text-sm mt-1">Industrial Knowledge Intelligence Platform</p>
        </div>

        <button onClick={handleGoogle} className="btn-secondary w-full flex items-center justify-center gap-2 mb-4">
          Continue with Google
        </button>

        <div className="flex items-center gap-3 my-4">
          <div className="flex-1 h-px bg-industrial-border" />
          <span className="text-xs text-slate-600">or</span>
          <div className="flex-1 h-px bg-industrial-border" />
        </div>

        <form onSubmit={handleEmailSubmit} className="space-y-3">
          <div className="flex items-center gap-2 bg-industrial-bg border border-industrial-border rounded-lg px-3 py-2">
            <Mail size={16} className="text-slate-500" />
            <input
              type="email"
              required
              placeholder="Work email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="bg-transparent outline-none text-sm w-full"
            />
          </div>
          <div className="flex items-center gap-2 bg-industrial-bg border border-industrial-border rounded-lg px-3 py-2">
            <Lock size={16} className="text-slate-500" />
            <input
              type="password"
              required
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="bg-transparent outline-none text-sm w-full"
            />
          </div>

          {error && <p className="text-industrial-danger text-xs">{error}</p>}

          <button type="submit" disabled={submitting} className="btn-primary w-full">
            {submitting ? "Please wait..." : mode === "login" ? "Sign in" : "Create account"}
          </button>
        </form>

        <p className="text-center text-xs text-slate-500 mt-5">
          {mode === "login" ? "Don't have an account?" : "Already have an account?"}{" "}
          <button
            className="text-industrial-accent hover:underline"
            onClick={() => setMode(mode === "login" ? "register" : "login")}
          >
            {mode === "login" ? "Register" : "Sign in"}
          </button>
        </p>
      </motion.div>
    </div>
  );
}
