"use client";

import {
  Activity,
  AlertTriangle,
  CheckCircle,
  DoorOpen,
  Megaphone,
  Wrench,
  TrendingUp,
  Shield,
} from "lucide-react";
import clsx from "clsx";
import { PipelineResult } from "@/types";

const densityColor = {
  GREEN: "bg-green-500",
  YELLOW: "bg-amber-500",
  RED: "bg-red-500",
} as const;

const densityBg = {
  GREEN: "bg-green-50 border-green-200",
  YELLOW: "bg-amber-50 border-amber-200",
  RED: "bg-red-50 border-red-200",
} as const;

interface Props {
  result: PipelineResult;
}

export function PipelineResultPanel({ result }: Props) {
  const occPct = (result.occupancyRatio * 100).toFixed(1);
  const freePct = (result.freeSpaceRatio * 100).toFixed(1);
  const spatialPct = (result.spatialOccupancyScore * 100).toFixed(1);

  return (
    <div className="space-y-5 animate-fade-in">
      <div className={clsx("flex items-center gap-3 p-4 rounded-2xl border", densityBg[result.densityIndicator])}>
        <div className={clsx("w-4 h-4 rounded-full", densityColor[result.densityIndicator])} />
        <div>
          <p className="text-sm font-semibold text-foreground">
            {result.carId} &mdash; Density: {result.densityIndicator}
          </p>
          <p className="text-xs text-muted-foreground">
            Analyzed at {new Date(result.timestamp).toLocaleString()}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <MetricCard
          icon={<Activity className="w-4 h-4" />}
          label="Occupancy"
          value={`${occPct}%`}
          accent={result.densityIndicator === "RED" ? "text-red-600" : result.densityIndicator === "YELLOW" ? "text-amber-600" : "text-green-600"}
        />
        <MetricCard
          icon={<TrendingUp className="w-4 h-4" />}
          label="Free Space"
          value={`${freePct}%`}
          accent="text-primary"
        />
        <MetricCard
          icon={<Activity className="w-4 h-4" />}
          label="Spatial Score"
          value={`${spatialPct}%`}
          accent="text-primary"
        />
        <MetricCard
          icon={<Shield className="w-4 h-4" />}
          label="CALES Score"
          value={`${result.calesScore.toFixed(1)}`}
          accent="text-secondary"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <InfoCard
          icon={<DoorOpen className="w-4 h-4 text-primary" />}
          title="Door Action"
          value={result.doorAction.replace("_", " ")}
        />
        <InfoCard
          icon={<Wrench className="w-4 h-4 text-secondary" />}
          title="Health Index"
          value={`${result.healthIndex.toFixed(0)} / 100`}
        />
        <InfoCard
          icon={<CheckCircle className="w-4 h-4 text-green-600" />}
          title="Recommended Action"
          value={result.recommendedAction.replace(/_/g, " ")}
        />
      </div>

      {result.recommendedTarget && (
        <div className="flex items-center gap-2 p-3 rounded-xl bg-primary/5 border border-primary/10 text-sm">
          <AlertTriangle className="w-4 h-4 text-primary" />
          <span className="text-foreground">
            Recommended redistribution to <strong>{result.recommendedTarget}</strong>
          </span>
        </div>
      )}

      {result.announcement && (
        <div className="flex items-start gap-2 p-3 rounded-xl bg-secondary/5 border border-secondary/10 text-sm">
          <Megaphone className="w-4 h-4 text-secondary mt-0.5 flex-shrink-0" />
          <p className="text-muted-foreground">{result.announcement}</p>
        </div>
      )}

      <div className="glass rounded-xl p-4">
        <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Damage Assessment</h4>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <span className="text-muted-foreground">Damage Multiplier:</span>
            <span className="ml-2 font-medium text-foreground">{result.damageMultiplier.toFixed(2)}x</span>
          </div>
          <div>
            <span className="text-muted-foreground">Inspection Priority:</span>
            <span className="ml-2 font-medium text-foreground">Level {result.inspectionPriority}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ icon, label, value, accent }: { icon: React.ReactNode; label: string; value: string; accent: string }) {
  return (
    <div className="glass rounded-xl p-3">
      <div className="flex items-center gap-1.5 text-muted-foreground mb-1">
        {icon}
        <span className="text-xs">{label}</span>
      </div>
      <p className={clsx("text-lg font-bold", accent)}>{value}</p>
    </div>
  );
}

function InfoCard({ icon, title, value }: { icon: React.ReactNode; title: string; value: string }) {
  return (
    <div className="glass rounded-xl p-3">
      <div className="flex items-center gap-1.5 mb-1">
        {icon}
        <span className="text-xs text-muted-foreground">{title}</span>
      </div>
      <p className="text-sm font-semibold text-foreground capitalize">{value}</p>
    </div>
  );
}
