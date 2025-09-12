"use client";
import { useEffect, useRef, useState } from "react";

export type RunEvent = {
  type: "status" | "result" | "error" | "done" | string;
  payload?: any;
};

export function useRunStream(runId?: string) {
  const wsRef = useRef<WebSocket | null>(null);
  const [events, setEvents] = useState<RunEvent[]>([]);

  useEffect(() => {
    if (!runId) return;
    const url = `${process.env.NEXT_PUBLIC_API_WS}/api/runs/${runId}/stream`;
    const ws = new WebSocket(url);
    wsRef.current = ws;
    ws.onmessage = (ev) => {
      try {
        const evt: RunEvent = JSON.parse(ev.data);
        setEvents((prev) => [...prev, evt]);
      } catch (e) {
        // ignore
      }
    };
    ws.onerror = () => ws.close();
    return () => ws.close();
  }, [runId]);

  return { events };
}
