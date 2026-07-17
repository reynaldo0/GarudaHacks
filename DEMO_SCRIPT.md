# PROJECT THEMIS — Demo Script 30 Detik

## Persiapan Sebelum Recording

1. **Backend harus running** — `cd backend && python main.py`
2. **Frontend harus running** — `cd frontend && npm run dev`
3. **Load skenario `peak_hour` dulu** — supaya website langsung terlihat hidup saat demo dimulai:
   ```
   POST http://localhost:8005/api/v1/simulation/scenario/peak_hour
   ```
4. **Buka browser di `http://localhost:3000`** — Landing page
5. **Fullscreen browser** (F11)
6. **Matikan notifikasi desktop** agar tidak mengganggu

---

## Script 30 Detik — Detik per Detik

### DETIK 0-3: LANDING PAGE — Hero & Live Data
**Yang tampil:** Landing page THEMIS v6.0
**Yang terlihat di layar:**
- Logo THEMIS + badge "v6.0" di navbar
- Tombol hijau "Live" (koneksi WebSocket aktif)
- Judul besar: "Spatial Occupancy Intelligence for KRL Commuter Line"
- 4 KPI cards langsung terisi data:
  - Avg Occupancy: ~82% (kuning/merah)
  - RED Cars: 5
  - Warnings: 6
  - Uptime: berjalan
- **Train visualization SF6** terlihat hidup — gerbong 1-5 warna MERAH (terisi penuh), gerbong 6 KUNING
- Warnings feed muncul: "RED DENSITY — Gerbong X mencapai batas kritis"

**Yang diucapkan/narasi:**
> "THEMIS — Spatial Occupancy Intelligence untuk KRL Commuter Line. Real-time monitoring langsung dari kamera."

---

### DETIK 3-5: NAVIGASI KE DASHBOARD
**Aksi:** Klik tombol "Open Operation Center" (tombol gradient hijau-biru di hero)

**Yang tampil:** Halaman Dashboard (`/dashboard`)
**Yang terlihat di layar:**
- Sidebar kiri: Dashboard (active), Train Status, Frame Upload, History, Simulation
- 4 KPI cards: Avg Occupancy, RED Cars, Active Alerts, System Uptime
- **TrainOverview** — visual kereta SF6 samping dengan:
  - Gerbong 1-5 warna MERAH (occupancy tinggi)
  - Gerbong 6 warna KUNING
  - Badge "Penuh" (merah) di gerbong sumber
  - Badge "Tujuan" (hijau) di gerbong target
- **Occupancy Chart** — bar chart menunjukkan warna merah/kuning per gerbong

**Yang diucapkan/narasi:**
> "Dashboard menampilkan real-time spatial occupancy dengan visualisasi kereta langsung."

---

### DETIK 5-8: DETAIL DASHBOARD — Alert & AI Recommendation
**Aksi:** Scroll sedikit ke bawah (perlahan)

**Yang terlihat di layar:**
- **Alert Panel** — daftar warning aktif dengan severity CRITICAL (merah)
  - "RED DENSITY — Gerbong X mencapai batas kritis"
- **AI Recommendation Panel** — rekomendasi redistribusi:
  - "Gerbong 4 penuh → Gerbong 6 (Confidence: 87%)"
  - Label "#1 Best Choice"
  - Badge khusus wanita (pink) untuk gerbong 1 & 6
- **Timeline** — event log berjalan, setiap perubahan tercatat
- **System Health** — 8/8 status OK (Backend, AI, Database, dll)

**Yang diucapkan/narasi:**
> "AI Recommendation Engine merekomendasikan redistribusi penumpang dari gerbong penuh ke gerbong kosong. Semua status infrastruktur normal."

---

### DETIK 8-10: TRAIN STATUS — Detail Per Gerbong
**Aksi:** Klik "Train Status" di sidebar

**Yang tampil:** Halaman Train Status (`/train`)
**Yang terlihat di layar:**
- TrainOverview yang sama (visual kereta)
- Occupancy Chart
- **6 kartu detail gerbong** dalam grid 3 kolom:
  - Gerbong 1: 88% — Kosong: 12% — RED
  - Gerbong 2: 80% — Kosong: 20% — RED
  - Gerbong 3: 92% — Kosong: 8% — RED
  - Gerbong 4: 97% — Kosong: 3% — RED
  - Gerbong 5: 72% — Kosong: 28% — RED
  - Gerbong 6: 65% — Kosong: 35% — YELLOW

**Yang diucapkan/narasi:**
> "Detail spatial occupancy per gerbong — Gerbong 4 mencapai 97% penuh, sementara Gerbong 6 masih 65%."

---

### DETIK 10-14: UPLOAD FRAME — Proses AI Pipeline
**Aksi:** Klik "Frame Upload" di sidebar

**Yang tampil:** Halaman Frame Upload (`/upload`)
**Yang terlihat di layar:**
- **Car selector** — 6 tombol nomor gerbong (klik gerbong 3)
- **4 camera slots** — kosong, siap diisi
- Input Train ID: "SF6-001"
- Tombol "Upload & Analyze Gerbong 3"

**Aksi:** Upload 4 gambar test (siapkan 4 foto test di folder sebelumnya)
- Klik camera slot satu per satu → pilih gambar
- Atau drag & drop ke 4 slot

**Yang diucapkan/narasi:**
> "Operator dapat mengunggah frame dari 4 kamera ceiling fisheye per gerbong untuk dianalisis AI."

---

### DETIK 14-18: HASIL ANALISIS AI
**Aksi:** Klik tombol "Upload & Analyze Gerbong 3"

**Yang tampil:** Hasil Pipeline AI muncul di panel kanan
**Yang terlihat di layar:**
- **Density banner** — "Gerbong 3 — Density: RED" (latar merah)
- **4 metric cards:**
  - Occupancy: 92%
  - Free Space: 8%
  - Spatial Score: 0.92
  - CALES Score: 0.78
- **Info cards:**
  - Door Action: "hold_open"
  - Health Index: "78 / 100"
  - Recommended: "maintain current settings"
- **Redistribution alert** — "Recommended redistribution to Car 6"
- **Announcement text** — pesan pengumuman otomatis
- **Pipeline flow** — 10 langkah terurai di bawah

**Yang diucapkan/narasi:**
> "AI pipeline menganalisis dalam hitungan detik — occupancy, spatial score, door action, dan rekomendasi redistribusi langsung tersedia."

---

### DETIK 18-22: SIMULASI — Ganti Skenario
**Aksi:** Klik "Simulation" di sidebar

**Yang tampil:** Halaman Simulation (`/simulation`)
**Yang terlihat di layar:**
- 6 kartu skenario: Empty, Normal, Peak Hour, Holiday, Imbalanced, Emergency
- Skenario "Peak Hour" sedang aktif (badge "Active" + border glow)

**Aksi:** Klik skenario **"Imbalanced"**

**Yang terlihat di layar:**
- Banner sukses: "Scenario loaded successfully"
- Skenario "Imbalanced" sekarang aktif

**Yang diucapkan/narasi:**
> "Operator dapat memuat skenario simulasi untuk testing — ini adalah skenario imbalanced di mana penumpang menumpuk di satu sisi."

---

### DETIK 22-25: CEK IMBALANCED DI DASHBOARD
**Aksi:** Klik "Dashboard" di sidebar

**Yang terlihat di layar (data berubah!):**
- KPI cards berubah:
  - Avg Occupancy: ~53%
  - RED Cars: 3 (bukan 5 lagi)
  - Warnings: 3
- **TrainOverview** berubah drastis:
  - Gerbong 1, 2, 3: **MERAH** (97%, 94%, 90%)
  - Gerbong 4, 5, 6: **HIJAU** (20%, 10%, 5%)
  - Visual split kiri-merah, kanan-hijau
  - Badge "Penuh" di gerbong 1 (sumber)
  - Badge "Tujuan" di gerbong 6 (target)
- **AI Recommendation berubah:**
  - "Gerbong 1 → Gerbong 6 — Confidence: 92%"
  - Alasan: "Gerbong 1 penuh 97%, Gerbong 6 hanya 5%"

**Yang diucapkan/narasi:**
> "Data berubah secara real-time! AI menunjukkan distribusi tidak merata — penumpang menumpuk di gerbong 1-3, sementara gerbong 4-6 hampir kosong. Confidence redistribusi naik ke 92%."

---

### DETIK 25-28: HISTORY — Data Historis
**Aksi:** Klik "History" di sidebar

**Yang tampil:** Halaman History (`/history`)
**Yang terlihat di layar:**
- Dropdown time range: "Last 24 hours"
- 4 summary cards: Avg Occupancy, Peak Occupancy, Peak Time, Total Records
- **Data table** — baris-baris data historis dengan kolom:
  - Timestamp
  - Car (nomor gerbong)
  - Occupancy (progress bar + persentase)
  - Density badge (warna)

**Yang diucapkan/narasi:**
> "Semua data tersimpan di database MySQL — histori occupancy, density, dan setiap keputusan AI dapat diakses kapan saja."

---

### DETIK 28-30: KEMBALI KE LANDING — Closing
**Aksi:** Klik logo "THEMIS" di navbar atau buka tab baru ke `localhost:3000`

**Yang tampil:** Landing page kembali
**Yang terlihat di layar:**
- Live KPI cards masih berjalan
- Train visualization masih hidup
- Warnings feed ter-update
- Koneksi WebSocket hijau "Live"

**Yang diucapkan/narasi:**
> "THEMIS — AI-powered Railway Decision Intelligence. Dari kamera fisheye hingga keputusan real-time. Terima kasih."

---

## Checklist Sebelum Recording

| No | Item | Status |
|----|------|--------|
| 1 | Backend running (port 8005) | [ ] |
| 2 | Frontend running (port 3000) | [ ] |
| 3 | Load skenario `peak_hour` via API/Postman | [ ] |
| 4 | Browser fullscreen (F11) | [ ] |
| 5 | Notifikasi desktop dimatikan | [ ] |
| 6 | 4 foto test siap untuk upload frame | [ ] |
| 7 | Resolusi minimal 1920x1080 | [ ] |
| 8 | Koneksi WebSocket hijau (Live) | [ ] |
| 9 | Mouse cursor terlihat jelas | [ ] |
| 10 | Suara jelas (jika pakai narasi) | [ ] |

## Tips Recording

1. **Jangan terburu-buru** — beri jeda 0.5 detik antar navigasi supaya viewer bisa membaca
2. **Tunjukkan cursor** — gunakan software seperti [Mouse Pointer Highlight](https://learn.microsoft.com/en-us/windows/powertoys/) agar cursor terlihat
3. **Zoom browser 100%** — jangan zoom in/out agar layout konsisten
4. **Recording tool** — OBS Studio (gratis) atau Windows Game Bar (Win+G) untuk screen recording
5. **Video format** — MP4, minimal 1080p

## Urutan Navigasi (Ringkasan Cepat)

```
DETIK 0-5    → Landing page (tampilkan hero + live data)
DETIK 5-8    → Dashboard (scroll ke bawah lihat alerts & recommendation)
DETIK 8-10   → Train Status (detail per gerbong)
DETIK 10-18  → Frame Upload (upload foto + lihat hasil AI)
DETIK 18-22  → Simulation (ganti ke skenario "Imbalanced")
DETIK 22-25  → Dashboard (lihat data berubah real-time)
DETIK 25-28  → History (data historis di database)
DETIK 28-30  → Landing page (closing)
```

## Konten yang Harus Terlihat di Layar (Minimum)

1. **Koneksi real-time** — Tombol hijau "Live" + data berubah
2. **Visualisasi kereta** — 6 gerbong dengan warna dinamis
3. **AI Recommendation** — Rekomendasi redistribusi dengan confidence score
4. **Alert System** — Warning list dengan severity (CRITICAL/WARNING)
5. **AI Pipeline** — Upload frame → hasil analisis occupancy + density
6. **Simulasi interaktif** — Ganti skenario → data berubah langsung
7. **Database persistence** — History page menunjukkan data tersimpan
8. **6 gerbong SF6** — Formation SF6 terlihat konsisten di semua halaman

## API Calls yang Terjadi Saat Demo

| Detik | Endpoint | Method | Trigger |
|-------|----------|--------|---------|
| 0 | `/api/v1/state` | GET | Landing page mount |
| 0 | `/api/v1/occupancy` | GET | Landing page mount |
| 0 | `/api/v1/history/warnings` | GET | Landing page mount |
| 0 | `/ws` | WS | Landing page mount |
| 5 | (navigasi ke /dashboard) | — | Klik "Open Operation Center" |
| 10 | (navigasi ke /train) | — | Klik sidebar "Train Status" |
| 12 | (navigasi ke /upload) | — | Klik sidebar "Frame Upload" |
| 16 | `/api/v1/frame` | POST | Klik "Upload & Analyze" |
| 18 | (navigasi ke /simulation) | — | Klik sidebar "Simulation" |
| 20 | `/api/v1/simulation/scenario/imbalanced` | POST | Klik skenario "Imbalanced" |
| 22 | (navigasi ke /dashboard) | — | Klik sidebar "Dashboard" |
| 25 | (navigasi ke /history) | — | Klik sidebar "History" |
| 25 | `/api/v1/history` | GET | History page mount |
| 28 | (kembali ke landing) | — | Klik logo |

## Voice Recommendation (Bonus)

Saat AI Recommendation muncul, sistem otomatis membacakan announcement:
- Bahasa Indonesia: "Perhatian. Gerbong 4 penuh. Silakan berpindah ke Gerbong 6."
- Bahasa Inggris: "Attention. Car 4 is full. Please move to Car 6."

Pastikan speaker aktif saat recording untuk menunjukkan fitur ini.
