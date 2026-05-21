import type { DirtSpot, SearchResult } from "../types";
import type { AlgorithmId } from "../types";

const API_BASE = import.meta.env.VITE_API_URL ?? "";

export async function searchPuzzle(
  algorithm: AlgorithmId,
  board: number[],
): Promise<SearchResult> {
  const res = await fetch(`${API_BASE}/api/search/puzzle`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ algorithm, board }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail ?? res.statusText);
  }
  return res.json();
}

export async function searchVacuum(payload: {
  algorithm: AlgorithmId;
  robot_x: number;
  robot_y: number;
  dirt: DirtSpot[];
  room_x: number;
  room_y: number;
  room_w: number;
  room_h: number;
  cell_size: number;
  timeout_sec?: number | null;
}): Promise<SearchResult> {
  const res = await fetch(`${API_BASE}/api/search/vacuum`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail ?? res.statusText);
  }
  return res.json();
}

export async function fetchHistory(limit = 10) {
  const res = await fetch(`${API_BASE}/api/search/history?limit=${limit}`);
  if (!res.ok) return { enabled: false, items: [] };
  return res.json();
}
