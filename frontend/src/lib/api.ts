import axios from "axios";
import { SystemState } from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function toCamelCase(str: string): string {
  return str.replace(/_([a-z])/g, (_, c) => c.toUpperCase());
}

function camelizeKeys(obj: unknown): unknown {
  if (Array.isArray(obj)) return obj.map(camelizeKeys);
  if (obj !== null && typeof obj === "object" && !(obj instanceof Date)) {
    return Object.fromEntries(
      Object.entries(obj as Record<string, unknown>).map(([k, v]) => [toCamelCase(k), camelizeKeys(v)])
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
    const res = await api.get("/health");
    return res.data;
  },

  async getState(): Promise<SystemState> {
    const res = await api.get("/api/v1/state");
    return res.data.data;
  },

  async getOccupancy() {
    const res = await api.get("/api/v1/occupancy");
    return res.data.data;
  },

  async getWarnings() {
    const res = await api.get("/api/v1/history/warnings");
    return res.data.data;
  },

  async resetSimulation() {
    const res = await api.post("/api/v1/simulation/reset");
    return res.data;
  },

  async loadScenario(scenarioName: string) {
    const res = await api.post(`/api/v1/simulation/scenario/${scenarioName}`);
    return res.data;
  },

  async getSimulationStatus() {
    const res = await api.get("/api/v1/simulation/status");
    return res.data.data;
  },

  async getRecommendation() {
    const res = await api.get("/api/v1/recommendation");
    return res.data.data;
  },

  async getHistory(hours: number = 24, carId?: number) {
    const params = new URLSearchParams({ hours: String(hours) });
    if (carId) params.append("car_id", String(carId));
    const res = await api.get(`/api/v1/history?${params}`);
    return res.data.data;
  },
};
