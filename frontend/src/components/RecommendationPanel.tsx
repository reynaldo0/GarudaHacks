"use client";

import { Recommendation } from "@/types";
import { ArrowRight, CheckCircle, Sparkles } from "lucide-react";

interface RecommendationPanelProps {
  recommendation: Recommendation | null;
}

export function RecommendationPanel({ recommendation }: RecommendationPanelProps) {
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
          <div className="flex items-center gap-3 p-4 rounded-xl bg-primary/5 border border-primary/10">
            <div className="flex-1 text-center">
              <p className="text-[11px] text-muted-foreground uppercase tracking-wider mb-1">From</p>
              <p className="text-2xl font-bold text-accent">Car {recommendation.fromCarId}</p>
            </div>
            <div className="flex flex-col items-center gap-1">
              <div className="flex items-center gap-1">
                <div className="w-6 h-[1px] bg-gradient-to-r from-accent to-primary" />
                <ArrowRight className="w-5 h-5 text-primary" />
              </div>
              <span className="text-[10px] text-muted-foreground">{recommendation.action}</span>
            </div>
            <div className="flex-1 text-center">
              <p className="text-[11px] text-muted-foreground uppercase tracking-wider mb-1">To</p>
              <p className="text-2xl font-bold text-green-600">Car {recommendation.toCarId}</p>
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-muted-foreground">Confidence</span>
              <span className="text-sm font-bold text-primary">
                {(recommendation.confidence * 100).toFixed(0)}%
              </span>
            </div>
            <div className="h-2 rounded-full bg-muted overflow-hidden">
              <div
                className="h-full rounded-full bg-gradient-to-r from-primary to-secondary transition-all duration-700"
                style={{ width: `${recommendation.confidence * 100}%` }}
              />
            </div>
          </div>

          <div className="p-4 rounded-xl bg-muted border border-border">
            <p className="text-[11px] text-muted-foreground uppercase tracking-wider mb-1">Reason</p>
            <p className="text-sm text-foreground">{recommendation.reason}</p>
          </div>
        </div>
      )}
    </div>
  );
}
