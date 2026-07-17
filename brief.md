                 UNITY (Digital Twin)
                        │
                        │
      4 Camera Fisheye / Gerbong
                        │
      Capture JPEG / PNG setiap 5 detik
                        │
                        ▼
            POST /api/v1/camera/upload
                        │
                        ▼
                 FASTAPI Backend
                        │
                        ▼
           Image Preprocessing
    - Resize
    - Undistort Fisheye
    - Normalize
                        │
                        ▼
          AI Vision Engine (YOLO)
                        │
                        ▼
    Analisis ruang lantai (free floor area)
    BUKAN menghitung skeleton/manusia sebagai output utama
                        │
                        ▼
       Occupancy / Floor Visibility
                        │
                        ▼
    Density Classification
    🟢 Banyak lantai terlihat
    🟡 Sebagian tertutup
    🔴 Hampir seluruh lantai tertutup
                        │
                        ▼
        pax_per_m² / Density Score
                        │
        ┌───────────────┴───────────────┐
        ▼                               ▼
 CALES + Bogie Health            Redistribution AI
        ▼                               ▼
 RUL / OPEX                  Rule Engine
        │                               ▼
        │                      Backend Validation
        │                               ▼
        │                        Safety Chain
        │                               ▼
        │                     Door Recommendation
        └───────────────┬───────────────┘
                        ▼
              PipelineState Builder
                        ▼
        WebSocket / REST Response
                        ▼
                  UNITY Client
                        │
        ┌───────────────┴──────────────┐
        ▼                              ▼
  Lamp Indicator                 Door Animation
 Green / Yellow / Red           Middle Door Open

Di sini saya ingin memberi catatan teknis penting.

Kalau maksudnya adalah:

"YOLO tidak menghitung jumlah orang, tetapi menghitung seberapa banyak lantai yang masih terlihat."

Ini memungkinkan sebagai pendekatan desain, tetapi itu bukan cara kerja YOLO secara langsung.

YOLO adalah object detector. Secara bawaan ia mendeteksi objek seperti person, chair, bag, dan lain-lain—bukan menghitung luas lantai yang terlihat.

Kalau targetmu memang ingin menggunakan persentase lantai yang terlihat, pendekatan yang lebih tepat adalah salah satu dari berikut:

Semantic Segmentation
Model memisahkan area lantai dari area yang tertutup orang.
Output: persentase lantai yang masih terlihat.
Floor Occupancy Mask
Mendeteksi area lantai berwarna (misalnya mendekati #e7d3a9 jika memang itu representatif pada simulasi Unity).
Menghitung luas piksel lantai yang masih tampak.
Hybrid (yang saya rekomendasikan)
YOLO mendeteksi orang.
Dari hasil deteksi tersebut dihitung estimasi area lantai yang tertutup.
Sistem menghasilkan Floor Visibility Score.
Ini lebih tahan terhadap perubahan pencahayaan dibanding hanya mengandalkan warna lantai.

Saya tidak menyarankan menggunakan kode warna #e7d3a9 saja sebagai indikator, karena perubahan pencahayaan, bayangan, tekstur, atau material lantai akan membuat pendekatan berbasis warna menjadi rapuh. Jika ini hanya untuk digital twin Unity dengan kondisi visual yang selalu konsisten, pendekatan tersebut memang bisa dipakai untuk demo, tetapi untuk sistem vision yang lebih robust lebih baik menggunakan segmentasi atau kombinasi deteksi objek + estimasi area.

Tentang pintu otomatis

Alur yang lebih aman adalah:

Unity
↓

Upload Image

↓

AI Vision

↓

Density

↓

Redistribution

↓

Rule Engine

↓

Safety Chain

↓

Door Recommendation

↓

Unity membuka animasi pintu

Jadi backend tidak langsung "membuka pintu", melainkan mengirim door recommendation/door simulation state ke Unity. Unity yang memutuskan menjalankan animasi pintu sesuai status tersebut. Ini juga sejalan dengan filosofi V6 bahwa AI memberikan rekomendasi, sedangkan aksi akhir tetap melalui lapisan validasi dan simulasi.
