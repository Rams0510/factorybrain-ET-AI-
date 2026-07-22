import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Upload from "./pages/Upload";
import Documents from "./pages/Documents";
import Equipment from "./pages/Equipment";
import KnowledgeGraph from "./pages/KnowledgeGraph";
import Chat from "./pages/Chat";
import Maintenance from "./pages/Maintenance";
import Compliance from "./pages/Compliance";
import Analytics from "./pages/Analytics";
import Profile from "./pages/Profile";
import Settings from "./pages/Settings";
import SearchResults from "./pages/SearchResults";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, refetchOnWindowFocus: false } },
});

function Protected({ children }: { children: React.ReactNode }) {
  return <ProtectedRoute>{children}</ProtectedRoute>;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={<Protected><Dashboard /></Protected>} />
            <Route path="/upload" element={<Protected><Upload /></Protected>} />
            <Route path="/documents" element={<Protected><Documents /></Protected>} />
            <Route path="/equipment" element={<Protected><Equipment /></Protected>} />
            <Route path="/graph" element={<Protected><KnowledgeGraph /></Protected>} />
            <Route path="/chat" element={<Protected><Chat /></Protected>} />
            <Route path="/maintenance" element={<Protected><Maintenance /></Protected>} />
            <Route path="/compliance" element={<Protected><Compliance /></Protected>} />
            <Route path="/analytics" element={<Protected><Analytics /></Protected>} />
            <Route path="/profile" element={<Protected><Profile /></Protected>} />
            <Route path="/settings" element={<Protected><Settings /></Protected>} />
            <Route path="/search" element={<Protected><SearchResults /></Protected>} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}
