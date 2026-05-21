# AI Agent Visualizer (FastAPI + React)

Ứng dụng trực quan hóa BFS/DFS cho **8-Puzzle** và **máy hút bụi**, tách thành 3 phần để deploy.

## Cấu trúc

```
Visualization/
├── thuat_toan/     # 4 thuật toán: bfs, dfs, bfs_goal_on_generate, dfs_goal_on_generate
├── backend/        # FastAPI + Supabase
├── frontend/       # React (Vite) — theme pixel game (teal/coral)
└── supabase/       # Migration SQL
```

## Thuật toán

| ID    | File                    | Mô tả                          |
|-------|-------------------------|--------------------------------|
| bfs1  | `bfs.py`                | BFS — goal khi dequeue         |
| bfs2  | `bfs_goal_on_generate.py` | BFS — goal khi sinh state    |
| dfs1  | `dfs.py`                | DFS — goal khi pop stack       |
| dfs2  | `dfs_goal_on_generate.py` | DFS — goal khi sinh state    |

## Supabase

1. Tạo project trên [supabase.com](https://supabase.com).
2. Chạy `supabase/migrations/001_search_runs.sql` trong SQL Editor.
3. Copy URL và **service role key** vào `backend/.env`:

```env
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
CORS_ORIGINS=http://localhost:5173
```

> **Lưu ý:** Service role chỉ dùng ở backend, không đưa vào frontend.

## Chạy local

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
copy .env.example .env   # rồi sửa biến môi trường
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Mở http://localhost:5173 — proxy `/api` → backend.

## API

- `GET /api/health`
- `POST /api/search/puzzle` — `{ algorithm, board: number[9] }`
- `POST /api/search/vacuum` — robot, dirt, room, `timeout_sec`
- `GET /api/search/history` — lịch sử từ Supabase

Response gồm `steps`, `path`, `tree` (biểu đồ cây cho panel).

## Panel biểu đồ cây

Trong **Search Trace**, bấm **BIỂU ĐỒ CÂY** để mở modal SVG hiển thị quan hệ cha–con khi expand.

## Deploy & cập nhật sau này

Xem **[DEPLOY.md](./DEPLOY.md)** — Git push → Vercel (frontend) + Render (backend) + Supabase.

Tóm tắt:

1. Code trên **GitHub** (bắt buộc để auto-deploy).
2. **Supabase:** chạy migration SQL một lần.
3. **Render:** backend (`render.yaml` có sẵn).
4. **Netlify** (hoặc Vercel): frontend, base `frontend/`, env `VITE_API_URL` = URL API.
5. Sửa `CORS_ORIGINS` trên backend = URL Netlify/Vercel.
6. **Cập nhật tương lai:** `git push` → hosting tự build lại.

## Bản Tkinter cũ

`app.py` và `search_adapters.py` ở thư mục gốc vẫn giữ để tham chiếu; phiên bản mới dùng `thuat_toan/` + API.
