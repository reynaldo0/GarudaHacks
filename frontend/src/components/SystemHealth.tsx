"use client";

import { Server, Camera, Cpu, Database, Wifi, Monitor, Clock, Brain } from "lucide-react";
import { SystemState } from "@/types";
import clsx from "clsx";

interface SystemHealthProps {
  systemState: SystemState | null;
}

interface HealthItem {
  label: string;
  status: "ok" | "warning" | "error";
  value: string;
  icon: React.ReactNode;
}

export function SystemHealth({ systemState }: SystemHealthProps) {
  const items: HealthItem[] = [
    {
      label: "Backend",
      status: systemState ? "ok" : "error",
      value: systemState ? "Connected" : "Disconnected",
      icon: <Server className="w-4 h-4" />,
    },
    {
      label: "YOLO Engine",
      status: systemState ? "ok" : "warning",
      value: systemState ? "YOLO11s Loaded" : "Offline",
      icon: <Brain className="w-4 h-4" />,
    },
    {
      label: "Database",
      status: "ok",
      value: "PostgreSQL",
      icon: <Database className="w-4 h-4" />,
    },
    {
      label: "WebSocket",
      status: systemState ? "ok" : "warning",
      value: systemState ? "Active" : "Fallback",
      icon: <Wifi className="w-4 h-4" />,
    },
    {
      label: "Unity Client",
      status: "warning",
      value: "Hackathon Mode",
      icon: <Monitor className="w-4 h-4" />,
    },
    {
      label: "Cameras",
      status: (systemState?.system?.activeCameras || 0) > 0 ? "ok" : "warning",
      value: `${systemState?.system?.activeCameras || 0} active`,
      icon: <Camera className="w-4 h-4" />,
    },
    {
      label: "AI Pipeline",
      status: systemState ? "ok" : "error",
      value: systemState ? "8 Engines Active" : "Offline",
      icon: <Cpu className="w-4 h-4" />,
    },
    {
      label: "Latency",
      status: "ok",
      value: "<100ms",
      icon: <Clock className="w-4 h-4" />,
    },
  ];

  const okCount = items.filter((i) => i.status === "ok").length;

  return (
    <div className="glass rounded-2xl p-6 animate-fade-in">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Server className="w-5 h-5 text-primary" />
          <h3 className="text-lg font-semibold text-foreground">System Health</h3>
        </div>
        <span className="text-xs text-muted-foreground bg-muted px-2.5 py-1 rounded-full">
          {okCount}/{items.length} OK
        </span>
      </div>

      <div className="space-y-1.5">
        {items.map((item) => (
          <div
            key={item.label}
            className="flex items-center justify-between p-3 rounded-xl hover:bg-muted/50 transition-colors"
          >
            <div className="flex items-center gap-3">
              <div
                className={clsx(
                  "transition-colors",
                  item.status === "ok" && "text-green-600",
                  item.status === "warning" && "text-secondary",
                  item.status === "error" && "text-accent"
                )}
              >
                {item.icon}
              </div>
              <span className="text-sm text-foreground">{item.label}</span>
            </div>
            <div className="flex items-center gap-2.5">
              <span className="text-xs text-muted-foreground">{item.value}</span>
              <div
                className={clsx(
                  "w-2 h-2 rounded-full",
                  item.status === "ok" && "bg-green-500 shadow-sm shadow-green-200",
                  item.status === "warning" && "bg-secondary shadow-sm shadow-orange-200",
                  item.status === "error" && "bg-accent shadow-sm shadow-red-200"
                )}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
