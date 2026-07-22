import { useState, useRef, useEffect } from "react";
import { useMutation } from "@tanstack/react-query";
import { Send, Bot, User as UserIcon, FileText } from "lucide-react";
import AppLayout from "../components/AppLayout";
import { sendChatMessage, type ChatSource } from "../lib/api";

interface Message {
  role: "user" | "assistant";
  text: string;
  confidence?: number;
  sources?: ChatSource[];
}

const SUGGESTIONS = [
  "Why did Pump P-101 fail?",
  "Show maintenance history for the last quarter",
  "Explain the SOP for Boiler B-12",
  "Show recent inspection findings",
];

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);
  const bottomRef = useRef<HTMLDivElement>(null);

  const mutation = useMutation({
    mutationFn: (message: string) => sendChatMessage(message, sessionId),
    onSuccess: (data) => {
      setSessionId(data.session_id);
      setMessages((prev) => [...prev, { role: "assistant", text: data.answer, confidence: data.confidence_score, sources: data.sources }]);
    },
  });

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  function send(text: string) {
    if (!text.trim()) return;
    setMessages((prev) => [...prev, { role: "user", text }]);
    mutation.mutate(text);
    setInput("");
  }

  return (
    <AppLayout>
      <h1 className="font-display text-2xl font-bold mb-6">Industrial AI Chat</h1>

      <div className="card flex flex-col h-[70vh]">
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-slate-500 mt-10">
              <Bot size={40} className="mx-auto mb-3 text-industrial-accent2" />
              <p className="mb-4">Ask a question about your equipment, maintenance history, or SOPs.</p>
              <div className="flex flex-wrap justify-center gap-2">
                {SUGGESTIONS.map((s) => (
                  <button key={s} onClick={() => send(s)} className="badge border-industrial-border text-slate-400 hover:text-slate-100 hover:border-industrial-accent2/50">
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((m, i) => (
            <div key={i} className={`flex gap-3 ${m.role === "user" ? "justify-end" : ""}`}>
              {m.role === "assistant" && <Bot size={22} className="text-industrial-accent2 shrink-0 mt-1" />}
              <div className={`max-w-2xl rounded-xl px-4 py-3 text-sm ${m.role === "user" ? "bg-industrial-accent/15 border border-industrial-accent/30" : "bg-white/5 border border-industrial-border"}`}>
                <p className="whitespace-pre-wrap">{m.text}</p>
                {m.confidence !== undefined && (
                  <div className="mt-2 text-xs text-slate-500">Confidence: {(m.confidence * 100).toFixed(0)}%</div>
                )}
                {m.sources && m.sources.length > 0 && (
                  <div className="mt-2 space-y-1 border-t border-industrial-border pt-2">
                    {m.sources.map((s, j) => (
                      <div key={j} className="flex items-center gap-1.5 text-xs text-industrial-accent2">
                        <FileText size={12} /> {s.filename} <span className="text-slate-600">({(s.score * 100).toFixed(0)}% match)</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              {m.role === "user" && <UserIcon size={22} className="text-slate-500 shrink-0 mt-1" />}
            </div>
          ))}

          {mutation.isPending && (
            <div className="flex gap-3">
              <Bot size={22} className="text-industrial-accent2 shrink-0 mt-1" />
              <div className="rounded-xl px-4 py-3 text-sm bg-white/5 border border-industrial-border text-slate-500">
                Retrieving relevant documents and generating an answer...
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <form
          onSubmit={(e) => { e.preventDefault(); send(input); }}
          className="border-t border-industrial-border p-4 flex items-center gap-3"
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask FactoryBrain AI..."
            className="flex-1 bg-industrial-bg border border-industrial-border rounded-lg px-4 py-2.5 outline-none text-sm"
          />
          <button type="submit" className="btn-primary flex items-center gap-2">
            <Send size={16} /> Send
          </button>
        </form>
      </div>
    </AppLayout>
  );
}
