# PROJECT THEMIS - Unity API Endpoints Reference

> Base URL: `http://localhost:8005`
> API Prefix: `/api/v1`
> Auth Header: `X-API-Key: themis-unity-key-2026`

---

## 1. `POST /api/v1/frame` — Upload Frame Kamera

Unity mengirim 4 gambar dari kamera fisheye ceiling ke backend untuk diproses AI pipeline.

### Unity Kirim

- **Header:** `X-API-Key: themis-unity-key-2026`
- **Content-Type:** `multipart/form-data`

| Field | Type | Required | Description |
|---|---|---|---|
| `files` | File[] | Yes | 4 file gambar JPEG/PNG dari 4 kamera fisheye |
| `camera_ids` | string (Form) | No | CSV camera IDs, e.g. `"cam01,cam02,cam03,cam04"` |
| `station_id` | string (Form) | No | ID stasiun, default `"unknown"` |
| `train_id` | string (Form) | No | ID kereta, default `"SF10-001"` |

### Backend Response

```json
{
  "success": true,
  "data": {
    "car_id": "car_04",
    "occupancy_ratio": 0.86,
    "free_space_ratio": 0.14,
    "density_indicator": "RED",
    "spatial_occupancy_score": 0.86,
    "recommended_target": "car_06",
    "door_action": "OPEN_MIDDLE",
    "announcement": "MOVE_TO_CAR_06",
    "cales_score": 0.82,
    "health_index": 100,
    "damage_multiplier": 1.0,
    "inspection_priority": 0,
    "recommended_action": "CONTINUE_MONITORING",
    "timestamp": "2026-07-17T12:00:00"
  }
}
```

### Field Reference

| Field | Type | Description |
|---|---|---|
| `car_id` | string | ID gerbong yang diproses |
| `occupancy_ratio` | float | Rasio okupansi (0.0 - 1.0) |
| `free_space_ratio` | float | Rasio ruang kosong (0.0 - 1.0) |
| `density_indicator` | string | `"GREEN"` / `"YELLOW"` / `"RED"` |
| `spatial_occupancy_score` | float | Skor okupansi spasial (0.0 - 1.0) |
| `recommended_target` | string/null | Gerbong tujuan rekomendasi |
| `door_action` | string | `"CLOSE"` / `"OPEN_MIDDLE"` / `"OPEN_ALL"` |
| `announcement` | string/null | Pesan announcement |
| `cales_score` | float | Skor CALES (kesehatan bogie) |
| `health_index` | float | Indeks kesehatan (0-100) |
| `damage_multiplier` | float | Pengali kerusakan |
| `inspection_priority` | int | Prioritas inspeksi (0 = normal) |
| `recommended_action` | string | Aksi yang direkomendasikan |
| `timestamp` | string | ISO 8601 timestamp |

---

## 2. `GET /api/v1/state` — Ambil Status Sistem

Mengembalikan status keseluruhan sistem: informasi kereta, distribusi density, warning aktif.

### Unity Kirim

Query parameter:
| Param | Type | Required | Description |
|---|---|---|---|
| `train_id` | string | No | ID kereta |

### Backend Response

```json
{
  "success": true,
  "data": {
    "timestamp": "2026-07-17T12:00:00",
    "station": {
      "id": "manggarai",
      "name": "Manggarai Station"
    },
    "train": {
      "id": "SF10-001",
      "formation": "SF10",
      "totalCars": 10,
      "avgOccupancyRatio": 0.65,
      "greenCars": 4,
      "yellowCars": 3,
      "redCars": 3
    },
    "occupancy": {
      "avgOccupancyRatio": 0.65,
      "greenCars": 4,
      "yellowCars": 3,
      "redCars": 3
    },
    "warning": {
      "id": "SF10-001-car_04-HIGH_OCCUPANCY",
      "isActive": true,
      "warningType": "HIGH_OCCUPANCY",
      "severity": "HIGH",
      "carId": 4,
      "trainId": "SF10-001",
      "message": "Car 04 occupancy at 86%",
      "timestamp": "2026-07-17T12:00:00"
    },
    "system": {}
  }
}
```

### Field Reference

| Field | Type | Description |
|---|---|---|
| `timestamp` | string | Waktu data diambil |
| `station.id` | string | ID stasiun |
| `station.name` | string | Nama stasiun |
| `train.id` | string | ID kereta |
| `train.formation` | string | Formasi kereta |
| `train.totalCars` | int | Jumlah total gerbong |
| `train.avgOccupancyRatio` | float | Rata-rata okupansi seluruh gerbong |
| `train.greenCars` | int | Jumlah gerbong hijau |
| `train.yellowCars` | int | Jumlah gerbong kuning |
| `train.redCars` | int | Jumlah gerbong merah |
| `warning` | object/null | Warning aktif terakhir (null jika tidak ada) |
| `warning.warningType` | string | Tipe warning |
| `warning.severity` | string | `"LOW"` / `"MEDIUM"` / `"HIGH"` / `"CRITICAL"` |
| `warning.carId` | int | Gerbong yang terdampak |
| `warning.message` | string | Pesan warning |

---

## 3. `GET /api/v1/occupancy` — Ambil Data Occupancy Semua Gerbong

Mengembalikan data okupansi lengkap untuk semua gerbong termasuk prediksi.

### Unity Kirim

Query parameter:
| Param | Type | Required | Description |
|---|---|---|---|
| `train_id` | string | No | ID kereta |

### Backend Response

```json
{
  "success": true,
  "data": {
    "trainId": "SF10-001",
    "station": "Manggarai",
    "timestamp": "2026-07-17T12:00:00",
    "cars": [
      {
        "carId": 1,
        "occupancyRatio": 0.35,
        "freeSpaceRatio": 0.65,
        "densityIndicator": "GREEN",
        "spatialOccupancyScore": 0.35,
        "cameraStatus": "active",
        "cameraId": "car01_cam01",
        "riskScore": 0.1,
        "prediction": {
          "trend": "stable",
          "predictedOccupancyRatio": 0.37,
          "confidence": 0.90,
          "horizonMinutes": 15
        }
      },
      {
        "carId": 2,
        "occupancyRatio": 0.52,
        "freeSpaceRatio": 0.48,
        "densityIndicator": "YELLOW",
        "spatialOccupancyScore": 0.52,
        "cameraStatus": "active",
        "cameraId": "car02_cam01",
        "riskScore": 0.4,
        "prediction": {
          "trend": "increasing",
          "predictedOccupancyRatio": 0.58,
          "confidence": 0.78,
          "horizonMinutes": 15
        }
      }
    ]
  }
}
```

### Field Reference

| Field | Type | Description |
|---|---|---|
| `carId` | int | Nomor gerbong |
| `occupancyRatio` | float | Rasio okupansi (0.0 - 1.0) |
| `freeSpaceRatio` | float | Rasio ruang kosong (0.0 - 1.0) |
| `densityIndicator` | string | `"GREEN"` / `"YELLOW"` / `"RED"` |
| `spatialOccupancyScore` | float | Skor okupansi spasial |
| `cameraStatus` | string | `"active"` / `"inactive"` |
| `cameraId` | string | ID kamera aktif |
| `riskScore` | float | Skor risiko |
| `prediction.trend` | string | `"stable"` / `"increasing"` / `"decreasing"` |
| `prediction.predictedOccupancyRatio` | float | Prediksi okupansi 15 menit ke depan |
| `prediction.confidence` | float | Confidence prediksi (0.0 - 1.0) |
| `prediction.horizonMinutes` | int | Horizon prediksi dalam menit |

---

## 4. `GET /api/v1/occupancy/{car_id}` — Ambil Occupancy 1 Gerbong

### Backend Response

```json
{
  "success": true,
  "data": {
    "carId": 4,
    "occupancyRatio": 0.86,
    "freeSpaceRatio": 0.14,
    "densityIndicator": "RED",
    "spatialOccupancyScore": 0.86,
    "riskScore": 0.8,
    "cameraStatus": "active",
    "cameraId": "car04_cam01",
    "prediction": {
      "trend": "increasing",
      "predictedOccupancyRatio": 0.92,
      "confidence": 0.85,
      "horizonMinutes": 15
    },
    "timestamp": "2026-07-17T12:00:00"
  }
}
```

### Jika Gerbong Tidak Ditemukan

```json
{
  "success": false,
  "data": {
    "message": "Car 99 not found"
  }
}
```

---

## 5. `GET /api/v1/recommendation` — Rekomendasi Redistribusi Penumpang

Menganalisis seluruh gerbong dan menghasilkan rekomendasi redistribusi berbasis okupansi spasial.

### Unity Kirim

Query parameter:
| Param | Type | Required | Description |
|---|---|---|---|
| `train_id` | string | No | ID kereta |

### Backend Response

```json
{
  "success": true,
  "data": {
    "fromCarId": 4,
    "fromOccupancy": 0.86,
    "congestionAvg": 0.55,
    "highestOccupancy": 0.86,
    "recommendedCars": [6, 7, 3],
    "recommendations": [
      {
        "action": "REDISTRIBUTION",
        "fromCarId": 4,
        "toCarId": 6,
        "confidence": 0.92,
        "reason": "Gerbong 4 86% -> Gerbong 6 30%.",
        "priority": 1,
        "label": "#1 Best Choice",
        "isWomenPriority": false,
        "score": 0.75
      },
      {
        "action": "REDISTRIBUTION",
        "fromCarId": 4,
        "toCarId": 1,
        "confidence": 0.80,
        "reason": "Gerbong 4 86% -> Gerbong 1 25%. (Khusus Wanita)",
        "priority": 2,
        "label": "#2 Alternative",
        "isWomenPriority": true,
        "score": 0.60
      }
    ],
    "timestamp": "2026-07-17T12:00:00"
  }
}
```

### Field Reference

| Field | Type | Description |
|---|---|---|
| `fromCarId` | int | Gerbong sumber (paling padat) |
| `fromOccupancy` | float | Okupansi gerbong sumber |
| `congestionAvg` | float | Rata-rata okupansi seluruh gerbong |
| `highestOccupancy` | float | Okupansi tertinggi |
| `recommendedCars` | int[] | Daftar nomor gerbong tujuan yang direkomendasikan |
| `recommendations[].action` | string | `"REDISTRIBUTION"` |
| `recommendations[].fromCarId` | int | Gerbong sumber |
| `recommendations[].toCarId` | int | Gerbong tujuan |
| `recommendations[].confidence` | float | Confidence rekomendasi (0.0 - 1.0) |
| `recommendations[].reason` | string | Alasan rekomendasi |
| `recommendations[].priority` | int | Urutan prioritas (1 = terbaik) |
| `recommendations[].label` | string | Label rekomendasi |
| `recommendations[].isWomenPriority` | bool | True jika gerbong khusus wanita (car 1 / car 10) |
| `recommendations[].score` | float | Skor rekomendasi |

### Jika Tidak Ada Rekomendasi

```json
{
  "success": true,
  "data": null
}
```

---

## 6. `GET /api/v1/history` — Riwayat Okupansi

### Unity Kirim

Query parameter:
| Param | Type | Required | Description |
|---|---|---|---|
| `hours` | int | No | Jumlah jam ke belakang (default: 24) |
| `car_id` | int | No | Filter per gerbong |

### Backend Response

```json
{
  "success": true,
  "data": {
    "query": { "hours": 24, "car_id": null },
    "records": [
      {
        "timestamp": "2026-07-17T12:00:00",
        "car_id": 4,
        "occupancy_ratio": 0.82,
        "density_indicator": "RED"
      }
    ],
    "summary": {
      "average_occupancy": 0.65,
      "peak_occupancy": 0.86,
      "peak_time": "08:30",
      "total_records": 24
    }
  }
}
```

---

## 7. `GET /api/v1/history/warnings` — Riwayat Warning

### Unity Kirim

Query parameter:
| Param | Type | Required | Description |
|---|---|---|---|
| `hours` | int | No | Jumlah jam ke belakang (default: 24) |

### Backend Response

```json
{
  "success": true,
  "data": {
    "warnings": [
      {
        "id": "SF10-001-car_04-HIGH_OCCUPANCY",
        "timestamp": "2026-07-17T12:00:00",
        "warningType": "HIGH_OCCUPANCY",
        "severity": "HIGH",
        "carId": 4,
        "message": "Car 04 occupancy at 86%",
        "trainId": "SF10-001",
        "isActive": true
      }
    ],
    "total": 1,
    "hours": 24,
    "timestamp": "2026-07-17T12:00:00"
  }
}
```

---

## 8. `GET /api/v1/config` — Konfigurasi Sistem

Mengembalikan konfigurasi penuh: formasi kereta, threshold density, daftar kamera, parameter AI.

### Backend Response

```json
{
  "success": true,
  "data": {
    "train": {
      "formation": "SF10",
      "totalCars": 10,
      "capacityPerCar": 200
    },
    "occupancy": {
      "greenThreshold": 0.4,
      "yellowThreshold": 0.7,
      "redThreshold": 0.9
    },
    "cameras": [
      {
        "id": "car01_cam01",
        "type": "ceiling_fisheye",
        "zone": "car_1",
        "carMapping": 1,
        "status": "online",
        "resolution": "640x640"
      }
    ],
    "ai": {
      "model": "Spatial Occupancy Segmentation",
      "confidence": 0.5,
      "imageSize": 640,
      "camerasPerCar": 4,
      "totalCameras": 40
    }
  }
}
```

### Field Reference

| Field | Type | Description |
|---|---|---|
| `train.formation` | string | Formasi kereta |
| `train.totalCars` | int | Total jumlah gerbong |
| `train.capacityPerCar` | int | Kapasitas per gerbong |
| `occupancy.greenThreshold` | float | Threshold GREEN |
| `occupancy.yellowThreshold` | float | Threshold YELLOW |
| `occupancy.redThreshold` | float | Threshold RED |
| `cameras[]` | array | Daftar semua kamera (40 total) |
| `cameras[].carMapping` | int | Nomor gerbong terkait |
| `ai.model` | string | Nama model AI |
| `ai.imageSize` | int | Ukuran input gambar |
| `ai.camerasPerCar` | int | Kamera per gerbong |
| `ai.totalCameras` | int | Total kamera |

---

## 9. `GET /api/v1/config/lookup-table` — Camera-to-Car Mapping

### Backend Response

```json
{
  "success": true,
  "data": {
    "mappings": [
      { "cameraId": "car01_cam01", "zone": "car_1", "carId": 1 },
      { "cameraId": "car01_cam02", "zone": "car_1", "carId": 1 },
      { "cameraId": "car01_cam03", "zone": "car_1", "carId": 1 },
      { "cameraId": "car01_cam04", "zone": "car_1", "carId": 1 }
    ]
  }
}
```

---

## 10. `POST /api/v1/simulation/scenario/{name}` — Load Scenario

### Backend Response

```json
{
  "success": true,
  "data": {
    "scenario": "rush_hour",
    "description": "Simulasi jam sibuk dengan okupansi tinggi",
    "cars_loaded": 10,
    "message": "Scenario 'rush_hour' loaded",
    "timestamp": "2026-07-17T12:00:00"
  }
}
```

### Jika Scenario Tidak Valid

```json
{
  "success": false,
  "error": "Invalid scenario. Valid: ['rush_hour', 'normal', 'empty']"
}
```

---

## 11. `POST /api/v1/simulation/reset` — Reset Simulation

### Backend Response

```json
{
  "success": true,
  "data": {
    "message": "Simulation reset successfully",
    "timestamp": "2026-07-17T12:00:00"
  }
}
```

---

## 12. `GET /health` — Health Check

### Backend Response

```json
{
  "status": "healthy",
  "version": "6.0.0"
}
```

---

## 13. WebSocket `ws://localhost:8005/ws` — Realtime Updates

Koneksi WebSocket persistent untuk menerima push data dari server secara real-time.

### Event Types yang Diterima Unity

```json
{
  "event": "pipeline_state_updated",
  "train_id": "SF10-001",
  "pipeline_state": {
    "car_id": "car_04",
    "occupancy_ratio": 0.86,
    "free_space_ratio": 0.14,
    "density_indicator": "RED",
    "spatial_occupancy_score": 0.86,
    "recommended_target": "car_06",
    "door_action": "OPEN_MIDDLE",
    "announcement": "MOVE_TO_CAR_06",
    "cales_score": 0.82,
    "health_index": 100,
    "damage_multiplier": 1.0,
    "inspection_priority": 0,
    "recommended_action": "CONTINUE_MONITORING",
    "timestamp": "2026-07-17T12:00:00"
  }
}
```

```json
{
  "event": "simulation_reset",
  "message": "Simulation reset"
}
```

---

## Unity Flow Summary

| Action | Endpoint | Method | Interval |
|---|---|---|---|
| Upload 4 frame kamera | `/api/v1/frame` | POST | Setiap 5 detik |
| Poll status sistem | `/api/v1/state` | GET | Periodic |
| Poll occupancy semua gerbong | `/api/v1/occupancy` | GET | Periodic |
| Poll occupancy 1 gerbong | `/api/v1/occupancy/{car_id}` | GET | On demand |
| Poll rekomendasi | `/api/v1/recommendation` | GET | Periodic |
| Riwayat okupansi | `/api/v1/history` | GET | On demand |
| Riwayat warning | `/api/v1/history/warnings` | GET | On demand |
| Konfigurasi sistem | `/api/v1/config` | GET | Startup |
| Camera mapping | `/api/v1/config/lookup-table` | GET | Startup |
| Load scenario simulasi | `/api/v1/simulation/scenario/{name}` | POST | On demand |
| Reset simulasi | `/api/v1/simulation/reset` | POST | On demand |
| Realtime push | `/ws` | WebSocket | Persistent |

---

## Threshold Reference

| Density | occupancy_ratio | Warna |
|---|---|---|
| LOW | 0.0 - 0.4 | GREEN |
| MEDIUM | 0.4 - 0.7 | YELLOW |
| HIGH | 0.7 - 0.9 | RED |
| CRITICAL | > 0.9 | RED |

---

## Door Action Reference

| door_action | Deskripsi |
|---|---|
| `CLOSE` | Pintu tetap tertutup |
| `OPEN_MIDDLE` | Buka pintu tengah |
| `OPEN_ALL` | Buka semua pintu |

---

## Density Indicator Reference

| density_indicator | arti |
|---|---|
| `GREEN` | Okupansi rendah, banyak ruang kosong |
| `YELLOW` | Okupansi sedang, mulai ramai |
| `RED` | Okupansi tinggi, padat |
