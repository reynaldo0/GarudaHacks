"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api";
import { TrainOverview } from "@/components/TrainOverview";
import { OccupancyChart } from "@/components/OccupancyChart";
import { CarSpatialOccupancy } from "@/types";
import { WifiOff, Loader2 } from "lucide-react";
import clsx from "clsx";

export default function TrainPage() {
  const [cars, setCars] = useState<CarSpatialOccupancy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    async function fetchOccupancy() {
      try {
        const data = await apiClient.getOccupancy();
        if (data?.cars) {
          setCars(
            data.cars.map((c: CarSpatialOccupancy) => ({
              carId: c.carId,
              occupancyRatio: c.occupancyRatio,
              freeSpaceRatio: c.freeSpaceRatio,
              densityIndicator: c.densityIndicator,
              spatialOccupancyScore: c.spatialOccupancyScore,
              cameraStatus: c.cameraStatus || "active",
              cameraId: c.cameraId,
              riskScore: c.riskScore,
              prediction: c.prediction || null,
            }))
          );
          setError(false);
        }
      } catch {
        setError(true);
      } finally {
        setLoading(false);
      }
    }
    fetchOccupancy();
    const interval = setInterval(fetchOccupancy, 3000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
          <p className="text-muted-foreground text-sm">Loading train data...</p>
        </div>
      </div>
    );
  }

  if (error && cars.length === 0) {
    return (
      <div className="space-y-6">
        <div className="animate-fade-in">
          <h1 className="text-2xl font-bold text-foreground tracking-tight">Train Status</h1>
          <p className="text-muted-foreground text-sm mt-1">SF10 Formation &mdash; Real-time spatial occupancy</p>
        </div>
        <div className="flex items-center justify-center min-h-[40vh]">
          <div className="glass rounded-2xl p-10 max-w-md text-center animate-fade-in">
            <div className="w-16 h-16 rounded-2xl bg-red-50 flex items-center justify-center mx-auto mb-4">
              <WifiOff className="w-8 h-8 text-accent" />
            </div>
            <h2 className="text-xl font-bold text-foreground mb-2">Backend Offline</h2>
            <p className="text-muted-foreground text-sm">
              Unable to fetch train data. Ensure the backend is running.
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
      <div className="animate-fade-in">
        <h1 className="text-2xl font-bold text-foreground tracking-tight">Train Status</h1>
        <p className="text-muted-foreground text-sm mt-1">SF10 Formation &mdash; Real-time spatial occupancy</p>
      </div>

      <TrainOverview cars={cars} />
      <OccupancyChart
        data={cars.map((c) => ({
          carId: c.carId,
          occupancyRatio: c.occupancyRatio,
          densityIndicator: c.densityIndicator,
        }))}
      />

      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {cars.map((car, i) => {
          const cfg = densityColorMap[car.densityIndicator] || densityColorMap.GREEN;
          return (
            <div
              key={car.carId}
              className="glass glass-hover rounded-2xl p-5 text-center transition-all duration-300 hover:scale-[1.03] animate-fade-in"
              style={{ animationDelay: `${i * 30}ms` }}
            >
              <p className="text-xs text-muted-foreground uppercase tracking-wider">Car {car.carId}</p>
              <p className="text-3xl font-bold mt-2 text-foreground tracking-tight">
                {(car.occupancyRatio * 100).toFixed(0)}%
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                Free: {(car.freeSpaceRatio * 100).toFixed(0)}%
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
