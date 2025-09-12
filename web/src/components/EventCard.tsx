"use client";
import { useState } from "react";

export type EventPayload = any;

export default function EventCard({ event }: { event: { type: string; payload?: EventPayload } }) {
  const p = event?.payload ?? {};
  const author = (p as any)?.author ?? (p as any)?.actions?.author ?? "";
  const content = (p as any)?.content ?? {};
  const parts: any[] = Array.isArray((content as any)?.parts) ? (content as any).parts : [];

  // Extract displayable bits from the first part only (for brevity)
  const first = parts[0] || {};
  const text = typeof p === "string" ? null : first?.text ?? null;
  const functionCall = first?.functionCall ?? null;
  const functionResponse = first?.functionResponse ?? null;
  const functionCallDisplay = functionCall ? { name: functionCall?.name, args: functionCall?.args } : null;
  const functionResponseDisplay = functionResponse ? { name: functionResponse?.name, response: functionResponse?.response } : null;

  const hasContent = !!(text || functionCallDisplay || functionResponseDisplay);
  if (!hasContent && !author) return null;

  const isFinal = author === "final_analizer_agent" || author === "crystalens_root_agent";
  const [showFullText, setShowFullText] = useState(false);
  const [showFullCall, setShowFullCall] = useState(false);
  const [showFullResp, setShowFullResp] = useState(false);

  const MAX_TEXT = 700;
  const MAX_JSON = 800;

  const textOverflow = !!(text && text.length > MAX_TEXT && !isFinal);
  const textToRender = textOverflow && !showFullText ? text?.slice(0, MAX_TEXT) + "…" : text;

  const callJson = functionCallDisplay ? JSON.stringify(functionCallDisplay, null, 2) : "";
  const callOverflow = !!(callJson && callJson.length > MAX_JSON && !isFinal);
  const callToRender = callOverflow && !showFullCall ? callJson.slice(0, MAX_JSON) + "…" : callJson;

  const respJson = functionResponseDisplay ? JSON.stringify(functionResponseDisplay, null, 2) : "";
  const respOverflow = !!(respJson && respJson.length > MAX_JSON && !isFinal);
  const respToRender = respOverflow && !showFullResp ? respJson.slice(0, MAX_JSON) + "…" : respJson;

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm animate-fade-in-up">
      <div className="flex items-center justify-end">
        {author ? (
          <span className="inline-flex items-center rounded-full bg-[#d68e2f] px-2.5 py-1 text-xs font-medium text-white">
            by <span className="ml-1 font-semibold text-white/95">{author}</span>
          </span>
        ) : null}
      </div>

      {textToRender ? (
        <div className="mt-2 whitespace-pre-wrap text-[15px] leading-relaxed text-slate-800">
          {textToRender}
          {textOverflow ? (
            <button onClick={() => setShowFullText((v) => !v)} className="ml-2 text-xs font-medium text-[#d6512f] hover:underline">
              {showFullText ? "Show less" : "Show more"}
            </button>
          ) : null}
        </div>
      ) : null}

      {functionCallDisplay ? (
        <div className="mt-2 text-sm">
          <div className="mb-1 font-semibold text-slate-700">functionCall</div>
          <pre className="m-0 whitespace-pre-wrap rounded-lg bg-slate-50 p-3 text-slate-800 shadow-inner">{callToRender}</pre>
          {callOverflow ? (
            <button onClick={() => setShowFullCall((v) => !v)} className="mt-1 text-xs font-medium text-[#d6512f] hover:underline">
              {showFullCall ? "Show less" : "Show more"}
            </button>
          ) : null}
        </div>
      ) : null}

      {functionResponseDisplay ? (
        <div className="mt-2 text-sm">
          <div className="mb-1 font-semibold text-slate-700">functionResponse</div>
          <pre className="m-0 whitespace-pre-wrap rounded-lg bg-slate-50 p-3 text-slate-800 shadow-inner">{respToRender}</pre>
          {respOverflow ? (
            <button onClick={() => setShowFullResp((v) => !v)} className="mt-1 text-xs font-medium text-[#d6512f] hover:underline">
              {showFullResp ? "Show less" : "Show more"}
            </button>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
