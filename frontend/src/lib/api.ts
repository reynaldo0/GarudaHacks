import axios from "axios";
import {
  SystemState,
  OccupancyData,
  Recommendation,
  PipelineResult,
} from "@/types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const FRAME_API_KEY =
  process.env.NEXT_PUBLIC_FRAME_API_KEY || "themis-unity-key-2026";

function toCamelCase(str: string): string {
  return str.replace(/_([a-z])/g, (_, c) => c.toUpperCase());
}

function camelizeKeys(obj: unknown): unknown {
  if (Array.isArray(obj)) return obj.map(camelizeKeys);
  if (obj !== null && typeof obj === "object" && !(obj instanceof Date)) {
    return Object.fromEntries(
      Object.entries(obj as Record<string, unknown>).map(([k, v]) => [
        toCamelCase(k),
        camelizeKeys(v),
      ]),
    );
  }
  return obj;
}

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.response.use((res) => {
  if (res.data && typeof res.data === "object") {
    res.data = camelizeKeys(res.data);
  }
  return res;
});

export const apiClient = {
  async getHealth() {
    const res = await api.get("/api/v1/health");
    return res.data.data;
  },

  async getState(): Promise<SystemState> {
    const res = await api.get("/api/v1/state");
    return res.data.data;
  },

  async getOccupancy(): Promise<OccupancyData> {
    const res = await api.get("/api/v1/occupancy");
    return res.data.data;
  },

  async getWarnings() {
    const res = await api.get("/api/v1/history/warnings");
    return res.data.data;
  },

  async resetSimulation() {
    const res = await api.post("/api/v1/simulation/reset");
    return res.data.data;
  },

  async loadScenario(scenarioName: string) {
    const res = await api.post(`/api/v1/simulation/scenario/${scenarioName}`);
    return res.data.data;
  },

  async getSimulationStatus() {
    const res = await api.get("/api/v1/simulation/status");
    return res.data.data;
  },

  async getRecommendation(): Promise<Recommendation | null> {
    const res = await api.get("/api/v1/recommendation");
    return res.data.data;
  },

  async getHistory(hours: number = 24, carId?: number) {
    const params = new URLSearchParams({ hours: String(hours) });
    if (carId) params.append("car_id", String(carId));
    const res = await api.get(`/api/v1/history?${params}`);
    return res.data.data;
  },

  async uploadFrames(
    files: File[],
    options?: { cameraIds?: string[]; stationId?: string; trainId?: string },
  ): Promise<PipelineResult> {
    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));
    if (options?.cameraIds?.length) {
      formData.append("camera_ids", options.cameraIds.join(","));
    }
    if (options?.stationId) formData.append("station_id", options.stationId);
    if (options?.trainId) formData.append("train_id", options.trainId);

    const res = await axios.post(`${API_BASE}/api/v1/frame`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
        "X-API-Key": FRAME_API_KEY,
      },
      timeout: 30000,
    });
    const data = camelizeKeys(res.data?.data ?? res.data) as PipelineResult;
    return data;
  },
};
