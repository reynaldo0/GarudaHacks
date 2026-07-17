"use client";

import { useState } from "react";
import { Camera, RotateCcw, ArrowRight } from "lucide-react";
import { ImageUpload } from "@/components/ImageUpload";
import { PipelineResultPanel } from "@/components/PipelineResultPanel";
import { PipelineResult } from "@/types";

export default function UploadPage() {
  const [result, setResult] = useState<PipelineResult | null>(null);

  return (
    <div className="space-y-6">
      <div className="animate-fade-in">
        <h1 className="text-2xl font-bold text-foreground tracking-tight">Frame Upload</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Upload 4 fisheye camera images for AI spatial occupancy analysis
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass rounded-2xl p-6 animate-fade-in">
          <div className="flex items-center gap-2 mb-5">
            <Camera className="w-5 h-5 text-primary" />
            <h2 className="font-semibold text-foreground">Camera Inputs</h2>
          </div>
          <ImageUpload onResult={setResult} />
        </div>

        <div className="glass rounded-2xl p-6 animate-fade-in" style={{ animationDelay: "100ms" }}>
          <div className="flex items-center justify-between mb-5">
            <div className="flex items-center gap-2">
              <ArrowRight className="w-5 h-5 text-secondary" />
              <h2 className="font-semibold text-foreground">Analysis Results</h2>
            </div>
            {result && (
              <button
                onClick={() => setResult(null)}
                className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                Clear
              </button>
            )}
          </div>

          {result ? (
            <PipelineResultPanel result={result} />
          ) : (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <div className="w-16 h-16 rounded-2xl bg-muted flex items-center justify-center mb-4">
                <Camera className="w-8 h-8 text-muted-foreground/50" />
              </div>
              <p className="text-sm text-muted-foreground font-medium">No analysis yet</p>
              <p className="text-xs text-muted-foreground/70 mt-1">
                Upload camera images on the left to see AI analysis results here
              </p>
            </div>
          )}
        </div>
      </div>

      <div className="glass rounded-2xl p-5 animate-fade-in" style={{ animationDelay: "200ms" }}>
        <h3 className="text-sm font-semibold text-foreground mb-3">Pipeline Flow</h3>
        <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
          {[
            "Upload 4 Frames",
            "Fisheye Undistortion",
            "Spatial Segmentation",
            "Occupancy Grid",
            "4-Grid Fusion",
            "Density Classification",
            "CALES Health",
            "Redistribution",
            "Door Logic",
            "Decision",
          ].map((step, i, arr) => (
            <span key={i} className="flex items-center gap-2">
              <span className="px-2 py-1 rounded-lg bg-muted border border-border font-medium text-foreground">
                {step}
              </span>
              {i < arr.length - 1 && <span className="text-muted-foreground/50">&rarr;</span>}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
