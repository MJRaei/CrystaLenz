"use client";
import { useMemo, useState } from "react";

export default function PlotsView({ items }: { items: Array<{ kind: string; id: string; event?: any }> }) {
  const htmlFiles = useMemo(() => {
    const set = new Map<string, string>();
    for (const it of items) {
      if (it.kind !== "event") continue;
      const p = it.event?.payload ?? {};
      const figs = p?.actions?.stateDelta?.reporter_output?.figures || [];
      if (Array.isArray(figs)) {
        for (const f of figs) {
          if (typeof f === "string" && f.endsWith(".html")) {
            set.set(f, f);
          }
        }
      }
    }
    return Array.from(set.values());
  }, [items]);

  const [active, setActive] = useState<string | null>(htmlFiles[0] ?? null);

  if (htmlFiles.length === 0) {
    return <div className="text-sm text-slate-500">No plots yet.</div>;
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="mb-2 flex gap-2 overflow-x-auto">
        {htmlFiles.map((f) => (
          <button
            key={f}
            onClick={() => setActive(f)}
            className={`rounded-lg px-3 py-2 text-sm transition ${active === f ? "bg-[#d68e2f] text-white" : "bg-white/70 text-slate-700 border border-slate-200 hover:bg-white"}`}
            title={f}
          >
            {f.split("/").pop()}
          </button>
        ))}
      </div>
      {active ? (
        <iframe src={`${process.env.NEXT_PUBLIC_API_HTTP}/xrd_outputs/${active.split("/").pop()}`} className="h-[70vh] w-full rounded-lg border border-slate-200 bg-white shadow-sm" />
      ) : null}
    </div>
  );
}
