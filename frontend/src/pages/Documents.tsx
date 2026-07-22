import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { FileText, Trash2, Search, ChevronLeft, ChevronRight } from "lucide-react";
import AppLayout from "../components/AppLayout";
import { fetchDocuments, fetchDocumentsCount, deleteDocument } from "../lib/api";

const STATUS_COLORS: Record<string, string> = {
  uploaded: "text-slate-400 border-slate-600",
  processing: "text-industrial-accent2 border-industrial-accent2/40",
  parsed: "text-industrial-accent border-industrial-accent/40",
  embedded: "text-industrial-success border-industrial-success/40",
  failed: "text-industrial-danger border-industrial-danger/40",
};

const PAGE_SIZE = 50;

export default function Documents() {
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [page, setPage] = useState(0);
  const queryClient = useQueryClient();

  // Debounce search input so we're not hitting the API on every keystroke
  // — matters once there are thousands of documents to filter server-side.
  useEffect(() => {
    const t = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(0);
    }, 300);
    return () => clearTimeout(t);
  }, [search]);

  const queryParams = { skip: page * PAGE_SIZE, limit: PAGE_SIZE, search: debouncedSearch || undefined };

  const { data, isLoading } = useQuery({
    queryKey: ["documents", queryParams],
    queryFn: () => fetchDocuments(queryParams),
    refetchInterval: 5000, // poll for processing status updates
  });

  const { data: totalCount } = useQuery({
    queryKey: ["documents-count", debouncedSearch],
    queryFn: () => fetchDocumentsCount({ search: debouncedSearch || undefined }),
    refetchInterval: 10000,
  });

  const del = useMutation({
    mutationFn: deleteDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      queryClient.invalidateQueries({ queryKey: ["documents-count"] });
    },
  });

  const docs = data ?? [];
  const totalPages = totalCount ? Math.max(1, Math.ceil(totalCount / PAGE_SIZE)) : 1;

  return (
    <AppLayout>
      <div className="flex items-center justify-between mb-6">
        <h1 className="font-display text-2xl font-bold">
          Documents {totalCount !== undefined && <span className="text-slate-500 text-base font-normal">({totalCount.toLocaleString()})</span>}
        </h1>
        <div className="flex items-center gap-2 bg-industrial-bg border border-industrial-border rounded-lg px-3 py-1.5 w-72">
          <Search size={14} className="text-slate-500" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Filter by filename"
            className="bg-transparent outline-none text-sm w-full"
          />
        </div>
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-white/5 text-slate-400 text-xs uppercase">
            <tr>
              <th className="text-left px-4 py-3">Document</th>
              <th className="text-left px-4 py-3">Category</th>
              <th className="text-left px-4 py-3">Status</th>
              <th className="text-left px-4 py-3">Chunks</th>
              <th className="text-left px-4 py-3">Uploaded</th>
              <th className="text-right px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr><td colSpan={6} className="px-4 py-6 text-slate-500 text-center">Loading documents...</td></tr>
            ) : docs.length === 0 ? (
              <tr><td colSpan={6} className="px-4 py-6 text-slate-500 text-center">No documents found.</td></tr>
            ) : (
              docs.map((doc) => (
                <tr key={doc.id} className="border-t border-industrial-border hover:bg-white/5">
                  <td className="px-4 py-3 flex items-center gap-2">
                    <FileText size={16} className="text-industrial-accent2" />
                    {doc.filename}
                  </td>
                  <td className="px-4 py-3 text-slate-400">{doc.doc_category ?? "—"}</td>
                  <td className="px-4 py-3">
                    <span className={`badge ${STATUS_COLORS[doc.status] ?? ""}`}>{doc.status}</span>
                    {doc.ocr_used && <span className="badge border-industrial-border text-slate-400 ml-2">OCR</span>}
                  </td>
                  <td className="px-4 py-3 text-slate-400">{doc.chunk_count}</td>
                  <td className="px-4 py-3 text-slate-500">{new Date(doc.uploaded_at).toLocaleString()}</td>
                  <td className="px-4 py-3 text-right">
                    <button onClick={() => del.mutate(doc.id)} className="text-slate-500 hover:text-industrial-danger transition">
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {totalCount !== undefined && totalCount > PAGE_SIZE && (
        <div className="flex items-center justify-between mt-4 text-sm text-slate-400">
          <div>
            Page {page + 1} of {totalPages}
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className="btn-secondary flex items-center gap-1 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <ChevronLeft size={16} /> Prev
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
              disabled={page >= totalPages - 1}
              className="btn-secondary flex items-center gap-1 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Next <ChevronRight size={16} />
            </button>
          </div>
        </div>
      )}
    </AppLayout>
  );
}
