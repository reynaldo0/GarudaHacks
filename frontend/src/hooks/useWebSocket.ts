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
    case "occupancy_updated": {
      if (message.data) {
        const currentCars = [...store.cars];
        const carIndex = currentCars.findIndex(
          (c) => c.carId === message.data!.car_id
        );
        if (carIndex >= 0) {
          currentCars[carIndex] = {
            ...currentCars[carIndex],
            occupancyPct:
              (message.data.occupancy_percentage as number) ??
              currentCars[carIndex].occupancyPct,
            passengers:
              (message.data.person_count as number) ??
              currentCars[carIndex].passengers,
            status:
              (message.data.status as string) ?? currentCars[carIndex].status,
          };
          store.setCars(currentCars);
        }
        store.addTimelineEvent({
          id: `occ-${Date.now()}`,
          timestamp: ts,
          type: "occupancy",
          message: `Car ${message.data.car_id}: ${(message.data.occupancy_percentage as string | number) ?? "?"}% occupancy`,
          severity: "info",
        });
      }
      break;
    }

    case "prediction_updated": {
      if (message.data) {
        const prediction = (message.data.prediction as Record<string, unknown>) || {};
        const currentCars = [...store.cars];
        const idx = currentCars.findIndex(
          (c) => c.carId === message.data!.car_id
        );
        if (idx >= 0) {
          currentCars[idx] = {
            ...currentCars[idx],
            prediction: {
              trend: (prediction.trend as string) ?? "stable",
              predictedOccupancy:
                (prediction.predictedOccupancy as number) ?? currentCars[idx].occupancyPct,
              confidence: (prediction.confidence as number) ?? 0,
            },
          };
          store.setCars(currentCars);
        }
      }
      break;
    }

    case "recommendation_changed": {
      if (message.data) {
        const recData = (message.data.recommendation as Record<string, unknown>) || message.data;
        store.setRecommendation(recData as never);
        const top = (recData.recommendations as Array<Record<string, unknown>>)?.[0];
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
        const newWarning = {
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
        const currentCars = [...store.cars];
        const idx = currentCars.findIndex(
          (c) => c.carId === message.data!.camera_id
        );
        if (idx >= 0) {
          currentCars[idx] = {
            ...currentCars[idx],
            cameraStatus: (message.data.status as string) ?? "unknown",
          };
          store.setCars(currentCars);
        }
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
        store.setSystemHealth(health as never);
      }
      break;
    }

    case "state_updated": {
      if (message.data) {
        store.setSystemState(message.data as never);
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
