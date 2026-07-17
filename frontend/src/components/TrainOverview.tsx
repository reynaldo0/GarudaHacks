"use client";

import clsx from "clsx";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { Recommendation, CarSpatialOccupancy } from "@/types";

interface TrainOverviewProps {
  cars: CarSpatialOccupancy[];
  recommendation?: Recommendation | null;
}

const WOMEN_CARS = [1, 6];

const densityConfig: Record<string, { fill: string; body: string; border: string; text: string; glow: string; label: string }> = {
  GREEN: { fill: "from-green-400/60 to-emerald-500/60", body: "border-green-300/50", border: "border-green-400", text: "text-green-600", glow: "shadow-green-200/40", label: "Low" },
  YELLOW: { fill: "from-amber-400/60 to-yellow-500/60", body: "border-amber-300/50", border: "border-amber-400", text: "text-amber-600", glow: "shadow-amber-200/40", label: "Medium" },
  RED: { fill: "from-red-400/60 to-rose-500/60", body: "border-red-300/50", border: "border-red-400", text: "text-red-600", glow: "shadow-red-200/40", label: "High" },
};

function LocomotiveFront() {
  return (
    <div className="relative flex-shrink-0 w-10 h-full">
      <svg viewBox="0 0 40 120" className="w-full h-full" fill="none">
        <path d="M38 8 C38 4, 34 0, 28 0 L12 0 C6 0, 2 4, 2 8 L2 112 C2 116, 6 120, 12 120 L28 120 C34 120, 38 116, 38 112 Z" fill="hsl(var(--muted))" stroke="hsl(var(--border))" strokeWidth="1.5"/>
        <rect x="8" y="16" width="24" height="14" rx="3" fill="hsl(var(--background))" stroke="hsl(var(--border))" strokeWidth="1"/>
        <rect x="10" y="36" width="20" height="8" rx="2" fill="hsl(var(--background))" stroke="hsl(var(--border))" strokeWidth="0.8"/>
        <circle cx="20" cy="60" r="4" fill="hsl(var(--primary))" opacity="0.3"/>
        <circle cx="20" cy="60" r="2" fill="hsl(var(--primary))" opacity="0.6"/>
        <rect x="8" y="80" width="24" height="20" rx="2" fill="hsl(var(--background))" stroke="hsl(var(--border))" strokeWidth="0.8"/>
        <circle cx="14" cy="108" r="4" fill="hsl(var(--muted-foreground))" opacity="0.3"/>
        <circle cx="26" cy="108" r="4" fill="hsl(var(--muted-foreground))" opacity="0.3"/>
      </svg>
    </div>
  );
}

function LocomotiveRear() {
  return (
    <div className="relative flex-shrink-0 w-6 h-full">
      <svg viewBox="0 0 24 120" className="w-full h-full" fill="none">
        <path d="M22 8 C22 4, 18 0, 12 0 L4 0 C2 0, 0 4, 0 8 L0 112 C0 116, 2 120, 4 120 L12 120 C18 120, 22 116, 22 112 Z" fill="hsl(var(--muted))" stroke="hsl(var(--border))" strokeWidth="1.5"/>
        <circle cx="11" cy="108" r="3" fill="hsl(var(--muted-foreground))" opacity="0.3"/>
      </svg>
    </div>
  );
}

function Carriage({ car, isSource, isTarget, isWomenCar, showDoor }: {
  car: CarSpatialOccupancy;
  isSource: boolean;
  isTarget: boolean;
  isWomenCar: boolean;
  showDoor: boolean;
}) {
  const config = densityConfig[car.densityIndicator] || densityConfig.GREEN;
  const fillHeight = Math.min(car.occupancyRatio * 100, 100);

  return (
    <div className="relative flex-shrink-0 flex flex-col items-center group" style={{ width: "calc((100% - 76px) / 6)" }}>
      {/* Source/Target label */}
      <div className="h-6 mb-1 flex items-center">
        {isSource && (
          <div className="flex items-center gap-1 text-[10px] text-red-600 font-medium">
            <div className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
            Penuh
          </div>
        )}
        {isTarget && !isSource && (
          <div className="flex items-center gap-1 text-[10px] text-green-600 font-medium">
            <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
            Tujuan
          </div>
        )}
      </div>

      {/* Carriage body */}
      <div
        className={clsx(
          "relative w-full rounded-lg border-2 overflow-hidden transition-all duration-500",
          "hover:scale-[1.03] hover:shadow-lg cursor-default",
          isSource && "border-red-400 shadow-lg shadow-red-200/40",
          isTarget && !isSource && "border-green-400 shadow-lg shadow-green-200/40",
          isWomenCar && !isTarget && !isSource && "border-pink-300/60",
          !isTarget && !isSource && !isWomenCar && "border-border",
          config.glow && (isSource || isTarget) && config.glow,
        )}
        style={{ aspectRatio: "2.2/1" }}
      >
        {/* Fill bar (occupancy level from bottom) */}
        <div
          className={clsx(
            "absolute bottom-0 left-0 right-0 transition-all duration-700 bg-gradient-to-t rounded-b-md",
            config.fill,
          )}
          style={{ height: `${fillHeight}%` }}
        />

        {/* Roof line */}
        <div className="absolute top-0 left-0 right-0 h-2 bg-gradient-to-b from-black/5 to-transparent" />

        {/* Windows row */}
        <div className="absolute top-[15%] left-[6%] right-[6%] flex gap-[4%] h-[30%]">
          {[0, 1, 2, 3].map((w) => (
            <div
              key={w}
              className="flex-1 rounded-sm bg-white/20 border border-white/30 backdrop-blur-[1px]"
            />
          ))}
        </div>

        {/* Door (center) */}
        {showDoor && (
          <div className="absolute top-[10%] bottom-[10%] left-1/2 -translate-x-1/2 w-[8%] flex flex-col gap-[2px]">
            <div className="flex-1 rounded-sm bg-white/10 border border-white/20" />
            <div className="flex-1 rounded-sm bg-white/10 border border-white/20" />
          </div>
        )}

        {/* Women car badge */}
        {isWomenCar && (
          <div className="absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full bg-pink-100 flex items-center justify-center ring-2 ring-white z-10">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="w-3 h-3 text-pink-600">
              <circle cx="12" cy="8" r="4" /><line x1="12" y1="12" x2="12" y2="20" /><line x1="9" y1="17" x2="15" y2="17" />
            </svg>
          </div>
        )}

        {/* Source pulse */}
        {isSource && (
          <div className="absolute inset-0 bg-red-500/5 animate-pulse rounded-lg" style={{ animationDuration: "2.5s" }} />
        )}

        {/* Target pulse */}
        {isTarget && !isSource && (
          <div className="absolute inset-0 bg-green-500/5 animate-ping rounded-lg" style={{ animationDuration: "3s" }} />
        )}

        {/* Car number + occupancy overlay */}
        <div className="absolute inset-0 flex flex-col items-center justify-center z-10">
          <span className={clsx(
            "text-sm sm:text-base font-bold drop-shadow-sm",
            isWomenCar ? "text-pink-700" : "text-foreground"
          )}>
            {car.carId}
          </span>
          <span className="text-[10px] sm:text-xs font-semibold text-foreground/80 drop-shadow-sm">
            {(car.occupancyRatio * 100).toFixed(0)}%
          </span>
        </div>

        {/* Wheels */}
        <div className="absolute -bottom-2.5 left-[15%] w-3 h-3 rounded-full bg-muted-foreground/30 border border-muted-foreground/20" />
        <div className="absolute -bottom-2.5 right-[15%] w-3 h-3 rounded-full bg-muted-foreground/30 border border-muted-foreground/20" />
      </div>

      {/* Bottom info row */}
      <div className="h-10 mt-3 flex flex-col items-center gap-0.5">
        <div className="flex items-center gap-1">
          <div className={clsx(
            "w-1.5 h-1.5 rounded-full",
            car.densityIndicator === "GREEN" && "bg-green-500",
            car.densityIndicator === "YELLOW" && "bg-amber-500",
            car.densityIndicator === "RED" && "bg-red-500",
          )} />
          <span className="text-[9px] sm:text-[10px] text-muted-foreground font-medium">{car.densityIndicator}</span>
        </div>
        {car.prediction ? (
          <div className="flex items-center gap-0.5">
            {car.prediction.trend === "increasing" ? (
              <TrendingUp className="w-2.5 h-2.5 text-red-500" />
            ) : car.prediction.trend === "decreasing" ? (
              <TrendingDown className="w-2.5 h-2.5 text-green-600" />
            ) : (
              <Minus className="w-2.5 h-2.5 text-muted-foreground" />
            )}
            <span className="text-[9px] text-muted-foreground">
              {(car.prediction.predictedOccupancyRatio * 100).toFixed(0)}%
            </span>
          </div>
        ) : (
          <span className="text-[9px] text-muted-foreground">&mdash;</span>
        )}
      </div>
    </div>
  );
}

export function TrainOverview({ cars, recommendation }: TrainOverviewProps) {
  const fromCarId = recommendation?.fromCarId;
  const recommendedCars = recommendation?.recommendedCars ?? [];

  const isSource = (carId: number) => fromCarId === carId;
  const isTarget = (carId: number) => recommendedCars.includes(carId);

  return (
    <div className="glass rounded-2xl p-4 sm:p-6 animate-fade-in w-full overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 sm:mb-5">
        <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
          Train Overview &mdash; SF6
        </h3>
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted-foreground bg-muted px-3 py-1 rounded-full">
            {cars.length} gerbong
          </span>
          <span className="hidden sm:flex text-[10px] text-pink-600 bg-pink-50 px-2 py-0.5 rounded-full items-center gap-1">
            Gerbong 1 & 6 (Wanita)
          </span>
        </div>
      </div>

      {/* Track line */}
      <div className="relative px-2">
        {/* Rail track */}
        <div className="absolute bottom-[9px] left-8 right-4 h-[2px] bg-muted-foreground/15 rounded-full" />
        <div className="absolute bottom-[5px] left-8 right-4 h-[1px] bg-muted-foreground/10 rounded-full" />

        {/* Train */}
        <div className="flex items-end gap-0">
          <LocomotiveFront />
          <div className="flex gap-1.5 flex-1 min-w-0">
            {cars.map((car, i) => (
              <Carriage
                key={car.carId}
                car={car}
                isSource={isSource(car.carId)}
                isTarget={isTarget(car.carId)}
                isWomenCar={WOMEN_CARS.includes(car.carId)}
                showDoor={i > 0}
              />
            ))}
          </div>
          <LocomotiveRear />
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-3 sm:gap-4 mt-6 pt-4 border-t border-border">
        {Object.entries(densityConfig).map(([key, cfg]) => (
          <div key={key} className="flex items-center gap-1.5">
            <div className={clsx("w-2.5 h-2.5 sm:w-3 sm:h-3 rounded bg-gradient-to-br", cfg.fill)} />
            <span className="text-[10px] sm:text-xs text-muted-foreground">{cfg.label}</span>
          </div>
        ))}
        <div className="flex items-center gap-1.5">
          <div className="w-2.5 h-2.5 sm:w-3 sm:h-3 rounded bg-gradient-to-br from-pink-400 to-pink-600" />
          <span className="text-[10px] sm:text-xs text-muted-foreground">Wanita</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-2.5 h-2.5 sm:w-3 sm:h-3 rounded bg-gradient-to-br from-red-400 to-red-500" />
          <span className="text-[10px] sm:text-xs text-muted-foreground">Sumber</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-2.5 h-2.5 sm:w-3 sm:h-3 rounded bg-gradient-to-br from-green-400 to-green-500" />
          <span className="text-[10px] sm:text-xs text-muted-foreground">Tujuan</span>
        </div>
      </div>
    </div>
  );
}
