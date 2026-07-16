"use client";

import { Recommendation } from "@/types";
import { ArrowRight, CheckCircle, Sparkles, VenusIcon as Female, Users } from "lucide-react";

interface RecommendationPanelProps {
  recommendation: Recommendation | null;
}

function RecommendCard({ rec, label, isWomen }: { rec: Recommendation; label?: string; isWomen?: boolean }) {
  return (
    <div className={clsx(
      "space-y-3 p-4 rounded-xl border",
      isWomen
        ? "border-pink-200 bg-pink-50/40"
        : "border-primary/10 bg-primary/5"
    )}>
      {label && (
        <div className="flex items-center gap-1.5">
          <div className={clsx("px-2 py-0.5 rounded-full text-[10px] font-bold", isWomen ? "bg-pink-100 text-pink-700" : "bg-primary/10 text-primary")}>
            {label}
          </div>
        </div>
      )}

      <div className="flex items-center gap-3">
        <div className="flex-1 text-center">
          <p className="text-[11px] text-muted-foreground uppercase tracking-wider mb-1">From</p>
          <p className="text-2xl font-bold text-accent">Gerbong {rec.fromCarId}</p>
        </div>
        <div className="flex flex-col items-center gap-1">
          <div className="flex items-center gap-1">
            <div className="w-6 h-[1px] bg-gradient-to-r from-accent to-primary" />
            <ArrowRight className="w-5 h-5 text-primary" />
          </div>
          <span className="text-[10px] text-muted-foreground">{rec.action}</span>
          {rec.passengersToMove && (
            <span className="text-[10px] text-muted-foreground flex items-center gap-0.5">
              <Users className="w-3 h-3" /> ~{rec.passengersToMove}
            </span>
          )}
        </div>
        <div className="flex-1 text-center">
          <p className="text-[11px] text-muted-foreground uppercase tracking-wider mb-1">To</p>
          <p className={clsx("text-2xl font-bold flex items-center justify-center gap-1", isWomen ? "text-pink-600" : "text-green-600")}>
            {isWomen && <Female className="w-4 h-4" />}
            Gerbong {rec.toCarId}
          </p>
        </div>
      </div>

      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-muted-foreground">Confidence</span>
          <span className="text-sm font-bold text-primary">
            {(rec.confidence * 100).toFixed(0)}%
          </span>
        </div>
        <div className="h-2 rounded-full bg-muted overflow-hidden">
          <div
            className="h-full rounded-full bg-gradient-to-r from-primary to-secondary transition-all duration-700"
            style={{ width: `${rec.confidence * 100}%` }}
          />
        </div>
      </div>

      <div className="p-3 rounded-lg bg-background/50 border border-border">
        <p className="text-[11px] text-muted-foreground uppercase tracking-wider mb-1">Alasan</p>
        <p className="text-sm text-foreground">{rec.reason}</p>
      </div>
    </div>
  );
}

import clsx from "clsx";

export function RecommendationPanel({ recommendation }: RecommendationPanelProps) {
  const hasWomenAlt = recommendation?.womenAlternative;
  const primaryRec = recommendation?.womenAlternative ? { ...recommendation, womenAlternative: undefined } : recommendation;

  return (
    <div className="glass rounded-2xl p-6 animate-fade-in">
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="w-5 h-5 text-primary" />
        <h3 className="text-lg font-semibold text-foreground">AI Recommendation</h3>
      </div>

      {!recommendation ? (
        <div className="text-center py-8">
          <div className="w-12 h-12 rounded-full bg-green-50 flex items-center justify-center mx-auto mb-3">
            <CheckCircle className="w-6 h-6 text-green-600" />
          </div>
          <p className="text-foreground font-medium">No action needed</p>
          <p className="text-sm text-muted-foreground mt-1">All cars within normal range</p>
        </div>
      ) : (
        <div className="space-y-4">
          {primaryRec && (
            <RecommendCard rec={primaryRec as Recommendation} label="Priority 1" />
          )}

          {hasWomenAlt && (
            <div className="relative">
              <div className="absolute inset-x-0 -top-2 flex justify-center">
                <span className="text-[10px] text-pink-500 font-semibold bg-background px-2">
                  Alternatif Khusus Wanita
                </span>
              </div>
              <RecommendCard rec={recommendation.womenAlternative!} label="Priority 2" isWomen />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
