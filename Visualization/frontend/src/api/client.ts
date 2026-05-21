import type { DirtSpot, SearchResult } from "../types";
import type { AlgorithmId } from "../types";

/** URL Render — phải set VITE_API_URL trên Netlify rồi build lại */
function getApiBase(): string {
  const raw = (import.meta.env.VITE_API_URL ?? "").trim();
  return raw.replace(/\/+$/, "");
}

const API_BASE = getApiBase();

function apiUrl(path: string): string {
  const p = path.startsWith("/") ? path : `/${path}`;
  if (!API_BASE) {
    // Không có env: gọi cùng host (chỉ work nếu Netlify proxy /api → Render)
    return p;
  }
  return `${API_BASE}${p}`;
}

function checkApiConfigured(): void {
  if (import.meta.env.PROD && !API_BASE) {
    console.warn(
      "[AI Visualizer] VITE_API_URL trống. Trên Netlify: Site settings → Environment variables → " +
        "VITE_API_URL = https://<ten-ban>.onrender.com → Deploy lại.",
    );
  }
}

checkApiConfigured();

async function parseError(res: Response): Promise<string> {
  if (res.status === 404) {
    return API_BASE
      ? `API 404: ${res.url} — kiểm tra URL Render và đường dẫn /api`
      : "API 404: Chưa cấu hình VITE_API_URL trên Netlify (hoặc chưa proxy /api → Render).";
  }
  const err = await res.json().catch(() => ({}));
  return (err as { detail?: string }).detail ?? res.statusText;
}

export function getConfiguredApiBase(): string {
  return API_BASE;
}

export async function checkHealth(): Promise<{ ok: boolean; message: string }> {
  try {
    const res = await fetch(apiUrl("/api/health"));
    if (!res.ok) {
      return { ok: false, message: await parseError(res) };
    }
    const data = await res.json();
    return { ok: true, message: String(data.status ?? "ok") };
  } catch {
    return {
      ok: false,
      message: API_BASE
        ? `Không kết nối được ${API_BASE}`
        : "Không kết nối API — cấu hình VITE_API_URL trên Netlify",
    };
  }
}

export async function searchPuzzle(
  algorithm: AlgorithmId,
  board: number[],
): Promise<SearchResult> {
  const res = await fetch(apiUrl("/api/search/puzzle"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ algorithm, board }),
  });
  if (!res.ok) {
    throw new Error(await parseError(res));
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
  const res = await fetch(apiUrl("/api/search/vacuum"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(await parseError(res));
  }
  return res.json();
}

export async function fetchHistory(limit = 10) {
  const res = await fetch(apiUrl(`/api/search/history?limit=${limit}`));
  if (!res.ok) return { enabled: false, items: [] };
  return res.json();
}
