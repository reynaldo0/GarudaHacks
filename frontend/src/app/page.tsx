"use client";

import { useEffect, useState } from "react";
import { Users, AlertTriangle, Activity, Zap, WifiOff } from "lucide-react";
import { KPICard } from "@/components/KPICard";
import { TrainOverview } from "@/components/TrainOverview";
import { AlertPanel } from "@/components/AlertPanel";
import { OccupancyChart } from "@/components/OccupancyChart";
import { RecommendationPanel } from "@/components/RecommendationPanel";
import { Timeline } from "@/components/Timeline";
import { SystemHealth } from "@/components/SystemHealth";
import { apiClient } from "@/lib/api";
import { useAppStore } from "@/store/useAppStore";
import { useWebSocket } from "@/hooks/useWebSocket";
import { SystemState, OccupancyCarResponse } from "@/types";

export default function DashboardPage() {
  const {
    systemState,
    setSystemState,
    setConnected,
    setWarnings,
    setRecommendation,
    cars,
    setCars,
    warnings,
    recommendation,
    isConnected,
  } = useAppStore();
  const [loading, setLoading] = useState(true);
  const [backendOffline, setBackendOffline] = useState(false);

  useWebSocket();

  useEffect(() => {
    async function fetchInitialState() {
      try {
        const state: SystemState = await apiClient.getState();
        setSystemState(state);
        setConnected(true);
        setBackendOffline(false);

        if (state?.train) {
          try {
            const occData = await apiClient.getOccupancy();
            if (occData?.cars) {
              setCars(
                occData.cars.map((c: OccupancyCarResponse) => ({
                  carId: c.carId,
                  occupancyPct: c.occupancyPct,
                  status: c.status,
                  passengers: c.passengers,
                  capacity: c.capacity,
                  prediction: c.prediction || null,
                  cameraStatus: c.cameraStatus || "active",
                  recommendation: c.recommendation || null,
                }))
              );
            }
          } catch {
            setCars([]);
          }
        }

        try {
          const warnData = await apiClient.getWarnings();
          if (warnData?.warnings) {
            setWarnings(warnData.warnings);
          }
        } catch { /* ignore */ }

        try {
          const recData = await apiClient.getRecommendation();
          if (recData) {
            setRecommendation(recData);
          }
        } catch { /* ignore */ }
      } catch {
        setConnected(false);
        setBackendOffline(true);
      } finally {
        setLoading(false);
      }
    }
    fetchInitialState();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const totalPassengers =
    systemState?.train?.totalPassengers ||
    cars.reduce((sum, c) => sum + c.passengers, 0);
  const totalCapacity = systemState?.train?.totalCapacity || 2000;
  const occupancyPct =
    systemState?.train?.percentage ||
    (totalPassengers / totalCapacity) * 100;
  const status = systemState?.train?.status || "NORMAL";

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          <p className="text-muted-foreground text-sm">Connecting to backend...</p>
        </div>
      </div>
    );
  }

  if (backendOffline && cars.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="glass rounded-2xl p-10 max-w-md text-center animate-fade-in">
          <div className="w-16 h-16 rounded-2xl bg-red-50 flex items-center justify-center mx-auto mb-4">
            <WifiOff className="w-8 h-8 text-accent" />
          </div>
          <h2 className="text-xl font-bold text-foreground mb-2">Backend Offline</h2>
          <p className="text-muted-foreground text-sm mb-4">
            Unable to connect to the THEMIS backend at localhost:8000.
          </p>
          <p className="text-muted-foreground text-xs">
            Please ensure the backend server is running and try again.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between animate-fade-in">
        <div>
          <h1 className="text-2xl font-bold text-foreground tracking-tight">Operation Center</h1>
          <p className="text-muted-foreground text-sm mt-1">Real-time railway occupancy monitoring</p>
        </div>
        <div className="flex items-center gap-2 glass px-3 py-1.5 rounded-full">
          <div className={`w-2 h-2 rounded-full ${isConnected ? "bg-green-500 animate-pulse" : "bg-accent"}`} />
          <span className="text-xs text-muted-foreground">{isConnected ? "Live" : "Offline"}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Total Passengers"
          value={totalPassengers}
          subtitle={`of ${totalCapacity} capacity`}
          icon={<Users className="w-5 h-5" />}
          variant={occupancyPct > 90 ? "danger" : occupancyPct > 70 ? "warning" : "success"}
          delay={0}
        />
        <KPICard
          title="Occupancy"
          value={`${occupancyPct.toFixed(1)}%`}
          subtitle={status}
          icon={<Activity className="w-5 h-5" />}
          variant={status === "FULL" ? "danger" : status === "HIGH" ? "warning" : "default"}
          delay={50}
        />
        <KPICard
          title="Active Alerts"
          value={systemState?.system?.activeWarnings || warnings.length}
          icon={<AlertTriangle className="w-5 h-5" />}
          variant={warnings.length > 0 ? "warning" : "success"}
          delay={100}
        />
        <KPICard
          title="System Uptime"
          value={`${Math.floor((systemState?.system?.uptimeSeconds || 0) / 3600)}h`}
          icon={<Zap className="w-5 h-5" />}
          variant="default"
          delay={150}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <TrainOverview cars={cars} recommendation={recommendation} />
          <OccupancyChart
            data={cars.map((c) => ({
              carId: c.carId,
              occupancy: c.occupancyPct,
              status: c.status,
            }))}
          />
        </div>

        <div className="space-y-6">
          <AlertPanel warnings={warnings} />
          <RecommendationPanel recommendation={recommendation} />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Timeline />
        <SystemHealth systemState={systemState} />
      </div>
    </div>
  );
}
