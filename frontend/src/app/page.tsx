"use client";

import Link from "next/link";
import {
  Activity,
  Train,
  Shield,
  Zap,
  Eye,
  BarChart3,
  ArrowRight,
  ChevronRight,
  Camera,
  Bell,
  DoorOpen,
  Wrench,
  GitBranch,
} from "lucide-react";

const features = [
  {
    icon: Eye,
    title: "Spatial Occupancy Intelligence",
    desc: "AI estimates usable space inside each carriage using 4 ceiling fisheye cameras — not people counting, but spatial analysis.",
    color: "from-primary to-primary/80",
  },
  {
    icon: GitBranch,
    title: "Real-time Fusion Engine",
    desc: "4 camera occupancy grids fused into a single carriage map per frame. Density classified as GREEN / YELLOW / RED in real-time.",
    color: "from-secondary to-secondary/80",
  },
  {
    icon: BarChart3,
    title: "Redistribution AI",
    desc: "When congestion is detected, the system recommends the optimal target carriage and generates passenger announcements.",
    color: "from-primary to-secondary",
  },
  {
    icon: Wrench,
    title: "Bogie Predictive Maintenance",
    desc: "CALES engine tracks cumulative asymmetric load exposure — predicting health index, remaining useful life, and inspection priority.",
    color: "from-secondary to-accent",
  },
  {
    icon: DoorOpen,
    title: "Smart Door Automation",
    desc: "Door recommendations follow a safety chain: Redistribution → Rule Engine → Validation → Safety Check → Door Recommendation.",
    color: "from-primary to-primary/60",
  },
  {
    icon: Bell,
    title: "Instant Alerts & Announcements",
    desc: "CRITICAL density triggers real-time WebSocket alerts and automated voice announcements guiding passengers to available carriages.",
    color: "from-accent to-accent/80",
  },
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

const stats = [
  { value: "10", label: "Carriages", suffix: "" },
  { value: "40", label: "Cameras", suffix: "" },
  { value: "5", label: "sec interval", suffix: "" },
  { value: "12", label: "AI engines", suffix: "" },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* ── Navbar ── */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass border-b border-border/50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-foreground text-lg tracking-tight">THEMIS</span>
          </div>
          <div className="flex items-center gap-3">
            <Link
              href="/dashboard"
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-primary to-secondary text-white text-sm font-medium hover:shadow-lg hover:shadow-primary/25 transition-all duration-200 hover:scale-[1.02]"
            >
              Open Dashboard
            </Link>
          </div>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="relative pt-32 pb-20 px-6 overflow-hidden">
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-96 h-96 rounded-full bg-primary/5 blur-3xl" />
          <div className="absolute -bottom-40 -left-40 w-96 h-96 rounded-full bg-secondary/5 blur-3xl" />
        </div>

        <div className="max-w-7xl mx-auto relative">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full glass border border-border/50 text-xs font-medium text-muted-foreground mb-6">
              <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
              AI-powered Railway Decision Intelligence
            </div>

            <h1 className="text-5xl md:text-6xl font-bold text-foreground tracking-tight leading-[1.1]">
              Spatial Occupancy{" "}
              <span className="gradient-text">Intelligence</span>{" "}
              for KRL Commuter Line
            </h1>

            <p className="mt-6 text-lg text-muted-foreground leading-relaxed max-w-2xl">
              Real-time carriage occupancy estimation using ceiling fisheye cameras and AI segmentation.
              Not people counting — but measuring available usable space to support operational decisions.
            </p>

            <div className="flex flex-wrap gap-3 mt-8">
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-primary to-secondary text-white font-medium hover:shadow-lg hover:shadow-primary/25 transition-all duration-200 hover:scale-[1.02]"
              >
                Open Operation Center
                <ArrowRight className="w-4 h-4" />
              </Link>
              <a
                href="#how-it-works"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl glass border border-border text-foreground font-medium hover:bg-muted transition-all duration-200"
              >
                How It Works
              </a>
            </div>
          </div>

          {/* Stats bar */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-16">
            {stats.map((s, i) => (
              <div
                key={i}
                className="glass glass-hover rounded-2xl p-5 text-center animate-fade-in"
                style={{ animationDelay: `${i * 80}ms` }}
              >
                <p className="text-3xl font-bold gradient-text">
                  {s.value}{s.suffix}
                </p>
                <p className="text-xs text-muted-foreground mt-1 font-medium">{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Features ── */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-foreground tracking-tight">Platform Capabilities</h2>
            <p className="text-muted-foreground mt-3 max-w-xl mx-auto">
              9 AI engines working in sequence to deliver real-time spatial intelligence for every carriage.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {features.map((f, i) => {
              const Icon = f.icon;
              return (
                <div
                  key={i}
                  className="glass glass-hover rounded-2xl p-6 animate-fade-in group"
                  style={{ animationDelay: `${i * 60}ms` }}
                >
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

      {/* ── Pipeline Flow ── */}
      <section id="how-it-works" className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-foreground tracking-tight">AI Pipeline Flow</h2>
            <p className="text-muted-foreground mt-3 max-w-xl mx-auto">
              From camera capture to operational decision — 9 steps in under 5 seconds.
            </p>
          </div>

          <div className="glass rounded-2xl p-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {pipelineSteps.map((step, i) => (
                <div key={i} className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white text-xs font-bold">
                    {i + 1}
                  </div>
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
                  <span className="px-2.5 py-1 rounded-lg bg-muted border border-border font-medium text-foreground">
                    {step.label}
                  </span>
                  {i < arr.length - 1 && (
                    <ChevronRight className="w-3 h-3 text-muted-foreground/40" />
                  )}
                </span>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── Train Overview ── */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
            <div>
              <h2 className="text-3xl font-bold text-foreground tracking-tight mb-4">
                SF10 Formation — 10 Carriages
              </h2>
              <p className="text-muted-foreground leading-relaxed mb-6">
                Each carriage is equipped with 4 ceiling fisheye cameras providing full interior coverage.
                The AI analyzes spatial occupancy in real-time and classifies density into three levels.
              </p>
              <div className="space-y-3">
                {[
                  { color: "bg-green-500", label: "GREEN", desc: "Free space > 60% — comfortable" },
                  { color: "bg-amber-500", label: "YELLOW", desc: "Free space 30–60% — moderate" },
                  { color: "bg-red-500", label: "RED", desc: "Free space < 30% — redistribution needed" },
                ].map((d, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${d.color}`} />
                    <div>
                      <span className="text-sm font-semibold text-foreground">{d.label}</span>
                      <span className="text-sm text-muted-foreground ml-2">{d.desc}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="glass rounded-2xl p-6">
              <div className="flex items-center gap-2 mb-4">
                <Train className="w-5 h-5 text-primary" />
                <h3 className="font-semibold text-foreground">Live Train Visualization</h3>
              </div>
              <div className="flex gap-1.5">
                {Array.from({ length: 10 }, (_, i) => {
                  const occ = [0.85, 0.72, 0.55, 0.40, 0.65, 0.30, 0.20, 0.15, 0.45, 0.90][i];
                  const color =
                    occ > 0.7 ? "bg-red-500" : occ > 0.4 ? "bg-amber-500" : "bg-green-500";
                  return (
                    <div key={i} className="flex-1 text-center">
                      <div className="relative h-32 rounded-lg bg-muted border border-border overflow-hidden mb-1.5">
                        <div
                          className={`absolute bottom-0 left-0 right-0 ${color} rounded-b-lg transition-all duration-700`}
                          style={{ height: `${occ * 100}%` }}
                        />
                      </div>
                      <p className="text-[10px] text-muted-foreground font-medium">C{i + 1}</p>
                      <p className="text-[10px] text-foreground font-bold">{(occ * 100).toFixed(0)}%</p>
                    </div>
                  );
                })}
              </div>
              <div className="flex items-center gap-4 mt-4 text-[10px] text-muted-foreground">
                <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-green-500" /> GREEN</div>
                <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-amber-500" /> YELLOW</div>
                <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-red-500" /> RED</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="glass rounded-3xl p-10 md:p-14 text-center relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-secondary/5 pointer-events-none" />
            <div className="relative">
              <Shield className="w-12 h-12 text-primary mx-auto mb-4" />
              <h2 className="text-3xl font-bold text-foreground tracking-tight mb-3">
                Ready to Monitor?
              </h2>
              <p className="text-muted-foreground max-w-lg mx-auto mb-8">
                Access the Operation Center for real-time spatial occupancy monitoring, AI-driven redistribution recommendations, and bogie predictive maintenance insights.
              </p>
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl bg-gradient-to-r from-primary to-secondary text-white font-medium hover:shadow-lg hover:shadow-primary/25 transition-all duration-200 hover:scale-[1.02]"
              >
                <Zap className="w-4 h-4" />
                Open Operation Center
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="border-t border-border py-8 px-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
              <Activity className="w-4 h-4 text-white" />
            </div>
            <span className="text-sm font-semibold text-foreground">THEMIS v6.0</span>
          </div>
          <p className="text-xs text-muted-foreground">
            AI-powered Railway Decision Intelligence Platform &middot; Garuda Hacks 2026
          </p>
        </div>
      </footer>
    </div>
  );
}
