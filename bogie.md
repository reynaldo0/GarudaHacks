# PROJECT THEMIS V6
# Bogie Predictive Maintenance Brief

> **Module Name**
>
> Bogie Predictive Maintenance (CALES + RUL + OPEX)

---

# Objective

Modul Bogie Predictive Maintenance bertujuan untuk mengubah data kepadatan penumpang menjadi indikator kesehatan bogie secara **real-time**.

Sistem **tidak mendiagnosis kerusakan bogie**, melainkan memberikan **indikator pendukung** untuk membantu petugas maintenance menentukan prioritas inspeksi lebih awal berdasarkan pola pembebanan gerbong.

Output modul ini digunakan sebagai **decision support system**, bukan pengganti inspeksi fisik.

---

# Core Philosophy

Occupancy bukan tujuan akhir.

Occupancy adalah indikator beban.

Beban digunakan untuk menghitung distribusi massa pada setiap gerbong.

Distribusi massa digunakan untuk memperkirakan akumulasi stres pada bogie.

Akumulasi stres digunakan untuk menentukan prioritas maintenance.

Pipeline:

```text
Occupancy Detection
        │
Fusion Engine
        │
pax_per_m²
        │
CALES
        │
Health Index
        │
Damage Multiplier
        │
Remaining Useful Life
        │
OPEX Estimation
        │
Inspection Priority
```

---

# Principle

AI **tidak pernah mengatakan bogie rusak.**

AI hanya mengatakan:

> Gerbong ini memiliki pola pembebanan yang membuatnya layak diperiksa lebih dahulu dibanding gerbong lain.

Keputusan akhir tetap berada pada teknisi maintenance.

---

# Input

Per gerbong:

- platform_headcount
- cabin_headcount
- fused_headcount
- floor_area_m2
- pax_per_m2
- occupancy_percent
- confidence
- timestamp

---

# Step 1 — Density Calculation

```text
pax_per_m²

=

headcount

/

floor_area_m²
```

Semua analisis bogie menggunakan metric ini.

Bukan occupancy_percent.

---

# Step 2 — CALES

CALES
(Cumulative Asymmetric Load Exposure Score)

Mengukur:

- tingkat pembebanan
- ketidakseimbangan beban
- durasi pembebanan

Output:

```text
GREEN

YELLOW

ORANGE

RED
```

Status ini terus bertambah secara kumulatif selama kereta beroperasi.

---

# Step 3 — Asymmetry Analysis

AI membandingkan density satu gerbong dengan rata-rata seluruh formasi.

```text
Asymmetry Ratio

=

Density Car

/

Average Density Formation
```

Semakin besar selisihnya

↓

Semakin besar beban bogie.

---

# Step 4 — Severity Weight

Asymmetry Ratio

↓

Severity Weight

↓

Damage Weight

Semakin lama overload terjadi,

semakin besar skor CALES.

---

# Step 5 — Health Index

Selain warna CALES,

setiap gerbong mempunyai Health Index.

Contoh

```text
100%

↓

95%

↓

82%

↓

61%

↓

38%
```

Health Index digunakan untuk visualisasi dashboard.

Semakin kecil nilainya

↓

Semakin tinggi prioritas inspeksi.

---

# Step 6 — Damage Multiplier

Status CALES diterjemahkan menjadi multiplier.

| Status | Multiplier |
|----------|-----------|
| GREEN | 1.0x |
| YELLOW | 1.0x |
| ORANGE | 2.5x |
| RED | 3.0x |

Semakin tinggi multiplier,

semakin cepat umur komponen berkurang.

---

# Step 7 — Remaining Useful Life (RUL)

Komponen yang dimonitor:

## Wheel Flange

Nominal Life

```text
12 bulan
```

---

## Air Spring

Nominal Life

```text
192 bulan
```

---

## Chevron Rubber

Nominal Life

```text
72 bulan
```

---

Setelah multiplier diterapkan

AI menghitung

```text
Effective Life

↓

Remaining Months
```

Contoh

```text
Wheel Flange

Nominal

12 bulan

↓

RED

↓

Effective

4 bulan

↓

Remaining

2.7 bulan
```

---

# Step 8 — OPEX Estimation

AI menghitung estimasi biaya apabila inspeksi ditunda.

Kategori:

| Perawatan | Estimasi |
|-----------|----------|
| Wheel Reprofile | Rp15–25 juta |
| Air Spring/Bogie Overhaul | > Rp150 juta |
| Catastrophic Derailment | > Rp2 miliar |

Tujuan utama:

Memberikan estimasi potensi penghematan biaya melalui deteksi dini.

---

# Step 9 — Inspection Priority

Output akhir bukan status kerusakan.

Melainkan urutan inspeksi.

Contoh

```text
Priority #1

Car 4

RED

↓

Priority #2

Car 7

ORANGE

↓

Priority #3

Car 2

YELLOW
```

---

# Dashboard Output

Setiap gerbong menampilkan:

- Health Index
- CALES Status
- Asymmetry Ratio
- Current pax_per_m²
- Damage Multiplier
- Remaining Useful Life
- Estimated OPEX
- Inspection Priority
- Recommended Action

---

# Recommended Actions

| Status | Action |
|----------|---------|
| GREEN | Continue Monitoring |
| YELLOW | Schedule Inspection |
| ORANGE | Priority Inspection |
| RED | Immediate Depot Inspection |

---

# Future Roadmap

Tahap produksi dapat menambahkan integrasi:

- Vibration Sensor
- Axle Temperature Sensor
- Air Spring Pressure Sensor
- Wheel Profile Measurement
- Bearing Temperature
- IoT Telemetry

Sehingga Health Index tidak hanya berdasarkan occupancy,

tetapi juga berdasarkan kondisi fisik bogie.

---

# Important Disclaimer

PROJECT THEMIS tidak mengklaim mampu mendeteksi kerusakan bogie secara langsung.

CALES, RUL, Health Index, dan OPEX merupakan **indikator pendukung (supporting indicators)** yang digunakan untuk menentukan prioritas inspeksi maintenance.

Keputusan akhir tetap dilakukan melalui inspeksi fisik oleh teknisi sesuai SOP operator kereta.

docker run -d \
  --name themis-postgres \
  --restart unless-stopped \
  -e POSTGRES_DB=themis \
  -e POSTGRES_USER=themis \
  -e POSTGRES_PASSWORD=reynaldo \
  -p 5432:5432 \
  -v themis_postgres_data:/var/lib/postgresql/data \
  postgres:16


Host     : localhost
Port     : 5432
Database : themis
Username : themis
Password : reynaldo
