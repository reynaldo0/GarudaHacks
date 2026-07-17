"use client";

import { TrainOverview } from "@/components/TrainOverview";
import { OccupancyChart } from "@/components/OccupancyChart";
import { useAppStore } from "@/store/useAppStore";
import { useWebSocket } from "@/hooks/useWebSocket";
import { WifiOff } from "lucide-react";
import clsx from "clsx";

export default function TrainPage() {
  const { cars, isConnected } = useAppStore();

  useWebSocket();

  if (!isConnected && cars.length === 0) {
    return (
      <div className="space-y-6">
        <div className="animate-fade-in">
          <h1 className="text-2xl font-bold text-foreground tracking-tight">Train Status</h1>
          <p className="text-muted-foreground text-sm mt-1">SF6 Formation &mdash; Real-time spatial occupancy</p>
        </div>
        <div className="flex items-center justify-center min-h-[40vh]">
          <div className="glass rounded-2xl p-10 max-w-md text-center animate-fade-in">
            <div className="w-16 h-16 rounded-2xl bg-red-50 flex items-center justify-center mx-auto mb-4">
              <WifiOff className="w-8 h-8 text-accent" />
            </div>
            <h2 className="text-xl font-bold text-foreground mb-2">Backend Offline</h2>
            <p className="text-muted-foreground text-sm">
              Unable to connect. Ensure the backend is running.
            </p>
          </div>
        </div>
      </div>
    );
  }

  const densityColorMap: Record<string, { bg: string; text: string }> = {
    GREEN: { bg: "bg-green-50", text: "text-green-600" },
    YELLOW: { bg: "bg-amber-50", text: "text-amber-600" },
    RED: { bg: "bg-red-50", text: "text-red-600" },
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between animate-fade-in">
        <div>
          <h1 className="text-2xl font-bold text-foreground tracking-tight">Train Status</h1>
          <p className="text-muted-foreground text-sm mt-1">SF6 Formation &mdash; Real-time spatial occupancy</p>
        </div>
        <div className="flex items-center gap-2 glass px-3 py-1.5 rounded-full">
          <div className={`w-2 h-2 rounded-full ${isConnected ? "bg-green-500 animate-pulse" : "bg-accent"}`} />
          <span className="text-xs text-muted-foreground">{isConnected ? "Live" : "Offline"}</span>
        </div>
      </div>

      <TrainOverview cars={cars} />
      <OccupancyChart
        data={cars.map((c) => ({
          carId: c.carId,
          occupancyRatio: c.occupancyRatio,
          densityIndicator: c.densityIndicator,
        }))}
      />

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {cars.map((car, i) => {
          const cfg = densityColorMap[car.densityIndicator] || densityColorMap.GREEN;
          return (
            <div
              key={car.carId}
              className="glass glass-hover rounded-2xl p-5 text-center transition-all duration-300 hover:scale-[1.03] animate-fade-in"
              style={{ animationDelay: `${i * 30}ms` }}
            >
              <p className="text-xs text-muted-foreground uppercase tracking-wider">Gerbong {car.carId}</p>
              <p className="text-3xl font-bold mt-2 text-foreground tracking-tight">
                {(car.occupancyRatio * 100).toFixed(0)}%
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                Kosong: {(car.freeSpaceRatio * 100).toFixed(0)}%
              </p>
              <div className={clsx(
                "mt-3 px-3 py-1 rounded-lg inline-block text-xs font-medium",
                cfg.bg,
                cfg.text
              )}>
                {car.densityIndicator}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
