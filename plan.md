MASTER PHASE PLAN — PROJECT THEMIS V6**

### **STATUS SAAT INI**
- **Backend**: Python/FastAPI, 20 kamera (2 per gerbong), YOLO person detection
- **Unity**: Digital Twin dengan 2 flat kamera per gerbong, spawn capsule penumpang
- **Frontend**: Next.js dashboard
- **Database**: PostgreSQL dengan 7 tabel (person-counting based)
- **ESP32**: Belum ada kode sama sekali
- **Versi**: Campuran antara 5.0, 7.0, dan V6

---

### **PHASE 0: FOUNDATION RESET** *(Minggu 1)*
> Tujuan: Membersihkan fondasi agar seluruh kode berbicara bahasa yang sama

| # | File | Perubahan | Alasan |
|---|------|-----------|--------|
| 1 | `settings.py` | Hapus `PERSON_CLASS_ID`, `YOLO_CLASSES`. Tambah `SEGMENTATION_MODEL_PATH`, `DENSITY_RED_THRESHOLD`, `DENSITY_YELLOW_THRESHOLD`, `FLOOR_AREA_M2`, `NUM_CAMERAS_PER_CAR=4`, `CAMERA_TYPE="ceiling_fisheye"`. Update `APP_VERSION="6.0.0"` | V6 tidak lagi person-counting |
| 2 | `.env` | Update semua environment variable sesuai settings baru | Konsistensi |
| 3 | `models.py` (DB) | `OccupancyHistory`: ganti `detected_persons` → `occupancy_ratio`, `free_space_ratio`, `spatial_occupancy_score`, `density_indicator`. `CameraConfiguration`: ganti `camera_type` → `ceiling_fisheye`, `car_mapping` mendukung 4 cam/car. `DecisionHistory`: tambah `door_action`, `announcement` | DB harus mencerminkan data spatial |
| 4 | `schemas/occupancy.py` | Ganti seluruh `CarOccupancy` model: hapus `detected_persons`, tambah `occupancy_ratio`, `free_space_ratio`, `density_indicator`, `spatial_occupancy_score`. Buat `PipelineState` model baru sebagai response utama | Kontrak API baru |
| 5 | `lookup_table.py` | Ubah dari 20 kamera (2/car) → 40 kamera (4/car), type = `ceiling_fisheye` | 4 kamera fisheye per gerbong |
| 6 | `main.py` | Ganti inisialisasi engine: hapus `yolo_engine`, tambah `segmentation_engine`, `spatial_grid_engine`, `redistribution_engine`, `door_engine`, `announcement_engine` | Pipeline baru |

---

### **PHASE 1: AI PIPELINE REWRITE** *(Minggu 2-3)*
> Tujuan: Mengganti YOLO person detection dengan Spatial Occupancy Segmentation

| # | File | Perubahan | Alasan |
|---|------|-----------|--------|
| 1 | **BUAT BARU** `ai/spatial_engine.py` | Model segmentasi (bisa pakai MiDaS, DPT, atau custom U-Net) yang menghitung `occupied_space` vs `free_space`. Output: `occupancy_grid` ( NxM matrix per frame) | Core AI baru |
| 2 | **BUAT BARU** `ai/occupancy_grid.py` | Generate Occupancy Grid dari hasil segmentasi. Grid per kamera, lalu fuse 4 grid per gerbong | Spatial analysis |
| 3 | **BUAT BARU** `ai/density_classifier.py` | Threshold: `GREEN` (free_space > 60%), `YELLOW` (30-60%), `RED` (< 30%). Output: `density_indicator` + `spatial_occupancy_score` | Klasifikasi kepadatan |
| 4 | **UPDATE** `ai/video_adapter.py` | Tambah `undistort_fisheye()` menggunakan camera calibration matrix. Tambah `normalize_frame()` | Preprocessing fisheye |
| 5 | **BUAT BARU** `ai/floor_segmentation.py` | Floor Visibility Score berdasarkan segmentasi lantai (bukan warna `#e7d3a9` mentah) | Hybrid approach: YOLO tidak dipakai |
| 6 | **UPDATE** `ai/yolo_engine.py` | **HAPUS** atau convert menjadi optional module. **TIDAK DIGUNAKAN** dalam pipeline utama | V6 tidak pakai YOLO |
| 7 | **UPDATE** `ai/occupancy_engine.py` | Ganti input: bukan `person_count/capacity`, tapi `spatial_occupancy_score`. Output: `occupancy_ratio`, `free_space_ratio`, `density_indicator` | V6 metrics |
| 8 | **UPDATE** `ai/frame_receiver.py` | Tambah validasi: terima 4 frame sekaligus per gerbong (multi-file upload) | 4 kamera |

---

### **PHASE 2: CORE ENGINES REDESIGN** *(Minggu 3-4)*
> Tujuan: Menyelaraskan semua engine dengan data spatial

| # | File | Perubahan | Alasan |
|---|------|-----------|--------|
| 1 | **UPDATE** `ai/fusion_engine.py` | Bukan merge person count. Tapi merge 4 Occupancy Grids dari 4 kamera menjadi 1 Carriage Occupancy Map | Spatial fusion |
| 2 | **UPDATE** `ai/cales_engine.py` | Input: `spatial_occupancy_score` historis. Hitung CALES score (akumulasi beban). Output: `cales_score`, `health_index`, `damage_multiplier`, `inspection_priority` | Bogie predictive maintenance |
| 3 | **UPDATE** `ai/decision_engine.py` | Ganti logic: bukan `MOVE_PASSENGER`. Tapi `REDISTRIBUTION_RECOMMENDATION`, `DOOR_ACTION`, `ANNOUNCEMENT`. Buat Safety Chain: cek apakah ada target carriage dengan occupancy lebih rendah sebelum rekomendasikan buka pintu | Decision V6 |
| 4 | **BUAT BARU** `ai/redistribution_engine.py` | Setelah density diketahui, cari target carriage terbaik. Logic: jika current RED AND target < YELLOW, rekomendasi pindah | Redistribution AI |
| 5 | **BUAT BARU** `ai/door_engine.py` | Rule: IF density_indicator == "RED" AND recommended_target exists AND target occupancy < current → `door_action = "OPEN_MIDDLE"`. ELSE → `door_action = "CLOSE"` | Door automation |
| 6 | **BUAT BARU** `ai/announcement_engine.py` | Generate text announcement berdasarkan redistribution. Contoh: "Carriage 6 has available capacity. Passengers are advised to move to Carriage 6." | Speaker system |

---

### **PHASE 3: PIPELINE INTEGRATION** *(Minggu 4-5)*
> Tujuan: Menghubungkan seluruh engine menjadi satu pipeline utuh

| # | File | Perubahan | Alasan |
|---|------|-----------|--------|
| 1 | **REWRITE** `api/endpoints/frame.py` | Pipeline baru: `Receive 4 frames → Preprocess → Spatial Segmentation → Occupancy Grid → Density Classification → Fusion → CALES → Redistribution → Door Logic → Announcement → PipelineState` | Core pipeline V6 |
| 2 | **UPDATE** `api/endpoints/occupancy.py` | Response: `PipelineState` JSON format sesuai INSTRUCTION.md | Kontrak baru |
| 3 | **UPDATE** `api/endpoints/state.py` | Gunakan `PipelineState` sebagai response utama | Konsistensi |
| 4 | **UPDATE** `api/endpoints/recommendation.py` | Input: spatial occupancy scores. Logic tetap, tapi berdasarkan `spatial_occupancy_score` bukan `occupancy_percentage` | Spatial-based |
| 5 | **UPDATE** `core/state_manager.py` | Simpan `PipelineState` per gerbong. Hapus field `detected_persons`. Tambah `occupancy_ratio`, `density_indicator`, `door_action` | State baru |
| 6 | **UPDATE** `core/integration_hub.py` | Broadcast event baru: `pipeline_state_updated` (satu event berisi seluruh state). Hapus event `person_count_updated` | Satu payload |
| 7 | **UPDATE** `simulation/seeder.py` | Scenario berdasarkan `spatial_occupancy_score` (0.0-1.0), bukan `passengers` count | Simulation V6 |

---

### **PHASE 4: DATABASE MIGRATION** *(Minggu 5)*
> Tujuan: Migrasi database ke schema baru tanpa kehilangan data

| # | Task | Detail |
|---|------|--------|
| 1 | Buat migration script | `alembic revision --autogenerate` untuk perubahan schema |
| 2 | Migrate `OccupancyHistory` | Ganti kolom, drop `detected_persons`, tambah spatial columns |
| 3 | Migrate `CameraConfiguration` | Update `camera_type`, tambah 40 kamera entries |
| 4 | Seed data baru | Seed spatial occupancy data untuk testing |
| 5 | Backup strategy | Backup database lama sebelum migrate |

---

### **PHASE 5: UNITY DIGITAL TWIN UPDATE** *(Minggu 5-6)*
> Tujuan: Unity menerima PipelineState dan memvisualisasikan semuanya

| # | File | Perubahan | Alasan |
|---|------|-----------|--------|
| 1 | **REWRITE** `Camera/CameraSimulator.cs` | 4 kamera ceiling fisheye per gerbong. Setiap 5 detik capture. POST 4 frame sekaligus | 4 fisheye cameras |
| 2 | **UPDATE** `Train/TrainController.cs` | `CarData`: ganti `personCount/passengers` → `occupancyRatio`, `freeSpaceRatio`, `densityIndicator`, `doorAction`, `calesScore` | Data V6 |
| 3 | **UPDATE** `Train/CarController.cs` | Hapus `PassengerCount`, hapus spawn capsule penumpang. Ganti visualisasi: warna gerbong berdasarkan `density_indicator`. Tambah door animation (middle door open/close) | Visualisasi spatial |
| 4 | **UPDATE** `Managers/AppManager.cs` | Parse `PipelineState` JSON. Dispatch: lampu indicator, door animation, dashboard update | Single payload |
| 5 | **UPDATE** `Indicators/LEDIndicator.cs` | State: GREEN / YELLOW / RED (sudah ada, pastikan mapping ke `density_indicator`) | Sudah compatible |
| 6 | **UPDATE** `UI/OccupancyDisplay.cs` | Tampilkan: `occupancy_ratio`, `free_space_ratio`, `density_indicator`, `cales_score`, `inspection_priority` | Dashboard V6 |
| 7 | **BUAT BARU** `UI/BogieDashboard.cs` | Tampilkan Health Index, CALES Status, Damage Multiplier, RUL estimation | Bogie maintenance dashboard |
| 8 | **BUAT BARU** `Train/DoorController.cs` | Animasi pintu tengah: `OPEN_MIDDLE` ↔ `CLOSE`. Triggered oleh `door_action` dari PipelineState | Door animation |

---

### **PHASE 6: FRONTEND DASHBOARD UPDATE** *(Minggu 6)*

| # | File | Perubahan |
|---|------|-----------|
| 1 | `types/index.ts` | Ganti `CarOccupancy` type: `occupancyRatio`, `freeSpaceRatio`, `densityIndicator` |
| 2 | `hooks/useWebSocket.ts` | Parse `pipeline_state_updated` event |
| 3 | Dashboard components | Tambah Bogie Health panel, Spatial Occupancy map, Door status indicator |

---

### **PHASE 7: ESP32 INTEGRATION** *(Minggu 7)*

| # | Task | Detail |
|---|------|--------|
| 1 | ESP32 firmware | MQTT/HTTP client → terima command dari backend |
| 2 | Door actuator | `OPEN_MIDDLE` / `CLOSE` command |
| 3 | LED indicator | GREEN / YELLOW / RED |
| 4 | Speaker | Play announcement audio |

---

### **PHASE 8: TESTING & CONSISTENCY AUDIT** *(Minggu 7-8)*

| # | Task | Detail |
|---|------|--------|
| 1 | Unit tests | Setiap engine baru |
| 2 | Integration test | Full pipeline: frame upload → PipelineState |
| 3 | Load test | 10 gerbong × 4 kamera × 5 detik = 8 FPS |
| 4 | Architecture audit | Cek seluruh file, pastikan tidak ada lagi istilah "people counting" |
| 5 | Documentation | Update README, API docs, flowchart |

---

### **FILE YANG PERLU DIUBAH (TOTAL)**

| Komponen | Jumlah File | Urgency |
|----------|-------------|---------|
| Backend Config & Schema | 6 file | 🔴 Tinggi |
| Backend AI Engine | 8 file (5 update + 3 baru) | 🔴 Tinggi |
| Backend API | 5 file | 🔴 Tinggi |
| Backend Core | 3 file | 🟡 Sedang |
| Backend DB | 2 file | 🟡 Sedang |
| Backend Simulation | 1 file | 🟡 Sedang |
| Unity Scripts | 8 file (6 update + 2 baru) | 🔴 Tinggi |
| Frontend | 3 file | 🟡 Sedang |
| ESP32 | 1 firmware baru | 🟢 Rendah |
| **TOTAL** | **~37 file** | |

---

### **RISIKO & MITIGASI**

| Risiko | Mitigasi |
|--------|----------|
| Model segmentasi belum ada | Fase 1 bisa pakai placeholder/mock dulu, model ML di-training terpisah |
| Database migration data loss | Backup dulu, jalankan migration di staging |
| Unity camera change butuh scene rebuild | Buat prefab baru, jangan hapus yang lama |
| Frontend breaking change | Parallel version: lama & baru bisa jalan bersama sementara |

---

Apakah Anda ingin saya mulai eksekusi dari **Phase 0** sekarang? Atau ada phase yang ingin diprioritaskan/diubah terlebih dahulu?
