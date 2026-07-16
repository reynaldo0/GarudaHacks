"use client";

import { useEffect, useRef, useCallback } from "react";
import { useAppStore } from "@/store/useAppStore";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws";

interface WebSocketMessage {
  type: string;
  train_id?: string;
  timestamp?: string;
  data?: any;
}

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const { setConnected } = useAppStore();

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    try {
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
        reconnectTimeoutRef.current = setTimeout(connect, 3000);
      };

      ws.onerror = (error) => {
        console.error("[WS] Error:", error);
        ws.close();
      };
    } catch (error) {
      console.error("[WS] Connection failed:", error);
      reconnectTimeoutRef.current = setTimeout(connect, 3000);
    }
  }, [setConnected]);

  const handleMessage = useCallback((message: WebSocketMessage) => {
    const store = useAppStore.getState();
    const ts = message.timestamp || new Date().toISOString();

    switch (message.type) {
      case "occupancy_updated": {
        if (message.data) {
          const currentCars = [...store.cars];
          const carIndex = currentCars.findIndex(
            (c) => c.carId === message.data.car_id
          );
          if (carIndex >= 0) {
            currentCars[carIndex] = {
              ...currentCars[carIndex],
              occupancyPct:
                message.data.occupancy_percentage ??
                currentCars[carIndex].occupancyPct,
              passengers:
                message.data.person_count ??
                currentCars[carIndex].passengers,
              status:
                message.data.status ?? currentCars[carIndex].status,
            };
            store.setCars(currentCars);
          }
          store.addTimelineEvent({
            id: `occ-${Date.now()}`,
            timestamp: ts,
            type: "occupancy",
            message: `Car ${message.data.car_id}: ${message.data.occupancy_percentage ?? "?"}% occupancy`,
            severity: "info",
          });
        }
        break;
      }

      case "prediction_updated": {
        if (message.data) {
          const prediction = message.data.prediction || {};
          const currentCars = [...store.cars];
          const idx = currentCars.findIndex(
            (c) => c.carId === message.data.car_id
          );
          if (idx >= 0) {
            currentCars[idx] = {
              ...currentCars[idx],
              prediction: {
                trend: prediction.trend ?? "stable",
                predictedOccupancy:
                  prediction.predictedOccupancy ?? currentCars[idx].occupancyPct,
                confidence: prediction.confidence ?? 0,
              },
            };
            store.setCars(currentCars);
          }
        }
        break;
      }

      case "recommendation_changed": {
        if (message.data) {
          const rec = message.data.recommendation || message.data;
          store.setRecommendation(rec);
          store.addTimelineEvent({
            id: `rec-${Date.now()}`,
            timestamp: ts,
            type: "recommendation",
            message: `AI: Move passengers from Car ${rec.fromCarId} to Car ${rec.toCarId}`,
            severity: "info",
          });
        }
        break;
      }

      case "warning_updated": {
        if (message.data) {
          const warnings = store.warnings || [];
          const w = message.data.warning || message.data;
          const newWarning = {
            id: w.id || `warn-${Date.now()}`,
            trainId: w.trainId || w.train_id || "",
            carId: w.carId ?? w.car_id ?? 0,
            warningType: w.warningType || w.warning_type || "unknown",
            severity: w.severity || "INFO",
            message: w.message || "",
            timestamp: w.timestamp || ts,
            isActive: w.isActive ?? true,
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
            (c) => c.carId === message.data.camera_id
          );
          if (idx >= 0) {
            currentCars[idx] = {
              ...currentCars[idx],
              cameraStatus: message.data.status ?? "unknown",
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
          const health = message.data.health || message.data;
          store.setSystemHealth(health);
        }
        break;
      }

      case "state_updated": {
        if (message.data) {
          store.setSystemState(message.data);
        }
        break;
      }
    }
  }, []);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  useEffect(() => {
    connect();
    return disconnect;
  }, [connect, disconnect]);

  return { connect, disconnect };
}
