"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api";
import { TrainOverview } from "@/components/TrainOverview";
import { OccupancyChart } from "@/components/OccupancyChart";
import { CarOccupancy, OccupancyCarResponse } from "@/types";
import { WifiOff, Loader2, Users } from "lucide-react";
import clsx from "clsx";

export default function TrainPage() {
  const [cars, setCars] = useState<CarOccupancy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    async function fetchOccupancy() {
      try {
        const data = await apiClient.getOccupancy();
        if (data?.cars) {
          setCars(
            data.cars.map((c: OccupancyCarResponse) => ({
              carId: c.car_id,
              occupancyPct: c.occupancy_percentage || (c.occupancy ?? 0) * 100,
              status: c.status,
              passengers: c.person_count || c.passengers || 0,
              capacity: c.capacity || 200,
              prediction: c.prediction || null,
              cameraStatus: c.camera_status || "active",
              recommendation: c.recommendation || null,
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
          <p className="text-muted-foreground text-sm mt-1">SF10 Formation &mdash; Real-time occupancy</p>
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

  const statusConfig: Record<string, { bg: string; text: string }> = {
    LOW: { bg: "bg-green-50", text: "text-green-600" },
    NORMAL: { bg: "bg-emerald-50", text: "text-emerald-600" },
    HIGH: { bg: "bg-amber-50", text: "text-amber-600" },
    FULL: { bg: "bg-orange-50", text: "text-orange-600" },
    OVERCAPACITY: { bg: "bg-red-50", text: "text-red-600" },
  };

  return (
    <div className="space-y-6">
      <div className="animate-fade-in">
        <h1 className="text-2xl font-bold text-foreground tracking-tight">Train Status</h1>
        <p className="text-muted-foreground text-sm mt-1">SF10 Formation &mdash; Real-time occupancy</p>
      </div>

      <TrainOverview cars={cars} />
      <OccupancyChart
        data={cars.map((c) => ({
          carId: c.carId,
          occupancy: c.occupancyPct,
          status: c.status,
        }))}
      />

      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {cars.map((car, i) => {
          const cfg = statusConfig[car.status] || statusConfig.NORMAL;
          return (
            <div
              key={car.carId}
              className="glass glass-hover rounded-2xl p-5 text-center transition-all duration-300 hover:scale-[1.03] animate-fade-in"
              style={{ animationDelay: `${i * 30}ms` }}
            >
              <p className="text-xs text-muted-foreground uppercase tracking-wider">Car {car.carId}</p>
              <p className="text-3xl font-bold mt-2 text-foreground tracking-tight">
                {car.occupancyPct.toFixed(0)}%
              </p>
              <div className="flex items-center justify-center gap-1 mt-1">
                <Users className="w-3 h-3 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">
                  {car.passengers} / {car.capacity}
                </p>
              </div>
              <div className={clsx(
                "mt-3 px-3 py-1 rounded-lg inline-block text-xs font-medium",
                cfg.bg,
                cfg.text
              )}>
                {car.status}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
