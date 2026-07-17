"use client";

import { useEffect, useCallback, useRef, useState } from "react";
import Link from "next/link";
import {
  Activity, Train, Shield, Zap, Eye, BarChart3, ArrowRight, ChevronRight,
  Bell, DoorOpen, Wrench, GitBranch, AlertTriangle, Clock,
} from "lucide-react";
import clsx from "clsx";
import { useAppStore } from "@/store/useAppStore";
import { CarSpatialOccupancy } from "@/types";

const features = [
  { icon: Eye, title: "Spatial Occupancy Intelligence", desc: "AI estimates usable space inside each carriage using 4 ceiling fisheye cameras.", color: "from-blue-500 to-blue-600" },
  { icon: GitBranch, title: "Real-time Fusion Engine", desc: "4 camera occupancy grids fused into a single carriage map per frame.", color: "from-violet-500 to-violet-600" },
  { icon: BarChart3, title: "Redistribution AI", desc: "When congestion is detected, the system recommends the optimal target carriage.", color: "from-primary to-secondary" },
  { icon: Wrench, title: "Bogie Predictive Maintenance", desc: "CALES engine tracks cumulative asymmetric load exposure for health prediction.", color: "from-amber-500 to-orange-500" },
  { icon: DoorOpen, title: "Smart Door Automation", desc: "Door recommendations follow a safety chain with rule engine validation.", color: "from-emerald-500 to-emerald-600" },
  { icon: Bell, title: "Instant Alerts & Announcements", desc: "CRITICAL density triggers real-time WebSocket alerts and voice announcements.", color: "from-rose-500 to-rose-600" },
];

const pipelineSteps = [
  { label: "4 Fisheye Cameras", sub: "per carriage" },
  { label: "Image Preprocessing", sub: "undistort + resize" },
  { label: "Spatial Segmentation", sub: "occupancy grid" },
  { label: "4-Grid Fusion", sub: "weighted merge" },
  { label: "Density Classification", sub: "GREEN / YELLOW / RED" },
  { label: "Redistribution AI", sub: "target recommendation" },
  { label: "CALES Engine", sub: "bogie health scoring" },
  { label: "Door Logic", sub: "safety chain validation" },
  { label: "PipelineState Output", sub: "WebSocket + REST" },
];

function getWsUrl(): string {
  if (typeof window === "undefined") return "";
  const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${proto}//${window.location.host}/ws`;
}

const DC: Record<string, { fill: string; border: string }> = {
  GREEN: { fill: "from-green-400/70 to-emerald-500/70", border: "border-green-300/60" },
  YELLOW: { fill: "from-amber-400/70 to-yellow-500/70", border: "border-amber-300/60" },
  RED: { fill: "from-red-400/70 to-rose-500/70", border: "border-red-300/60" },
};

export default function LandingPage() {
  const { cars, warnings, isConnected, setCars, setWarnings, setConnected, setRecommendation, setSystemHealth } = useAppStore();
  const wsRef = useRef<WebSocket | null>(null);
  const retryRef = useRef(0);
  const reconnectTimer = useRef<NodeJS.Timeout | null>(null);
  const [uptime, setUptime] = useState(0);

  const handleWsMessage = useCallback((msg: { type: string; data?: Record<string, unknown> }) => {
    const store = useAppStore.getState();
    switch (msg.type) {
      case "pipeline_state_updated":
      case "spatial_occupancy_updated": {
        if (!msg.data) break;
        const d = msg.data;
        const carId = typeof d.car_id === "string" ? parseInt(d.car_id.replace(/\D/g, ""), 10) : (d.car_id as number);
        if (carId > 0) {
          const updated: CarSpatialOccupancy = {
            carId,
            occupancyRatio: (d.occupancy_ratio as number) ?? 0,
            freeSpaceRatio: (d.free_space_ratio as number) ?? 1,
            densityIndicator: (d.density_indicator as "GREEN" | "YELLOW" | "RED") ?? "GREEN",
            spatialOccupancyScore: (d.spatial_occupancy_score as number) ?? 0,
            cameraStatus: "active",
            riskScore: (d.occupancy_ratio as number) ?? 0,
            prediction: (d.prediction as CarSpatialOccupancy["prediction"]) ?? null,
          };
          const current = [...store.cars];
          const idx = current.findIndex((c) => c.carId === carId);
          if (idx >= 0) current[idx] = updated;
          else current.push(updated);
          store.setCars(current);
        }
        break;
      }
      case "occupancy_updated": {
        if (!msg.data) break;
        const carsList = (msg.data.cars as Array<Record<string, unknown>>) || [];
        if (Array.isArray(carsList)) {
          store.setCars(carsList.map((c) => ({
            carId: (c.car_id as number) ?? 0,
            occupancyRatio: (c.occupancy_ratio as number) ?? 0,
            freeSpaceRatio: (c.free_space_ratio as number) ?? 1,
            densityIndicator: (c.density_indicator as "GREEN" | "YELLOW" | "RED") ?? "GREEN",
            spatialOccupancyScore: (c.spatial_occupancy_score as number) ?? 0,
            cameraStatus: (c.camera_status as string) || "active",
            cameraId: (c.camera_id as string) || undefined,
            riskScore: (c.risk_score as number) ?? 0,
            prediction: null,
          })));
        }
        break;
      }
      case "warning_updated": {
        if (!msg.data) break;
        const w = (msg.data.warning as Record<string, unknown>) || msg.data;
        const nw = {
          id: (w.id as string) || `warn-${Date.now()}`,
          trainId: (w.trainId as string) || (w.train_id as string) || "",
          carId: (w.carId as number) ?? (w.car_id as number) ?? 0,
          warningType: (w.warningType as string) || (w.warning_type as string) || "unknown",
          severity: (w.severity as string) || "INFO",
          message: (w.message as string) || "",
          timestamp: (w.timestamp as string) || new Date().toISOString(),
          isActive: true,
        };
        if (!store.warnings.some((x) => x.id === nw.id)) store.setWarnings([...store.warnings, nw]);
        break;
      }
      case "system_health_updated": {
        if (!msg.data) break;
        const h = (msg.data.health as Record<string, unknown>) || msg.data;
        store.setSystemHealth([
          { label: "Backend", status: h.backend === "running" ? "ok" : "error", value: String(h.backend ?? "unknown"), icon: "server" },
          { label: "AI Pipeline", status: h.ai === "loaded" ? "ok" : "warning", value: String(h.ai ?? "offline"), icon: "cpu" },
          { label: "Cameras", status: (h.cameras as number) > 0 ? "ok" : "warning", value: `${h.cameras ?? 0} active`, icon: "camera" },
          { label: "Uptime", status: "ok", value: `${Math.floor((h.uptime as number ?? 0) / 60)}m`, icon: "clock" },
          { label: "Warnings", status: (h.activeWarnings as number) > 0 ? "warning" : "ok", value: `${h.activeWarnings ?? 0} active`, icon: "alert" },
        ]);
        setUptime((h.uptime as number) ?? 0);
        break;
      }
      case "recommendation_changed": {
        if (!msg.data) break;
        const r = (msg.data.recommendation as Record<string, unknown>) || msg.data;
        store.setRecommendation(r as never);
        break;
      }
    }
  }, []);

  useEffect(() => {
    async function fetchInitial() {
      try {
        const [stateRes, occRes, warnRes] = await Promise.allSettled([
          fetch("/api/v1/state").then((r) => r.json()),
          fetch("/api/v1/occupancy").then((r) => r.json()),
          fetch("/api/v1/history/warnings").then((r) => r.json()),
        ]);
        if (occRes.status === "fulfilled" && occRes.value?.data?.cars) {
          setCars(occRes.value.data.cars.map((c: Record<string, unknown>) => ({
            carId: c.carId ?? c.car_id,
            occupancyRatio: c.occupancyRatio ?? c.occupancy_ratio ?? 0,
            freeSpaceRatio: c.freeSpaceRatio ?? c.free_space_ratio ?? 1,
            densityIndicator: c.densityIndicator ?? c.density_indicator ?? "GREEN",
            spatialOccupancyScore: c.spatialOccupancyScore ?? c.spatial_occupancy_score ?? 0,
            cameraStatus: c.cameraStatus ?? c.camera_status ?? "active",
            cameraId: c.cameraId ?? c.camera_id,
            riskScore: c.riskScore ?? c.risk_score ?? 0,
            prediction: c.prediction ?? null,
          })));
        }
        if (warnRes.status === "fulfilled" && warnRes.value?.data?.warnings) setWarnings(warnRes.value.data.warnings);
        if (stateRes.status === "fulfilled" && stateRes.value?.data?.system) setUptime(stateRes.value.data.system.uptimeSeconds ?? 0);
      } catch {}
    }
    fetchInitial();
  }, [setCars, setWarnings]);

  useEffect(() => {
    function connect() {
      if (wsRef.current?.readyState === WebSocket.OPEN) return;
      const ws = new WebSocket(getWsUrl());
      wsRef.current = ws;
      ws.onopen = () => { setConnected(true); retryRef.current = 0; };
      ws.onmessage = (e) => { try { handleWsMessage(JSON.parse(e.data)); } catch {} };
      ws.onclose = () => {
        setConnected(false);
        if (retryRef.current < 5) {
          reconnectTimer.current = setTimeout(connect, Math.min(1000 * 2 ** retryRef.current, 15000));
          retryRef.current++;
        }
      };
      ws.onerror = () => ws.close();
    }
    connect();
    return () => {
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      if (wsRef.current) { wsRef.current.close(); wsRef.current = null; }
    };
  }, [setConnected, handleWsMessage]);

  const avgOcc = cars.length > 0 ? cars.reduce((s, c) => s + c.occupancyRatio, 0) / cars.length : 0;
  const greenCars = cars.filter((c) => c.densityIndicator === "GREEN").length;
  const yellowCars = cars.filter((c) => c.densityIndicator === "YELLOW").length;
  const redCars = cars.filter((c) => c.densityIndicator === "RED").length;
  const critWarnings = warnings.filter((w) => w.severity === "CRITICAL").length;

  const kpis = [
    { label: "Avg Occupancy", value: `${(avgOcc * 100).toFixed(1)}%`, icon: <BarChart3 className="w-4 h-4" />, accent: redCars > 0 ? "text-red-600" : yellowCars > 0 ? "text-amber-600" : "text-green-600" },
    { label: "RED Cars", value: String(redCars), icon: <AlertTriangle className="w-4 h-4" />, accent: redCars > 0 ? "text-red-600" : "text-green-600" },
    { label: "Warnings", value: String(critWarnings), icon: <Bell className="w-4 h-4" />, accent: critWarnings > 0 ? "text-amber-600" : "text-green-600" },
    { label: "Uptime", value: `${Math.floor(uptime / 60)}m`, icon: <Clock className="w-4 h-4" />, accent: "text-primary" },
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass border-b border-border/50 backdrop-blur-xl bg-background/80">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-lg shadow-primary/20">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-foreground text-lg tracking-tight">THEMIS</span>
            <span className="text-[10px] text-muted-foreground font-medium">v6.0</span>
          </div>
          <div className="flex items-center gap-4">
            <div className="hidden sm:flex items-center gap-2 text-xs text-muted-foreground">
              <div className={clsx("w-2 h-2 rounded-full", isConnected ? "bg-green-500 animate-pulse" : "bg-red-500")} />
              {isConnected ? "Live" : "Offline"}
            </div>
            <Link href="/dashboard" className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-primary to-secondary text-white text-sm font-medium hover:shadow-lg hover:shadow-primary/25 transition-all duration-200 hover:scale-[1.02]">
              Open Dashboard
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero + Live Preview */}
      <section className="relative pt-28 pb-16 px-6 overflow-hidden">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute -top-40 -right-40 w-[500px] h-[500px] rounded-full bg-primary/4 blur-3xl" />
          <div className="absolute -bottom-40 -left-40 w-[500px] h-[500px] rounded-full bg-secondary/4 blur-3xl" />
        </div>
        <div className="max-w-7xl mx-auto relative">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Left: Text */}
            <div>
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass border border-border/50 text-xs font-medium text-muted-foreground mb-6">
                <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
                AI-powered Railway Decision Intelligence
              </div>
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-foreground tracking-tight leading-[1.08]">
                Spatial Occupancy{" "}
                <span className="bg-gradient-to-r from-primary via-secondary to-primary bg-clip-text text-transparent">Intelligence</span>{" "}
                for KRL Commuter Line
              </h1>
              <p className="mt-6 text-base md:text-lg text-muted-foreground leading-relaxed max-w-xl">
                Real-time carriage occupancy estimation using ceiling fisheye cameras and AI segmentation.
                Measuring available usable space to support operational decisions.
              </p>
              <div className="flex flex-wrap gap-3 mt-8">
                <Link href="/dashboard" className="inline-flex items-center gap-2 px-7 py-3.5 rounded-xl bg-gradient-to-r from-primary to-secondary text-white font-medium shadow-lg shadow-primary/20 hover:shadow-xl hover:shadow-primary/30 transition-all duration-200 hover:scale-[1.02]">
                  <Zap className="w-4 h-4" />
                  Open Operation Center
                  <ArrowRight className="w-4 h-4" />
                </Link>
                <a href="#how-it-works" className="inline-flex items-center gap-2 px-7 py-3.5 rounded-xl glass border border-border text-foreground font-medium hover:bg-muted/50 transition-all duration-200">
                  How It Works
                </a>
              </div>
              {/* Live KPIs */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-10">
                {kpis.map((s, i) => (
                  <div key={i} className="glass rounded-xl p-3.5 animate-fade-in" style={{ animationDelay: `${i * 60}ms` }}>
                    <div className="flex items-center gap-1.5 text-muted-foreground mb-1.5">
                      {s.icon}
                      <span className="text-[11px] font-medium">{s.label}</span>
                    </div>
                    <p className={clsx("text-xl font-bold", s.accent)}>{s.value}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Right: Live Train + Warnings */}
            <div className="space-y-4">
              <div className="glass rounded-2xl p-5 border border-border/50 shadow-xl shadow-black/5">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Train className="w-5 h-5 text-primary" />
                    <h3 className="font-semibold text-foreground">Live Train — SF6</h3>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <div className={clsx("w-2 h-2 rounded-full", isConnected ? "bg-green-500 animate-pulse" : "bg-red-500")} />
                    <span className="text-[11px] text-muted-foreground">{isConnected ? "Real-time" : "Static"}</span>
                  </div>
                </div>
                <div className="relative rounded-xl bg-gradient-to-b from-muted/20 to-muted/50 border border-border p-3">
                  <div className="absolute bottom-3 left-3 right-3 h-[2px] bg-muted-foreground/15 rounded-full" />
                  <div className="flex items-end gap-0 relative z-10">
                    <div className="flex-shrink-0 w-6">
                      <svg viewBox="0 0 24 40" className="w-full" fill="none">
                        <path d="M22 3 C22 1.5, 20 0, 17 0 L7 0 C4 0, 2 1.5, 2 3 L2 37 C2 38.5, 4 40, 7 40 L17 40 C20 40, 22 38.5, 22 37 Z" fill="hsl(var(--muted))" stroke="hsl(var(--border))" strokeWidth="1"/>
                        <circle cx="12" cy="36" r="2" fill="hsl(var(--muted-foreground))" opacity="0.2"/>
                      </svg>
                    </div>
                    {Array.from({ length: 6 }, (_, i) => {
                      const car = cars.find((c) => c.carId === i + 1);
                      const occ = car ? car.occupancyRatio : [0.85, 0.72, 0.55, 0.40, 0.65, 0.30][i];
                      const ind = car ? car.densityIndicator : (occ > 0.7 ? "RED" : occ > 0.4 ? "YELLOW" : "GREEN");
                      const dc = DC[ind] || DC.GREEN;
                      return (
                        <div key={i} className="flex-1 mx-[1px]">
                          <div className={clsx("relative rounded border-2 overflow-hidden transition-all duration-500", dc.border)} style={{ aspectRatio: "2/1" }}>
                            <div className={clsx("absolute bottom-0 left-0 right-0 bg-gradient-to-t rounded-b-sm", dc.fill)} style={{ height: `${occ * 100}%` }} />
                            <div className="absolute top-[12%] left-[8%] right-[8%] flex gap-[5%] h-[30%]">
                              {[0,1,2].map(w => <div key={w} className="flex-1 rounded-sm bg-white/15 border border-white/20" />)}
                            </div>
                            <div className="absolute inset-0 flex items-center justify-center z-10">
                              <div className="text-center">
                                <span className="text-[10px] sm:text-xs font-bold text-foreground drop-shadow-sm">{i + 1}</span>
                                <span className="block text-[8px] font-semibold text-foreground/70">{(occ * 100).toFixed(0)}%</span>
                              </div>
                            </div>
                            <div className="absolute -bottom-1.5 left-[18%] w-2 h-2 rounded-full bg-muted-foreground/20" />
                            <div className="absolute -bottom-1.5 right-[18%] w-2 h-2 rounded-full bg-muted-foreground/20" />
                          </div>
                        </div>
                      );
                    })}
                    <div className="flex-shrink-0 w-3">
                      <svg viewBox="0 0 12 40" className="w-full" fill="none">
                        <path d="M10 3 C10 1.5, 8 0, 6 0 L3 0 C1.5 0, 0 1.5, 0 3 L0 37 C0 38.5, 1.5 40, 3 40 L6 40 C8 40, 10 38.5, 10 37 Z" fill="hsl(var(--muted))" stroke="hsl(var(--border))" strokeWidth="1"/>
                      </svg>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-4 mt-3 text-[10px] text-muted-foreground">
                  <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-green-500" /> GREEN</div>
                  <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-amber-500" /> YELLOW</div>
                  <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-red-500" /> RED</div>
                  <span className="ml-auto font-medium">{cars.length} / 6 gerbong</span>
                </div>
              </div>

              {/* Warnings Feed */}
              <div className="glass rounded-2xl p-5 border border-border/50">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Bell className="w-4 h-4 text-amber-500" />
                    <h3 className="text-sm font-semibold text-foreground">Active Warnings</h3>
                  </div>
                  <span className="text-[10px] text-muted-foreground bg-muted px-2 py-0.5 rounded-full">{warnings.length}</span>
                </div>
                {warnings.length === 0 ? (
                  <div className="text-center py-4">
                    <Shield className="w-8 h-8 text-green-500/30 mx-auto mb-2" />
                    <p className="text-xs text-muted-foreground">No active warnings</p>
                  </div>
                ) : (
                  <div className="space-y-2 max-h-32 overflow-y-auto">
                    {warnings.slice(0, 4).map((w) => (
                      <div key={w.id} className={clsx("flex items-start gap-2 p-2 rounded-lg border text-xs", w.severity === "CRITICAL" ? "bg-red-50 border-red-100" : "bg-amber-50 border-amber-100")}>
                        <AlertTriangle className={clsx("w-3.5 h-3.5 mt-0.5 flex-shrink-0", w.severity === "CRITICAL" ? "text-red-500" : "text-amber-500")} />
                        <div className="min-w-0">
                          <p className="font-medium text-foreground truncate">{w.message}</p>
                          <p className="text-muted-foreground mt-0.5">{new Date(w.timestamp).toLocaleTimeString()}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-6 bg-muted/20">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-foreground tracking-tight">Platform Capabilities</h2>
            <p className="text-muted-foreground mt-3 max-w-xl mx-auto">9 AI engines working in sequence to deliver real-time spatial intelligence.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {features.map((f, i) => {
              const Icon = f.icon;
              return (
                <div key={i} className="glass glass-hover rounded-2xl p-6 animate-fade-in group" style={{ animationDelay: `${i * 60}ms` }}>
                  <div className={`w-11 h-11 rounded-xl bg-gradient-to-br ${f.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                    <Icon className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="font-semibold text-foreground mb-2">{f.title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">{f.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Pipeline Flow */}
      <section id="how-it-works" className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-foreground tracking-tight">AI Pipeline Flow</h2>
            <p className="text-muted-foreground mt-3 max-w-xl mx-auto">From camera capture to operational decision — 9 steps in under 5 seconds.</p>
          </div>
          <div className="glass rounded-2xl p-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
              {pipelineSteps.map((step, i) => (
                <div key={i} className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white text-xs font-bold">{i + 1}</div>
                  <div>
                    <p className="text-sm font-semibold text-foreground">{step.label}</p>
                    <p className="text-xs text-muted-foreground">{step.sub}</p>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-8 pt-6 border-t border-border flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
              {pipelineSteps.map((step, i, arr) => (
                <span key={i} className="flex items-center gap-2">
                  <span className="px-2.5 py-1 rounded-lg bg-muted border border-border font-medium text-foreground">{step.label}</span>
                  {i < arr.length - 1 && <ChevronRight className="w-3 h-3 text-muted-foreground/40" />}
                </span>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="glass rounded-3xl p-10 md:p-14 text-center relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-secondary/5 pointer-events-none" />
            <div className="relative">
              <Shield className="w-12 h-12 text-primary mx-auto mb-4" />
              <h2 className="text-3xl font-bold text-foreground tracking-tight mb-3">Ready to Monitor?</h2>
              <p className="text-muted-foreground max-w-lg mx-auto mb-8">
                Access the Operation Center for real-time spatial occupancy monitoring, AI-driven redistribution, and bogie predictive maintenance.
              </p>
              <Link href="/dashboard" className="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl bg-gradient-to-r from-primary to-secondary text-white font-medium hover:shadow-lg hover:shadow-primary/25 transition-all duration-200 hover:scale-[1.02]">
                <Zap className="w-4 h-4" />
                Open Operation Center
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-8 px-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
              <Activity className="w-4 h-4 text-white" />
            </div>
            <span className="text-sm font-semibold text-foreground">THEMIS v6.0</span>
          </div>
          <p className="text-xs text-muted-foreground">AI-powered Railway Decision Intelligence Platform &middot; Garuda Hacks 2026</p>
        </div>
      </footer>
    </div>
  );
}
