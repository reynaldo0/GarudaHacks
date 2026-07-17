"use client";

import { useEffect, useRef } from "react";
import { useAppStore } from "@/store/useAppStore";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws";

interface WebSocketMessage {
  type: string;
  train_id?: string;
  timestamp?: string;
  data?: Record<string, unknown>;
}

function handleMessage(message: WebSocketMessage) {
  const store = useAppStore.getState();
  const ts = message.timestamp || new Date().toISOString();

  switch (message.type) {
    case "pipeline_state_updated":
    case "spatial_occupancy_updated": {
      if (message.data) {
        const d = message.data;
        const carIdNum = typeof d.car_id === "string"
          ? parseInt(d.car_id.replace(/\D/g, ""), 10)
          : (d.car_id as number);

        if (carIdNum > 0) {
          const currentCars = [...store.cars];
          const idx = currentCars.findIndex((c) => c.carId === carIdNum);

          const updated: import("@/types").CarSpatialOccupancy = {
            carId: carIdNum,
            occupancyRatio: (d.occupancy_ratio as number) ?? 0,
            freeSpaceRatio: (d.free_space_ratio as number) ?? 1,
            densityIndicator: (d.density_indicator as "GREEN" | "YELLOW" | "RED") ?? "GREEN",
            spatialOccupancyScore: (d.spatial_occupancy_score as number) ?? 0,
            cameraStatus: "active",
            riskScore: (d.occupancy_ratio as number) ?? 0,
            prediction: (d.prediction as import("@/types").CarSpatialOccupancy["prediction"]) ?? null,
          };

          if (idx >= 0) {
            currentCars[idx] = updated;
          } else {
            currentCars.push(updated);
          }
          store.setCars(currentCars);
        }

        store.addTimelineEvent({
          id: `pipe-${Date.now()}`,
          timestamp: ts,
          type: "occupancy",
          message: `Car ${d.car_id}: ${(((d.occupancy_ratio as number) ?? 0) * 100).toFixed(0)}% occupancy [${d.density_indicator ?? "GREEN"}]`,
          severity: d.density_indicator === "RED" ? "warning" : "info",
        });
      }
      break;
    }

    case "occupancy_updated": {
      if (message.data) {
        const d = message.data;
        const carIdNum = d.car_id as number;
        if (carIdNum > 0) {
          const currentCars = [...store.cars];
          const idx = currentCars.findIndex((c) => c.carId === carIdNum);
          if (idx >= 0) {
            currentCars[idx] = {
              ...currentCars[idx],
              occupancyRatio: (d.occupancy_ratio as number) ?? currentCars[idx].occupancyRatio,
              freeSpaceRatio: (d.free_space_ratio as number) ?? currentCars[idx].freeSpaceRatio,
              densityIndicator: (d.density_indicator as "GREEN" | "YELLOW" | "RED") ?? currentCars[idx].densityIndicator,
            };
            store.setCars(currentCars);
          }
        }
        store.addTimelineEvent({
          id: `occ-${Date.now()}`,
          timestamp: ts,
          type: "occupancy",
          message: `Car ${d.car_id}: ${((d.occupancy_ratio as number) ?? 0).toFixed(2)} [${d.density_indicator ?? "GREEN"}]`,
          severity: "info",
        });
      }
      break;
    }

    case "recommendation_changed": {
      if (message.data) {
        const recData = (message.data.recommendation as Record<string, unknown>) || message.data;
        store.setRecommendation(recData as unknown as import("@/types").Recommendation);
        const recs = recData.recommendations as Array<Record<string, unknown>> | undefined;
        const top = recs?.[0];
        if (top) {
          store.addTimelineEvent({
            id: `rec-${Date.now()}`,
            timestamp: ts,
            type: "recommendation",
            message: `AI: Move passengers from Car ${top.fromCarId} to Car ${top.toCarId}`,
            severity: "info",
          });
        }
      }
      break;
    }

    case "warning_updated": {
      if (message.data) {
        const warnings = store.warnings || [];
        const w = (message.data.warning as Record<string, unknown>) || message.data;
        const newWarning: import("@/types").Warning = {
          id: (w.id as string) || `warn-${Date.now()}`,
          trainId: (w.trainId as string) || (w.train_id as string) || "",
          carId: (w.carId as number) ?? (w.car_id as number) ?? 0,
          warningType: (w.warningType as string) || (w.warning_type as string) || "unknown",
          severity: (w.severity as string) || "INFO",
          message: (w.message as string) || "",
          timestamp: (w.timestamp as string) || ts,
          isActive: (w.isActive as boolean) ?? true,
        };
        const exists = warnings.some((warn) => warn.id === newWarning.id);
        if (!exists) {
          store.setWarnings([...warnings, newWarning]);
        }
        store.addTimelineEvent({
          id: `warn-${Date.now()}`,
          timestamp: ts,
          type: "warning",
          message: newWarning.message || `Car ${newWarning.carId}: ${newWarning.warningType}`,
          severity: newWarning.severity === "CRITICAL" ? "warning" : "info",
        });
      }
      break;
    }

    case "camera_status_updated": {
      if (message.data) {
        store.addTimelineEvent({
          id: `cam-${Date.now()}`,
          timestamp: ts,
          type: "info",
          message: `Camera ${(message.data.camera_id as string) ?? ""}: ${(message.data.status as string) ?? "unknown"}`,
          severity: "info",
        });
      }
      break;
    }

    case "simulation_reset": {
      store.setCars([]);
      store.setWarnings([]);
      store.setRecommendation(null);
      store.addTimelineEvent({
        id: `reset-${Date.now()}`,
        timestamp: ts,
        type: "system",
        message: "Simulation has been reset",
        severity: "info",
      });
      break;
    }

    case "system_health_updated": {
      if (message.data) {
        const health = (message.data.health as Record<string, unknown>) || message.data;
        store.setSystemHealth([
          { label: "Backend", status: health.backend === "running" ? "ok" : "error", value: String(health.backend ?? "unknown"), icon: "server" },
          { label: "AI Pipeline", status: health.ai === "loaded" ? "ok" : "warning", value: String(health.ai ?? "offline"), icon: "cpu" },
          { label: "Cameras", status: (health.cameras as number) > 0 ? "ok" : "warning", value: `${health.cameras ?? 0} active`, icon: "camera" },
          { label: "Uptime", status: "ok", value: `${Math.floor((health.uptime as number ?? 0) / 60)}m`, icon: "clock" },
          { label: "Warnings", status: (health.activeWarnings as number) > 0 ? "warning" : "ok", value: `${health.activeWarnings ?? 0} active`, icon: "alert" },
        ]);
      }
      break;
    }
  }
}

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const { setConnected } = useAppStore();

  useEffect(() => {
    function connect() {
      if (wsRef.current?.readyState === WebSocket.OPEN) return;

      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log("[WS] Connected to backend");
        setConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          handleMessage(message);
        } catch (e) {
          console.error("[WS] Failed to parse message:", e);
        }
      };

      ws.onclose = () => {
        console.log("[WS] Disconnected");
        setConnected(false);
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 3000);
      };

      ws.onerror = (error) => {
        console.error("[WS] Error:", error);
        ws.close();
      };
    }

    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [setConnected]);
}
