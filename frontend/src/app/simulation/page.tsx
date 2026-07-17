"use client";

import { useState } from "react";
import { apiClient } from "@/lib/api";
import { RotateCcw, CheckCircle, Zap, Cloud, Sun, Moon, TrainFront, AlertTriangle } from "lucide-react";
import clsx from "clsx";

const scenarios = [
  { id: "empty", name: "Empty", description: "Empty train - no passengers", icon: Cloud, gradient: "from-slate-100 to-slate-200" },
  { id: "normal", name: "Normal", description: "Normal operation - balanced mid-day traffic", icon: Sun, gradient: "from-green-100 to-emerald-100" },
  { id: "peak_hour", name: "Peak Hour", description: "Rush hour congestion", icon: Zap, gradient: "from-amber-100 to-orange-100" },
  { id: "holiday", name: "Holiday", description: "Holiday light traffic", icon: Moon, gradient: "from-blue-100 to-indigo-100" },
  { id: "imbalanced", name: "Imbalanced", description: "Heavy imbalance - test redistribution", icon: AlertTriangle, gradient: "from-orange-100 to-red-100" },
  { id: "emergency", name: "Emergency", description: "Multiple RED density cars", icon: AlertTriangle, gradient: "from-red-100 to-rose-100" },
];

export default function SimulationPage() {
  const [activeScenario, setActiveScenario] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);

  const handleLoadScenario = async (scenarioId: string) => {
    setLoading(true);
    setMessage("");
    setIsError(false);
    try {
      await apiClient.loadScenario(scenarioId);
      setActiveScenario(scenarioId);
      setMessage(`Scenario "${scenarioId}" loaded successfully`);
    } catch {
      setMessage("Failed to load scenario \u2014 backend may be offline");
      setIsError(true);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    setLoading(true);
    setMessage("");
    setIsError(false);
    try {
      await apiClient.resetSimulation();
      setActiveScenario(null);
      setMessage("Simulation reset to initial state");
    } catch {
      setMessage("Failed to reset \u2014 backend may be offline");
      setIsError(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="animate-fade-in">
        <h1 className="text-2xl font-bold text-foreground tracking-tight">Simulation</h1>
        <p className="text-muted-foreground text-sm mt-1">Load predefined spatial occupancy scenarios</p>
      </div>

      {message && (
        <div
          className={clsx(
            "flex items-center gap-2 p-4 rounded-xl border animate-fade-in",
            isError
              ? "bg-red-50 border-red-200 text-accent"
              : "bg-primary/5 border-primary/10 text-primary"
          )}
        >
          <CheckCircle className="w-5 h-5 flex-shrink-0" />
          <span className="text-sm">{message}</span>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {scenarios.map((scenario, i) => {
          const Icon = scenario.icon;
          const isActive = activeScenario === scenario.id;
          return (
            <button
              key={scenario.id}
              onClick={() => handleLoadScenario(scenario.id)}
              disabled={loading}
              className={clsx(
                "glass rounded-2xl p-6 text-left transition-all duration-300 hover:scale-[1.03] group animate-fade-in",
                isActive
                  ? "border-primary/30 shadow-lg shadow-primary/5"
                  : "hover:border-border"
              )}
              style={{ animationDelay: `${i * 50}ms` }}
            >
              <div className={clsx(
                "w-12 h-12 rounded-xl bg-gradient-to-br flex items-center justify-center mb-4 transition-transform duration-300 group-hover:scale-110",
                scenario.gradient
              )}>
                <Icon className={clsx("w-6 h-6", isActive ? "text-primary" : "text-muted-foreground group-hover:text-foreground")} />
              </div>
              <h3 className="font-semibold text-foreground">{scenario.name}</h3>
              <p className="text-sm text-muted-foreground mt-1">{scenario.description}</p>
              {isActive && (
                <div className="mt-3 flex items-center gap-1.5 text-xs text-primary font-medium">
                  <div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
                  Active
                </div>
              )}
            </button>
          );
        })}
      </div>

      <button
        onClick={handleReset}
        disabled={loading}
        className="flex items-center gap-2 px-6 py-3 rounded-xl glass glass-hover text-muted-foreground hover:text-foreground transition-all duration-200 disabled:opacity-50"
      >
        <RotateCcw className="w-5 h-5" />
        Reset Simulation
      </button>

      <div className="glass rounded-2xl p-6 animate-fade-in">
        <div className="flex items-center gap-2 mb-4">
          <TrainFront className="w-5 h-5 text-primary" />
          <h3 className="font-semibold text-foreground">How it works</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          {[
            "Select a scenario to load predefined spatial occupancy data",
            "Backend populates State Manager with occupancy ratios per car",
            "Unity Digital Twin visualizes density indicators (GREEN/YELLOW/RED)",
            "Dashboard shows real-time occupancy charts and predictions",
            "AI generates redistribution recommendations for imbalanced trains",
          ].map((step, i) => (
            <div key={i} className="flex items-start gap-2 p-3 rounded-xl bg-muted border border-border">
              <span className="text-xs font-bold text-primary mt-0.5">{i + 1}</span>
              <p className="text-xs text-muted-foreground leading-relaxed">{step}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
