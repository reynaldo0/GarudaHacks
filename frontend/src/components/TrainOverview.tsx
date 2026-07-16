"use client";

import clsx from "clsx";
import { ArrowRight, Camera, TrendingUp, TrendingDown, Minus, Users, VenusIcon as Female } from "lucide-react";
import { Recommendation } from "@/types";
import { TransferAnimation } from "@/components/TransferAnimation";

interface Prediction {
  trend: string;
  predictedOccupancy: number;
  confidence: number;
}

interface CarData {
  carId: number;
  occupancyPct: number;
  status: string;
  passengers: number;
  capacity: number;
  prediction?: Prediction | null;
  cameraStatus?: string;
  recommendation?: { action: string; confidence: number } | null;
}

interface TrainOverviewProps {
  cars: CarData[];
  recommendation?: Recommendation | null;
}

const WOMEN_CARS = [1, 10];

const statusConfig: Record<string, { bg: string; text: string; ring: string; label: string }> = {
  LOW: { bg: "from-green-500 to-emerald-600", text: "text-green-600", ring: "ring-green-200", label: "Low" },
  NORMAL: { bg: "from-emerald-400 to-green-500", text: "text-emerald-600", ring: "ring-emerald-200", label: "Normal" },
  HIGH: { bg: "from-amber-400 to-yellow-500", text: "text-amber-600", ring: "ring-amber-200", label: "High" },
  FULL: { bg: "from-orange-400 to-orange-600", text: "text-orange-600", ring: "ring-orange-200", label: "Full" },
  OVERCAPACITY: { bg: "from-red-500 to-rose-600", text: "text-red-600", ring: "ring-red-200", label: "Over" },
};

export function TrainOverview({ cars, recommendation }: TrainOverviewProps) {
  const recommendedToCar = recommendation?.toCarId;
  const recommendedFromCar = recommendation?.fromCarId;
  const showWomenAnim = recommendation?.priority === 2 || recommendation?.womenAlternative?.isWomenPriority;

  return (
    <div className="glass rounded-2xl p-6 animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
          Train Overview &mdash; SF10
        </h3>
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted-foreground bg-muted px-3 py-1 rounded-full">
            {cars.length} cars
          </span>
          <span className="text-[10px] text-pink-600 bg-pink-50 px-2 py-0.5 rounded-full flex items-center gap-1">
            <Female className="w-3 h-3" /> Car 1 & Car 10 (Women)
          </span>
        </div>
      </div>

      <div className="relative">
        <TransferAnimation recommendation={recommendation ?? null} carCount={cars.length} showWomenAlternative={showWomenAnim} />

        <div className="flex gap-3 pb-4 justify-center">
          {cars.map((car) => {
          const config = statusConfig[car.status] || statusConfig.NORMAL;
          const isTarget = recommendedToCar === car.carId;
          const isSource = recommendedFromCar === car.carId;
          const fillHeight = Math.min(car.occupancyPct, 100);
          const isWomenCar = WOMEN_CARS.includes(car.carId);

          return (
            <div
              key={car.carId}
              className={clsx(
                "flex-1 min-w-0 max-w-[120px] flex flex-col items-center group",
                isWomenCar && "order-first"
              )}
              style={isWomenCar ? {} : car.carId === 10 ? {} : undefined}
            >
              <div className="h-6 mb-1 flex items-center">
                {isTarget && (
                  <div className="flex items-center gap-1 text-[11px] text-green-600 animate-bounce">
                    <ArrowRight className="w-3 h-3" />
                    <span className="font-medium">Move here</span>
                  </div>
                )}
                {isSource && (
                  <div className="text-[11px] text-red-600 font-medium">
                    From here
                  </div>
                )}
              </div>

              <div
                className={clsx(
                  "relative w-full aspect-[3/4] rounded-xl flex flex-col items-center justify-center border transition-all duration-300",
                  "hover:scale-105 hover:shadow-lg",
                  isTarget && "ring-2 ring-green-400/50 shadow-lg shadow-green-200",
                  isSource && "ring-2 ring-red-400/50 shadow-lg shadow-red-200",
                  isWomenCar && !isTarget && !isSource && "border-pink-200 ring-1 ring-pink-100",
                  !isTarget && !isSource && !isWomenCar && "border-border bg-surface"
                )}
              >
                <div
                  className="absolute bottom-0 left-0 right-0 rounded-b-xl opacity-20 transition-all duration-500"
                  style={{
                    height: `${fillHeight}%`,
                    background: `linear-gradient(to top, ${isWomenCar ? "#EC4899" : config.bg.includes("green") ? "#22C55E" : config.bg.includes("amber") ? "#F59E0B" : config.bg.includes("orange") ? "#F97316" : config.bg.includes("red") ? "#EF4444" : "#6366F1"}, transparent)`,
                  }}
                />
                <div className="absolute inset-0 rounded-xl border border-border" />

                {isWomenCar && (
                  <div className="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-pink-100 flex items-center justify-center ring-2 ring-white">
                    <Female className="w-3 h-3 text-pink-600" />
                  </div>
                )}

                <span className="relative text-2xl font-bold text-foreground">{car.carId}</span>
                <span className={clsx("relative text-sm font-medium", isWomenCar ? "text-pink-600" : "text-muted-foreground")}>{car.occupancyPct.toFixed(0)}%</span>
                <div className="relative flex items-center gap-1 mt-1">
                  <Users className="w-3 h-3 text-muted-foreground" />
                  <span className="text-[11px] text-muted-foreground">{car.passengers}</span>
                </div>
              </div>

              <div className="h-5 mt-2 flex items-center">
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
                      {car.prediction.predictedOccupancy.toFixed(0)}%
                    </span>
                  </div>
                ) : (
                  <span className="text-[11px] text-muted-foreground">&mdash;</span>
                )}
              </div>

              <div className="flex items-center gap-1 mt-0.5">
                <Camera
                  className={clsx(
                    "w-3 h-3",
                    car.cameraStatus === "active" ? "text-green-600" : "text-muted-foreground"
                  )}
                />
                <span className="text-[10px] text-muted-foreground">
                  {car.cameraStatus === "active" ? "Online" : "Offline"}
                </span>
              </div>
            </div>
          );
        })}
        </div>
      </div>

      <div className="flex flex-wrap gap-4 mt-6 pt-4 border-t border-border">
        {Object.entries(statusConfig).map(([status, cfg]) => (
          <div key={status} className="flex items-center gap-2">
            <div className={clsx("w-3 h-3 rounded bg-gradient-to-br", cfg.bg)} />
            <span className="text-xs text-muted-foreground">{cfg.label}</span>
          </div>
        ))}
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-gradient-to-br from-pink-400 to-pink-600" />
          <span className="text-xs text-muted-foreground">Women Car</span>
        </div>
      </div>
    </div>
  );
}
