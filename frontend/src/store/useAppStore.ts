import { create } from "zustand";
import { SystemState, Warning, Recommendation, CarOccupancy, TimelineEvent } from "@/types";

interface AppState {
  isConnected: boolean;
  systemState: SystemState | null;
  warnings: Warning[];
  recommendation: Recommendation | null;
  cars: CarOccupancy[];
  timeline: TimelineEvent[];
  setConnected: (connected: boolean) => void;
  setSystemState: (state: SystemState) => void;
  setWarnings: (warnings: Warning[]) => void;
  setRecommendation: (rec: Recommendation | null) => void;
  setCars: (cars: CarOccupancy[]) => void;
  addTimelineEvent: (event: TimelineEvent) => void;
  setSystemHealth: (items: import("@/types").SystemHealthItem[]) => void;
  systemHealth: import("@/types").SystemHealthItem[];
}

export const useAppStore = create<AppState>((set) => ({
  isConnected: false,
  systemState: null,
  warnings: [],
  recommendation: null,
  cars: [],
  timeline: [],
  systemHealth: [],

  setConnected: (connected) => set({ isConnected: connected }),
  setSystemState: (state) => set({ systemState: state }),
  setWarnings: (warnings) => set({ warnings }),
  setRecommendation: (rec) => set({ recommendation: rec }),
  setCars: (cars) => set({ cars }),
  setSystemHealth: (items) => set({ systemHealth: items }),

  addTimelineEvent: (event) =>
    set((state) => ({
      timeline: [event, ...state.timeline].slice(0, 50),
    })),
}));
