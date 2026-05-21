# Hướng dẫn deploy & cập nhật sau này

Dự án gồm **3 phần tách riêng** — deploy từng phần, cập nhật bằng **Git push** (không cần upload tay).

```
[GitHub/GitLab]  ──push──►  Frontend (Vercel/Netlify)
                ──push──►  Backend (Render/Railway)
                ──SQL──►   Supabase (database, ít đổi)
```

---

## Bước 0: Đưa code lên Git (bắt buộc để cập nhật dễ)

Từ thư mục repo (ví dụ `tri_tue_nhan_tao` hoặc `Visualization`):

```powershell
git init
git add Visualization/
git commit -m "AI visualizer FastAPI + React"
git remote add origin https://github.com/<user>/<repo>.git
git push -u origin main
```

**Sau này mỗi lần sửa code:** `git add` → `git commit` → `git push` → hosting **tự build lại** (1–3 phút).

---

## Bước 1: Supabase (một lần, hoặc khi đổi schema)

1. [supabase.com](https://supabase.com) → New project.
2. **SQL Editor** → dán file `supabase/migrations/001_search_runs.sql` → Run.
3. Lưu lại:
   - **Project URL** → `SUPABASE_URL`
   - **Settings → API → service_role** (secret) → `SUPABASE_SERVICE_ROLE_KEY`

Không đưa service role vào frontend.

---

## Bước 2: Deploy Backend (API Python)

### Cách A — Render (miễn phí tier, dễ)

1. [render.com](https://render.com) → **New → Blueprint** hoặc **Web Service**.
2. Kết nối repo GitHub; **Root Directory** = `Visualization` (nếu repo là `tri_tue_nhan_tao`, đặt root là thư mục chứa `backend/` và `thuat_toan/`).
3. Dùng file `render.yaml` có sẵn trong repo, hoặc cấu hình tay:

| Mục | Giá trị |
|-----|---------|
| Runtime | Python 3.11+ |
| Build | `pip install -r backend/requirements.txt` |
| Start | `cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

4. **Environment variables:**

| Biến | Ví dụ |
|------|--------|
| `SUPABASE_URL` | `https://xxx.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | `eyJ...` |
| `CORS_ORIGINS` | `https://your-app.vercel.app` (sửa sau khi có URL frontend) |

5. Deploy → copy URL dạng `https://ai-visualizer-api.onrender.com`.

**Kiểm tra:** mở `https://<api-url>/api/health` → `{"status":"ok",...}`.

### Cách B — Docker (VPS, Railway, Fly…)

```powershell
cd Visualization
docker build -t ai-visualizer-api .
docker run -p 8000:8000 -e SUPABASE_URL=... -e SUPABASE_SERVICE_ROLE_KEY=... -e CORS_ORIGINS=https://... ai-visualizer-api
```

---

## Bước 3: Deploy Frontend (React tĩnh)

### Vercel (khuyên dùng)

1. [vercel.com](https://vercel.com) → Import Git repo.
2. **Root Directory:** `Visualization/frontend` (hoặc `frontend` nếu root repo là `Visualization`).
3. Framework: **Vite** (tự nhận).
4. **Environment variable:**

| Biến | Giá trị |
|------|---------|
| `VITE_API_URL` | URL backend **không** có slash cuối, ví dụ `https://ai-visualizer-api.onrender.com` |

5. Deploy → URL dạng `https://your-app.vercel.app`.

### Netlify (tương tự)

- Base directory: `frontend`
- Build: `npm run build`
- Publish: `dist`
- Env: `VITE_API_URL` = URL backend

**Quan trọng:** Sau khi có URL frontend, quay lại Render → sửa `CORS_ORIGINS` = URL Vercel (có thể nhiều domain, cách nhau bằng dấu phẩy) → **Redeploy** backend.

---

## Bước 4: Luồng cập nhật trong tương lai

| Bạn sửa | Push Git | Tự động |
|---------|----------|---------|
| `frontend/src/...` | `git push` | Vercel build lại frontend |
| `backend/...` hoặc `thuat_toan/...` | `git push` | Render build lại API |
| SQL schema mới | Chạy migration trên Supabase SQL Editor | Không auto — làm tay 1 lần |

**Quy trình làm việc gợi ý:**

```
main          → production (auto deploy)
develop       → optional preview deploy
feature/xxx   → PR → merge vào main → production cập nhật
```

**Chỉ đổi biến môi trường** (URL API, Supabase): sửa trên dashboard Render/Vercel → Redeploy, **không** cần đổi code.

---

## Checklist trước go-live

- [ ] `GET <API>/api/health` → OK
- [ ] Frontend mở được, APPLY 8-puzzle chạy (không lỗi CORS)
- [ ] `CORS_ORIGINS` khớp domain frontend
- [ ] `VITE_API_URL` trỏ đúng backend production
- [ ] Supabase migration đã chạy (nếu cần lưu lịch sử)

---

## Lỗi thường gặp

| Triệu chứng | Cách xử lý |
|-------------|------------|
| CORS error trên trình duyệt | Thêm URL frontend vào `CORS_ORIGINS`, redeploy backend |
| `Failed to fetch` / 404 API | Kiểm tra `VITE_API_URL`; build lại frontend sau khi đổi env |
| Render sleep (free) | Lần đầu mở app chờ ~30s cold start |
| Supabase không lưu | Kiểm tra `SUPABASE_*` trên Render; bảng `search_runs` đã tạo |

---

## Chạy local vẫn như cũ

```powershell
# Terminal 1
cd Visualization\backend
pip install -r requirements.txt
python run.py

# Terminal 2 (cần Node.js)
cd Visualization\frontend
npm install
npm run dev
```

Local không cần `VITE_API_URL` (Vite proxy `/api` → `localhost:8000`).
