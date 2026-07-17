"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, Activity, Zap, WifiOff } from "lucide-react";
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
import { useVoiceRecommendation } from "@/hooks/useVoiceRecommendation";
import { SystemState, CarSpatialOccupancy } from "@/types";

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
  const [backendOffline, setBackendOffline] = useState(false);

  useWebSocket();
  useVoiceRecommendation(recommendation);

  useEffect(() => {
    async function fetchInitialState() {
      try {
        const state: SystemState = await apiClient.getState();
        setSystemState(state);
        setConnected(true);
        setBackendOffline(false);

        const [occData, warnData, recData] = await Promise.allSettled([
          apiClient.getOccupancy(),
          apiClient.getWarnings(),
          apiClient.getRecommendation(),
        ]);

        if (occData.status === "fulfilled" && occData.value?.cars) {
          setCars(
            occData.value.cars.map((c: CarSpatialOccupancy) => ({
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
        }

        if (warnData.status === "fulfilled" && warnData.value?.warnings) {
          setWarnings(warnData.value.warnings);
        }

        if (recData.status === "fulfilled" && recData.value) {
          setRecommendation(recData.value);
        }
      } catch {
        setConnected(false);
        setBackendOffline(true);
      }
    }
    fetchInitialState();
  }, []);

  const avgOccupancy = systemState?.occupancy?.avgOccupancyRatio ?? (
    cars.length > 0
      ? cars.reduce((sum, c) => sum + c.occupancyRatio, 0) / cars.length
      : 0
  );
  const avgPct = avgOccupancy * 100;
  const greenCars = systemState?.occupancy?.greenCars ?? cars.filter((c) => c.densityIndicator === "GREEN").length;
  const yellowCars = systemState?.occupancy?.yellowCars ?? cars.filter((c) => c.densityIndicator === "YELLOW").length;
  const redCars = systemState?.occupancy?.redCars ?? cars.filter((c) => c.densityIndicator === "RED").length;

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
          <p className="text-muted-foreground text-sm mt-1">Real-time spatial occupancy monitoring</p>
        </div>
        <div className="flex items-center gap-2 glass px-3 py-1.5 rounded-full">
          <div className={`w-2 h-2 rounded-full ${isConnected ? "bg-green-500 animate-pulse" : "bg-accent"}`} />
          <span className="text-xs text-muted-foreground">{isConnected ? "Live" : "Offline"}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Avg Occupancy"
          value={`${avgPct.toFixed(1)}%`}
          subtitle={`${greenCars}G ${yellowCars}Y ${redCars}R`}
          icon={<Activity className="w-5 h-5" />}
          variant={redCars > 0 ? "danger" : yellowCars > 0 ? "warning" : "success"}
          delay={0}
        />
        <KPICard
          title="RED Cars"
          value={redCars}
          subtitle={`of ${cars.length} total`}
          icon={<AlertTriangle className="w-5 h-5" />}
          variant={redCars > 0 ? "danger" : "success"}
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
              occupancyRatio: c.occupancyRatio,
              densityIndicator: c.densityIndicator,
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
