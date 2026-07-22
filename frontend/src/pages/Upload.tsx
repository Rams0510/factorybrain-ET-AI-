import { useState, useRef } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { UploadCloud, FileCheck2, Loader2 } from "lucide-react";
import AppLayout from "../components/AppLayout";
import { uploadDocuments } from "../lib/api";

export default function Upload() {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (files: FileList) => uploadDocuments(files),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      queryClient.invalidateQueries({ queryKey: ["analytics"] });
      setSelectedFiles([]);
    },
  });

  function handleFiles(fileList: FileList | null) {
    if (!fileList) return;
    setSelectedFiles(Array.from(fileList));
    mutation.mutate(fileList);
  }

  return (
    <AppLayout>
      <h1 className="font-display text-2xl font-bold mb-6">Upload Documents</h1>

      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          handleFiles(e.dataTransfer.files);
        }}
        onClick={() => inputRef.current?.click()}
        className={`card p-12 flex flex-col items-center justify-center text-center cursor-pointer transition border-2 border-dashed ${
          isDragging ? "border-industrial-accent bg-industrial-accent/5" : "border-industrial-border"
        }`}
      >
        <UploadCloud size={48} className="text-industrial-accent mb-4" />
        <p className="font-semibold mb-1">Drag & drop files here, or click to browse</p>
        <p className="text-xs text-slate-500">
          Supports PDF, DOCX, XLSX, CSV, TXT, PNG, JPEG, ZIP, and email exports (.eml/.msg)
        </p>
        <input
          ref={inputRef}
          type="file"
          multiple
          hidden
          onChange={(e) => handleFiles(e.target.files)}
          accept=".pdf,.docx,.xlsx,.xls,.csv,.txt,.png,.jpg,.jpeg,.zip,.eml,.msg"
        />
      </div>

      {selectedFiles.length > 0 && (
        <div className="card p-5 mt-6">
          <h2 className="font-semibold mb-3">
            {mutation.isPending ? "Uploading & queuing for processing..." : "Upload complete"}
          </h2>
          <ul className="space-y-2">
            {selectedFiles.map((f) => (
              <li key={f.name} className="flex items-center gap-3 text-sm text-slate-300">
                {mutation.isPending ? (
                  <Loader2 size={16} className="animate-spin text-industrial-accent2" />
                ) : (
                  <FileCheck2 size={16} className="text-industrial-success" />
                )}
                {f.name}
                <span className="text-slate-600 text-xs ml-auto">{(f.size / 1024).toFixed(1)} KB</span>
              </li>
            ))}
          </ul>
          <p className="text-xs text-slate-500 mt-3">
            Each document is processed through OCR, parsing, entity extraction, embedding, and
            knowledge-graph indexing in the background — check the Documents page for status.
          </p>
        </div>
      )}

      {mutation.isError && (
        <p className="text-industrial-danger text-sm mt-4">Upload failed. Please try again.</p>
      )}
    </AppLayout>
  );
}
