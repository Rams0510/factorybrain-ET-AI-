import axios from "axios";
import { auth } from "./firebase";

export const api = axios.create({
  baseURL: "/api",
});

api.interceptors.request.use(async (config) => {
  const currentUser = auth.currentUser;
  if (currentUser) {
    const token = await currentUser.getIdToken();
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ---------- Typed API calls ----------

export interface DocumentItem {
  id: string;
  filename: string;
  file_type: string | null;
  doc_category: string | null;
  size_bytes: number;
  status: string;
  page_count: number;
  ocr_used: boolean;
  chunk_count: number;
  uploaded_at: string;
  processed_at: string | null;
  extracted_text_preview?: string | null;
  task_id?: string | null;
}

export interface EquipmentItem {
  id: string;
  tag: string;
  name: string | null;
  equipment_type: string;
  plant: string | null;
  department: string | null;
  status: string;
  risk_score: number;
  last_maintenance: string | null;
}

export interface ChatSource {
  document_id: string;
  filename: string;
  chunk_text: string;
  score: number;
}

export interface ChatApiResponse {
  session_id: string;
  answer: string;
  confidence_score: number;
  sources: ChatSource[];
}

export const loginWithIdToken = (id_token: string) =>
  api.post("/login", { id_token }).then((r) => r.data);

export const fetchDocuments = (params?: { skip?: number; limit?: number; category?: string; search?: string; status?: string }) =>
  api.get<DocumentItem[]>("/documents", { params }).then((r) => r.data);

export const fetchDocumentsCount = (params?: { category?: string; search?: string; status?: string }) =>
  api.get<{ count: number }>("/documents/count", { params }).then((r) => r.data.count);

export const uploadDocuments = (files: FileList) => {
  const form = new FormData();
  Array.from(files).forEach((f) => form.append("files", f));
  // Do NOT set Content-Type manually here — the browser must generate it
  // itself so it includes the multipart "boundary" parameter that marks
  // where each file starts/ends in the body. A hard-coded
  // "multipart/form-data" header without a boundary produces a body the
  // server cannot parse, which is why uploads were failing.
  return api.post("/upload", form).then((r) => r.data);
};

export const deleteDocument = (id: string) => api.delete(`/document/${id}`).then((r) => r.data);

export const fetchEquipment = () => api.get<EquipmentItem[]>("/equipment").then((r) => r.data);

export const sendChatMessage = (message: string, session_id?: string) =>
  api.post<ChatApiResponse>("/chat", { message, session_id }).then((r) => r.data);

export const fetchAnalytics = () => api.get("/analytics").then((r) => r.data);

export const fetchGraph = () => api.get("/graph").then((r) => r.data);

export const fetchMaintenance = () => api.get("/maintenance").then((r) => r.data);

export const fetchCompliance = () => api.get("/compliance").then((r) => r.data);

export const fetchLessonsLearned = () => api.get("/lessons-learned").then((r) => r.data);

export const globalSearch = (q: string, semantic = false) =>
  api.get("/search", { params: { q, semantic } }).then((r) => r.data);
