"use client";

import { useState, useRef, useCallback } from "react";
import { Upload, X, Camera, Loader2, ImageIcon, Train } from "lucide-react";
import clsx from "clsx";
import { apiClient } from "@/lib/api";
import { PipelineResult } from "@/types";

interface ImageSlot {
  file: File | null;
  preview: string | null;
}

const POSITION_LABELS = ["Front-Left", "Front-Right", "Rear-Left", "Rear-Right"];
const ACCEPTED_TYPES = ["image/jpeg", "image/png", "image/webp"];

export function ImageUpload({ onResult }: { onResult: (result: PipelineResult) => void }) {
  const [slots, setSlots] = useState<ImageSlot[]>([
    { file: null, preview: null },
    { file: null, preview: null },
    { file: null, preview: null },
    { file: null, preview: null },
  ]);
  const [selectedCar, setSelectedCar] = useState(1);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [trainId, setTrainId] = useState("SF6-001");
  const [stationId, setStationId] = useState("unknown");
  const fileRefs = useRef<(HTMLInputElement | null)[]>([]);

  const getCameraIds = (carNum: number) =>
    Array.from({ length: 4 }, (_, i) => `car${String(carNum).padStart(2, "0")}_cam${String(i + 1).padStart(2, "0")}`);

  const getCameraLabel = (carNum: number, camIndex: number) =>
    `Car ${carNum} — ${POSITION_LABELS[camIndex]}`;

  const handleFileSelect = useCallback((index: number, file: File) => {
    if (!ACCEPTED_TYPES.includes(file.type)) {
      setError("Only JPEG, PNG, and WebP images are accepted.");
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setError("File size must be under 10 MB.");
      return;
    }
    setError(null);
    const preview = URL.createObjectURL(file);
    setSlots((prev) => {
      const next = [...prev];
      if (next[index].preview) URL.revokeObjectURL(next[index].preview!);
      next[index] = { file, preview };
      return next;
    });
  }, []);

  const removeSlot = useCallback((index: number) => {
    setSlots((prev) => {
      const next = [...prev];
      if (next[index].preview) URL.revokeObjectURL(next[index].preview!);
      next[index] = { file: null, preview: null };
      return next;
    });
  }, []);

  const handleDrop = useCallback((index: number, e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file) handleFileSelect(index, file);
  }, [handleFileSelect]);

  const handleUpload = async () => {
    const files = slots.filter((s) => s.file).map((s) => s.file!);
    if (files.length === 0) {
      setError("Please select at least one image.");
      return;
    }
    setError(null);
    setUploading(true);
    try {
      const cameraIds = getCameraIds(selectedCar);
      const filledIndices = slots.map((s, i) => s.file ? i : -1).filter((i) => i >= 0);
      const result = await apiClient.uploadFrames(files, {
        cameraIds: filledIndices.map((i) => cameraIds[i]),
        stationId,
        trainId,
      });
      onResult(result);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Upload failed. Backend may be offline.";
      setError(msg);
    } finally {
      setUploading(false);
    }
  };

  const filledCount = slots.filter((s) => s.file).length;
  const cameraIds = getCameraIds(selectedCar);

  return (
    <div className="space-y-5">
      {/* Car Selector */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <Train className="w-4 h-4 text-primary" />
          <label className="text-sm font-medium text-foreground">Gerbong:</label>
        </div>
        <div className="flex gap-1.5">
          {Array.from({ length: 6 }, (_, i) => i + 1).map((car) => (
            <button
              key={car}
              onClick={() => setSelectedCar(car)}
              className={clsx(
                "w-9 h-9 rounded-lg text-xs font-bold transition-all duration-200",
                selectedCar === car
                  ? "bg-primary text-primary-foreground shadow-md shadow-primary/25 scale-105"
                  : "bg-muted text-muted-foreground hover:bg-muted/80 hover:text-foreground"
              )}
            >
              {car}
            </button>
          ))}
        </div>
        <span className="text-[11px] text-muted-foreground ml-1">
          Camera: {cameraIds[0]} — {cameraIds[3]}
        </span>
      </div>

      {/* Camera Slots */}
      <div className="grid grid-cols-2 gap-4">
        {slots.map((slot, i) => (
          <div
            key={i}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => handleDrop(i, e)}
            className={clsx(
              "relative group rounded-2xl border-2 border-dashed transition-all duration-200 overflow-hidden",
              slot.preview
                ? "border-primary/30 bg-primary/5"
                : "border-border hover:border-primary/40 hover:bg-muted/50",
              "aspect-square flex flex-col items-center justify-center cursor-pointer"
            )}
            onClick={() => !slot.preview && fileRefs.current[i]?.click()}
          >
            <input
              ref={(el) => { fileRefs.current[i] = el; }}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              className="hidden"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) handleFileSelect(i, f);
                e.target.value = "";
              }}
            />

            {slot.preview ? (
              <>
                <img
                  src={slot.preview}
                  alt={getCameraLabel(selectedCar, i)}
                  className="w-full h-full object-cover"
                />
                <button
                  onClick={(e) => { e.stopPropagation(); removeSlot(i); }}
                  className="absolute top-2 right-2 w-7 h-7 rounded-full bg-black/60 text-white flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <X className="w-4 h-4" />
                </button>
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent px-3 py-2">
                  <p className="text-xs text-white font-medium truncate">{slot.file!.name}</p>
                  <p className="text-[10px] text-white/70">{cameraIds[i]}</p>
                </div>
              </>
            ) : (
              <div className="flex flex-col items-center gap-2 p-4">
                <div className="w-12 h-12 rounded-xl bg-muted flex items-center justify-center">
                  <Camera className="w-6 h-6 text-muted-foreground" />
                </div>
                <p className="text-xs text-muted-foreground text-center font-medium">{getCameraLabel(selectedCar, i)}</p>
                <p className="text-[10px] text-primary/70 font-mono">{cameraIds[i]}</p>
                <p className="text-[10px] text-muted-foreground/70">Click or drag image</p>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Train & Station */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="flex-1">
          <label className="text-xs font-medium text-muted-foreground mb-1 block">Train ID</label>
          <input
            type="text"
            value={trainId}
            onChange={(e) => setTrainId(e.target.value)}
            className="w-full px-3 py-2 rounded-xl glass border border-border text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-primary/30"
          />
        </div>
        <div className="flex-1">
          <label className="text-xs font-medium text-muted-foreground mb-1 block">Station ID</label>
          <input
            type="text"
            value={stationId}
            onChange={(e) => setStationId(e.target.value)}
            className="w-full px-3 py-2 rounded-xl glass border border-border text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-primary/30"
          />
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-center gap-2 p-3 rounded-xl bg-red-50 border border-red-200 text-accent text-sm">
          <X className="w-4 h-4 flex-shrink-0" />
          {error}
        </div>
      )}

      {/* Upload Button */}
      <button
        onClick={handleUpload}
        disabled={uploading || filledCount === 0}
        className={clsx(
          "flex items-center justify-center gap-2 w-full px-6 py-3 rounded-xl font-medium text-sm transition-all duration-200",
          uploading || filledCount === 0
            ? "bg-muted text-muted-foreground cursor-not-allowed"
            : "bg-gradient-to-r from-primary to-secondary text-white hover:shadow-lg hover:shadow-primary/25 hover:scale-[1.01]"
        )}
      >
        {uploading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Analyzing Gerbong {selectedCar}...
          </>
        ) : (
          <>
            <Upload className="w-5 h-5" />
            Upload & Analyze Gerbong {selectedCar} {filledCount > 0 ? `(${filledCount} image${filledCount > 1 ? "s" : ""})` : ""}
          </>
        )}
      </button>

      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <ImageIcon className="w-3.5 h-3.5" />
        <span>JPEG, PNG, WebP &middot; Max 10 MB &middot; Upload 4 fisheye camera images for Gerbong {selectedCar}</span>
      </div>
    </div>
  );
}
