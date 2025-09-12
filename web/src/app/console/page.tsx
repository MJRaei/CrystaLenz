"use client";
import { useEffect, useRef, useState } from "react";
import PromptForm from "@/components/PromptForm";
import { useRunStream } from "@/lib/useRunStream";
import EventCard from "@/components/EventCard";
import PlotsView from "@/components/PlotsView";

type MessageItem =
  | { kind: "user"; id: string; text: string }
  | { kind: "event"; id: string; event: any };

type Filter = "agent" | "calls" | "responses" | "plots";

type Filter = "agent" | "calls" | "responses";

export default function ConsolePage() {
  const [runId, setRunId] = useState<string | undefined>(undefined);
  const { events } = useRunStream(runId);
  const [items, setItems] = useState<MessageItem[]>([]);
  const lastEventCountRef = useRef(0);
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const scrollRef = useRef<HTMLDivElement | null>(null);
  const [autoScroll, setAutoScroll] = useState(true);
  const [filter, setFilter] = useState<Filter>("agent");
  const [isRunning, setIsRunning] = useState(false);

  const getEventId = (ev: any, fallbackIndex: number): string => {
    const p = ev?.payload ?? {};
    return (
      p?.id || `${p?.author || "anon"}-${p?.timestamp || Date.now()}-${fallbackIndex}`
    );
  };

  // Classify an event into one bucket to avoid overlap
  const getEventCategory = (ev: any): Filter | null => {
    const p = ev?.payload ?? {};
    const parts: any[] = Array.isArray(p?.content?.parts) ? p.content.parts : [];
    let hasCall = false;
    let hasResp = false;
    let hasText = false;
    for (const part of parts) {
      if (part?.functionCall) hasCall = true;
      if (part?.functionResponse) hasResp = true;
      if (typeof part?.text === "string" && part.text.trim().length > 0) hasText = true;
    }
    if (hasCall) return "calls";
    if (hasResp) return "responses";
    if (hasText) return "agent";
    // If event contains figures paths, consider it plots
    const figures = (p as any)?.actions?.stateDelta?.reporter_output?.figures || [];
    if (Array.isArray(figures) && figures.some((f: string) => f.endsWith('.html'))) return "plots";
    return null;
  };

  // Append newly streamed events in order
  useEffect(() => {
    if (!events || events.length === lastEventCountRef.current) return;
    const newEvents = events.slice(lastEventCountRef.current);
    setItems((prev) => [
      ...prev,
      ...newEvents.map((ev, i) => ({ kind: "event", id: getEventId(ev, lastEventCountRef.current + i), event: ev })),
    ]);
    // Update running state based on terminal events
    for (const ev of newEvents) {
      if (ev?.type === "done" || ev?.type === "error") {
        setIsRunning(false);
      } else if (ev?.type === "status") {
        setIsRunning(true);
      }
    }
    lastEventCountRef.current = events.length;
  }, [events]);

  // Auto scroll to bottom on new items (only when near bottom)
  useEffect(() => {
    if (autoScroll) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [items, autoScroll]);

  const handleSubmitText = (text: string) => {
    setItems((prev) => [...prev, { kind: "user", id: `u-${prev.length}`, text }]);
  };
  const handleStartRun = (id: string) => {
    setRunId(id);
    setIsRunning(true);
  };

  const eventMatchesFilter = (ev: any): boolean => {
    const cat = getEventCategory(ev);
    if (!cat) return false;
    return cat === filter;
  };

  return (
    <main className="h-screen overflow-hidden flex flex-col p-6 pl-60">
      <div className="flex flex-1 min-h-0 gap-6">
        <aside className="fixed left-0 top-0 z-20 h-screen w-56 shrink-0 bg-[#f9f2e4] pt-2 border-r border-slate-200">
          <div className="mb-4 flex items-center gap-2 px-1">
            <img src="/logo.jpg" alt="CrystaLens logo" className="h-8 w-8 rounded-full object-cover" />
            <span className="text-lg font-semibold text-slate-900">CrystaLens</span>
          </div>
          <nav className="grid gap-2 px-1">
            <button onClick={() => setFilter("agent")} className={`rounded-lg px-3 py-2 text-sm text-left transition ${filter === "agent" ? "bg-[#d68e2f] text-white" : "bg-white/70 text-slate-700 border border-slate-200 hover:bg-white"}`}>Agent responses</button>
            <button onClick={() => setFilter("calls")} className={`rounded-lg px-3 py-2 text-sm text-left transition ${filter === "calls" ? "bg-[#d68e2f] text-white" : "bg-white/70 text-slate-700 border border-slate-200 hover:bg-white"}`}>Function calls</button>
            <button onClick={() => setFilter("responses")} className={`rounded-lg px-3 py-2 text-sm text-left transition ${filter === "responses" ? "bg-[#d68e2f] text-white" : "bg-white/70 text-slate-700 border border-slate-200 hover:bg-white"}`}>Function responses</button>
            <button onClick={() => setFilter("plots")} className={`rounded-lg px-3 py-2 text-sm text-left transition ${filter === "plots" ? "bg-[#d68e2f] text-white" : "bg-white/70 text-slate-700 border border-slate-200 hover:bg-white"}`}>Plots</button>
          </nav>
        </aside>

        <div className="flex min-w-0 min-h-0 flex-1 flex-col">

          <section
            ref={scrollRef}
            onWheel={() => setAutoScroll(false)}
            onTouchStart={() => setAutoScroll(false)}
            onScroll={() => {
              const el = scrollRef.current;
              if (!el) return;
              const distanceFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight;
              setAutoScroll(distanceFromBottom < 80);
            }}
            className="flex flex-1 flex-col gap-3 overflow-y-auto pb-24"
          >
            {filter !== "plots" ? (
              items.map((m) =>
                m.kind === "user"
                  ? (
                      filter === "agent" ? (
                        <div key={m.id} dir="ltr" className="ml-auto max-w-[80%] rounded-xl border border-slate-200 bg-slate-100 p-3 text-left text-slate-800 shadow-sm animate-fade-in-up">
                          {m.text}
                        </div>
                      ) : null
                    )
                  : eventMatchesFilter(m.event) ? (
                      <EventCard key={m.id} event={m.event as any} />
                    ) : null
              )
            ) : (
              <PlotsView items={items} />
            )}
            {isRunning ? (
              <div className="mt-2 flex items-center justify-start gap-2 text-xs text-slate-600">
                <span className="inline-block h-3 w-3 rounded-full border-2 border-[#d6512f] border-t-transparent animate-spin" />
                Running…
              </div>
            ) : null}
            <div ref={bottomRef} />
          </section>

          <div className="sticky bottom-0 z-10 -mx-6 border-t border-slate-200 bg-[#f9f2e4]/80 p-4 backdrop-blur supports-[backdrop-filter]:bg-[#f9f2e4]/60">
            <div className="mx-auto max-w-4xl">
              <PromptForm onStart={handleStartRun} onSubmitText={handleSubmitText} />
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
