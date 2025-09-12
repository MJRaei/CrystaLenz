"use client";
import { useEffect, useRef, useState } from "react";

export default function PromptForm({ onStart, onSubmitText }: { onStart: (runId: string) => void; onSubmitText?: (text: string) => void }) {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_HTTP}/api/runs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input }),
      });
      const data = await res.json();
      onStart(data.run_id);
      if (onSubmitText) onSubmitText(input);
      setInput("");
    } finally {
      setLoading(false);
    }
  };

  const taRef = useRef<HTMLTextAreaElement | null>(null);
  useEffect(() => {
    const el = taRef.current;
    if (!el) return;
    el.style.height = "0px";
    const next = Math.min(el.scrollHeight, 200); // cap at ~6-7 lines
    el.style.height = next + "px";
  }, [input]);

  const isEmpty = input.trim().length === 0;
  const formRef = useRef<HTMLFormElement | null>(null);

  return (
    <form ref={formRef} onSubmit={submit} className="flex items-start gap-2">
      <div className="relative flex-1">
        <textarea
          ref={taRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              formRef.current?.requestSubmit();
            }
          }}
          placeholder="Enter your task or question..."
          className="no-scrollbar max-h-80 min-h-[56px] w-full resize-none rounded-lg border border-slate-300 bg-white pr-12 pl-4 py-3 shadow-sm outline-none focus:ring-4 focus:ring-[#d68e2f]/30 focus:border-[#d68e2f] transition overflow-hidden"
        />
        <button
          disabled={loading}
          type="submit"
          className={`absolute right-2 ${isEmpty ? 'top-1/2 -translate-y-1/2 -mt-1' : 'bottom-3'} inline-flex h-10 w-10 items-center justify-center rounded-md bg-[#d6512f] text-white shadow hover:bg-[#c24728] active:bg-[#a83f25] disabled:opacity-60 transition`}
          aria-label="Send"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="h-5 w-5 transform rotate-180">
            <path d="M12 4.5a.75.75 0 0 1 .75.75v11.19l3.72-3.72a.75.75 0 1 1 1.06 1.06l-5 5a.75.75 0 0 1-1.06 0l-5-5a.75.75 0 1 1 1.06-1.06l3.72 3.72V5.25A.75.75 0 0 1 12 4.5z"/>
          </svg>
        </button>
      </div>
    </form>
  );
}
