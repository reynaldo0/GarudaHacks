"use client";

import clsx from "clsx";
import { Camera, TrendingUp, TrendingDown, Minus, Users } from "lucide-react";
import { Recommendation, CarSpatialOccupancy } from "@/types";

interface TrainOverviewProps {
  cars: CarSpatialOccupancy[];
  recommendation?: Recommendation | null;
}

const WOMEN_CARS = [1, 10];

const densityConfig: Record<string, { bg: string; text: string; ring: string; label: string }> = {
  GREEN: { bg: "from-green-500 to-emerald-600", text: "text-green-600", ring: "ring-green-200", label: "Low" },
  YELLOW: { bg: "from-amber-400 to-yellow-500", text: "text-amber-600", ring: "ring-amber-200", label: "Medium" },
  RED: { bg: "from-red-500 to-rose-600", text: "text-red-600", ring: "ring-red-200", label: "High" },
};

export function TrainOverview({ cars, recommendation }: TrainOverviewProps) {
  const fromCarId = recommendation?.fromCarId;
  const recommendedCars = recommendation?.recommendedCars ?? [];

  const isSource = (carId: number) => fromCarId === carId;
  const isTarget = (carId: number) => recommendedCars.includes(carId);

  return (
    <div className="glass rounded-2xl p-4 sm:p-6 animate-fade-in w-full">
      <div className="flex items-center justify-between mb-4 sm:mb-6">
        <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
          Train Overview &mdash; SF10
        </h3>
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted-foreground bg-muted px-3 py-1 rounded-full">
            {cars.length} cars
          </span>
          <span className="hidden sm:flex text-[10px] text-pink-600 bg-pink-50 px-2 py-0.5 rounded-full items-center gap-1">
            Car 1 & 10 (Women)
          </span>
        </div>
      </div>

      <div className="relative">
        <div className="flex gap-1 sm:gap-3 justify-between overflow-x-auto pb-4 scrollbar-thin -mx-2 px-2">
          {cars.map((car) => {
          const config = densityConfig[car.densityIndicator] || densityConfig.GREEN;
          const source = isSource(car.carId);
          const target = isTarget(car.carId);
          const fillHeight = Math.min(car.occupancyRatio * 100, 100);
          const isWomenCar = WOMEN_CARS.includes(car.carId);

          return (
            <div
              key={car.carId}
              className={clsx(
                "flex-1 min-w-0 max-w-[130px] flex flex-col items-center group"
              )}
            >
              <div className="h-6 mb-1 flex items-center">
                {source && (
                  <div className="flex items-center gap-1 text-[11px] text-red-600 font-medium">
                    <div className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
                    Current
                  </div>
                )}
              </div>

              <div
                className={clsx(
                  "relative w-full aspect-[3/4] rounded-xl flex flex-col items-center justify-center border transition-all duration-500",
                  "hover:scale-105 hover:shadow-lg",
                  target && !source && "ring-2 ring-green-400/50 shadow-lg shadow-green-200/30",
                  source && "ring-2 ring-red-400/50 shadow-lg shadow-red-200/30",
                  isWomenCar && !target && !source && "border-pink-200/60 ring-1 ring-pink-100/50",
                  !target && !source && !isWomenCar && "border-border bg-surface"
                )}
              >
                <div
                  className="absolute bottom-0 left-0 right-0 rounded-b-xl opacity-20 transition-all duration-700"
                  style={{
                    height: `${fillHeight}%`,
                    background: `linear-gradient(to top, ${
                      isWomenCar ? "#EC4899" : config.bg.includes("green") ? "#22C55E" : config.bg.includes("amber") ? "#F59E0B" : "#EF4444"
                    }, transparent)`,
                  }}
                />
                <div className="absolute inset-0 rounded-xl border border-border" />

                {isWomenCar && (
                  <div className="absolute -top-1 -right-1 w-4 h-4 sm:w-5 sm:h-5 rounded-full bg-pink-100 flex items-center justify-center ring-2 ring-white">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-2.5 h-2.5 sm:w-3 sm:h-3 text-pink-600">
                      <circle cx="12" cy="8" r="5" /><line x1="12" y1="13" x2="12" y2="21" /><line x1="8" y1="18" x2="16" y2="18" />
                    </svg>
                  </div>
                )}

                {target && !source && (
                  <div className="absolute -top-1 -left-1 w-4 h-4 sm:w-5 sm:h-5 rounded-full bg-green-500 flex items-center justify-center ring-2 ring-white">
                    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  </div>
                )}

                <span className={clsx(
                  "relative text-xl sm:text-2xl font-bold",
                  isWomenCar ? "text-pink-700" : "text-foreground"
                )}>
                  {car.carId}
                </span>
                <span className={clsx(
                  "relative text-xs sm:text-sm font-medium",
                  isWomenCar ? "text-pink-600" : "text-muted-foreground"
                )}>
                  {(car.occupancyRatio * 100).toFixed(0)}%
                </span>
                <div className="relative flex items-center gap-1 mt-1">
                  <div className={clsx(
                    "w-1.5 h-1.5 rounded-full",
                    car.densityIndicator === "GREEN" && "bg-green-500",
                    car.densityIndicator === "YELLOW" && "bg-amber-500",
                    car.densityIndicator === "RED" && "bg-red-500",
                  )} />
                  <span className="text-[10px] sm:text-[11px] text-muted-foreground">{car.densityIndicator}</span>
                </div>
              </div>

              <div className="h-5 mt-1.5 flex items-center">
                {car.prediction ? (
                  <div className="flex items-center gap-1">
                    {car.prediction.trend === "increasing" ? (
                      <TrendingUp className="w-3 h-3 text-red-500" />
                    ) : car.prediction.trend === "decreasing" ? (
                      <TrendingDown className="w-3 h-3 text-green-600" />
                    ) : (
                      <Minus className="w-3 h-3 text-muted-foreground" />
                    )}
                    <span className="text-[11px] text-muted-foreground">
                      {(car.prediction.predictedOccupancyRatio * 100).toFixed(0)}%
                    </span>
                  </div>
                ) : (
                  <span className="text-[11px] text-muted-foreground">&mdash;</span>
                )}
              </div>

              <div className="flex items-center gap-1 mt-0.5">
                <Camera
                  className={clsx(
                    "w-2.5 h-2.5 sm:w-3 sm:h-3",
                    car.cameraStatus === "active" ? "text-green-600" : "text-muted-foreground"
                  )}
                />
                <span className="text-[9px] sm:text-[10px] text-muted-foreground">
                  {car.cameraStatus === "active" ? "Online" : "Offline"}
                </span>
              </div>

              {source && (
                <div className="absolute inset-0 rounded-xl pointer-events-none">
                  <div className="absolute inset-0 rounded-xl bg-red-500/5 animate-pulse" style={{ animationDuration: "2.5s" }} />
                </div>
              )}

              {target && !source && (
                <div className="absolute inset-0 rounded-xl pointer-events-none overflow-hidden">
                  <div className="absolute inset-0 rounded-xl bg-green-500/5 animate-ping" style={{ animationDuration: "3s" }} />
                </div>
              )}
            </div>
          );
        })}
        </div>
      </div>

      <div className="flex flex-wrap gap-3 sm:gap-4 mt-4 sm:mt-6 pt-4 border-t border-border">
        {Object.entries(densityConfig).map(([key, cfg]) => (
          <div key={key} className="flex items-center gap-1.5">
            <div className={clsx("w-2.5 h-2.5 sm:w-3 sm:h-3 rounded bg-gradient-to-br", cfg.bg)} />
            <span className="text-[10px] sm:text-xs text-muted-foreground">{cfg.label}</span>
          </div>
        ))}
        <div className="flex items-center gap-1.5">
          <div className="w-2.5 h-2.5 sm:w-3 sm:h-3 rounded bg-gradient-to-br from-pink-400 to-pink-600" />
          <span className="text-[10px] sm:text-xs text-muted-foreground">Women Car</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-2.5 h-2.5 sm:w-3 sm:h-3 rounded bg-gradient-to-br from-red-400 to-red-500" />
          <span className="text-[10px] sm:text-xs text-muted-foreground">Source</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-2.5 h-2.5 sm:w-3 sm:h-3 rounded bg-gradient-to-br from-green-400 to-green-500" />
          <span className="text-[10px] sm:text-xs text-muted-foreground">Destination</span>
        </div>
      </div>
    </div>
  );
}
