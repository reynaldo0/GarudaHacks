"use client";

import { Recommendation } from "@/types";
import { CheckCircle, Sparkles, Users } from "lucide-react";
import clsx from "clsx";

interface RecommendationPanelProps {
  recommendation: Recommendation | null;
}

function FemaleIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <circle cx="12" cy="8" r="5" />
      <line x1="12" y1="13" x2="12" y2="21" />
      <line x1="8" y1="18" x2="16" y2="18" />
    </svg>
  );
}

export function RecommendationPanel({ recommendation }: RecommendationPanelProps) {
  return (
    <div className="glass rounded-2xl p-6 animate-fade-in">
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="w-5 h-5 text-primary" />
        <h3 className="text-lg font-semibold text-foreground">AI Recommendation</h3>
      </div>

      {!recommendation || !recommendation.recommendations?.length ? (
        <div className="text-center py-8">
          <div className="w-12 h-12 rounded-full bg-green-50 flex items-center justify-center mx-auto mb-3">
            <CheckCircle className="w-6 h-6 text-green-600" />
          </div>
          <p className="text-foreground font-medium">No action needed</p>
          <p className="text-sm text-muted-foreground mt-1">All cars within normal range</p>
        </div>
      ) : (
        <div className="space-y-4">
          {recommendation.recommendations.map((rec, i) => {
            const isPrimary = i === 0;
            const isWomen = rec.isWomenPriority;

            return (
              <div
                key={rec.toCarId}
                className={clsx(
                  "space-y-3 p-4 rounded-xl border transition-all",
                  isWomen
                    ? "border-pink-200 bg-pink-50/40"
                    : isPrimary
                      ? "border-primary/20 bg-primary/5"
                      : "border-border bg-muted/30"
                )}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <div
                      className={clsx(
                        "px-2 py-0.5 rounded-full text-[10px] font-bold",
                        isWomen
                          ? "bg-pink-100 text-pink-700"
                          : isPrimary
                            ? "bg-primary/10 text-primary"
                            : "bg-muted text-muted-foreground"
                      )}
                    >
                      {rec.label}
                    </div>
                    {isWomen && (
                      <FemaleIcon className="w-3 h-3 text-pink-600" />
                    )}
                  </div>
                  <span className="text-sm font-bold text-foreground">
                    {rec.label}
                  </span>
                </div>

                <div className="flex items-center gap-3">
                  <div className="flex-1 text-center">
                    <p className="text-[11px] text-muted-foreground uppercase tracking-wider mb-1">From</p>
                    <p className="text-2xl font-bold text-accent">Gerbong {rec.fromCarId}</p>
                  </div>
                  <div className="flex flex-col items-center gap-1">
                    <span className="text-xs text-muted-foreground">
                      {(rec.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="flex-1 text-center">
                    <p className="text-[11px] text-muted-foreground uppercase tracking-wider mb-1">To</p>
                    <p className={clsx(
                      "text-2xl font-bold flex items-center justify-center gap-1",
                      isWomen ? "text-pink-600" : "text-green-600"
                    )}>
                      {isWomen && <FemaleIcon className="w-4 h-4" />}
                      Gerbong {rec.toCarId}
                    </p>
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-background/50 border border-border">
                  <p className="text-[11px] text-muted-foreground uppercase tracking-wider mb-1">Alasan</p>
                  <p className="text-sm text-foreground">{rec.reason}</p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
