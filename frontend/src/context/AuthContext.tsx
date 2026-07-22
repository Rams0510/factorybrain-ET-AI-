import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import {
  subscribeToAuthChanges,
  loginWithGoogle,
  loginWithEmail,
  registerWithEmail,
  signOut,
  type FirebaseUser,
} from "../lib/firebase";
import { loginWithIdToken } from "../lib/api";

interface BackendUser {
  id: string;
  email: string;
  name: string | null;
  photo_url: string | null;
  role: string;
  department: string | null;
  plant: string | null;
}

interface AuthContextValue {
  firebaseUser: FirebaseUser | null;
  backendUser: BackendUser | null;
  loading: boolean;
  loginGoogle: () => Promise<void>;
  loginEmail: (email: string, password: string) => Promise<void>;
  registerEmail: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [firebaseUser, setFirebaseUser] = useState<FirebaseUser | null>(null);
  const [backendUser, setBackendUser] = useState<BackendUser | null>(null);
  const [loading, setLoading] = useState(true);

  async function syncBackend(user: FirebaseUser) {
    const idToken = await user.getIdToken();
    const data = await loginWithIdToken(idToken);
    setBackendUser(data.user);
  }

  useEffect(() => {
    const unsubscribe = subscribeToAuthChanges(async (user) => {
      setFirebaseUser(user);
      if (user) {
        try {
          await syncBackend(user);
        } catch (err) {
          console.error("Backend session sync failed", err);
        }
      } else {
        setBackendUser(null);
      }
      setLoading(false);
    });
    return unsubscribe;
  }, []);

  const value: AuthContextValue = {
    firebaseUser,
    backendUser,
    loading,
    loginGoogle: async () => {
      await loginWithGoogle();
    },
    loginEmail: async (email, password) => {
      await loginWithEmail(email, password);
    },
    registerEmail: async (email, password) => {
      await registerWithEmail(email, password);
    },
    logout: async () => {
      await signOut();
    },
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
