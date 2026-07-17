"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Train,
  History,
  PlayCircle,
  Activity,
  Wifi,
  WifiOff,
  Camera,
} from "lucide-react";
import clsx from "clsx";
import { useAppStore } from "@/store/useAppStore";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/train", label: "Train Status", icon: Train },
  { href: "/upload", label: "Frame Upload", icon: Camera },
  { href: "/history", label: "History", icon: History },
  { href: "/simulation", label: "Simulation", icon: PlayCircle },
];

export function Sidebar() {
  const pathname = usePathname();
  const { isConnected } = useAppStore();

  return (
    <aside className="fixed left-0 top-0 h-full w-64 flex flex-col z-50">
      <div className="absolute inset-0 bg-surface/90 backdrop-blur-xl border-r border-border" />

      <div className="relative flex flex-col h-full">
        <div className="p-6 border-b border-border">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-lg shadow-primary/25">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-foreground text-lg tracking-tight">
                THEMIS
              </h1>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={clsx(
                  "group flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200",
                  isActive
                    ? "bg-primary/10 text-primary font-medium"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted",
                )}
              >
                <div className="relative">
                  {isActive && (
                    <div className="absolute -left-2 top-1/2 -translate-y-1/2 w-1 h-5 rounded-full bg-gradient-to-b from-primary to-secondary" />
                  )}
                  <Icon className="w-5 h-5" />
                </div>
                <span className="text-sm">{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="px-4 mb-3">
          <div
            className={clsx(
              "flex items-center gap-2 px-3 py-2 rounded-lg text-xs",
              isConnected
                ? "bg-green-50 text-green-600"
                : "bg-red-50 text-red-600",
            )}
          >
            {isConnected ? (
              <Wifi className="w-3.5 h-3.5" />
            ) : (
              <WifiOff className="w-3.5 h-3.5" />
            )}
            <span>{isConnected ? "Connected" : "Disconnected"}</span>
          </div>
        </div>

        <div className="px-6 pb-4">
          <p className="text-[10px] text-muted-foreground">
            THEMIS v6.0 &middot; Garuda Hacks
          </p>
        </div>
      </div>
    </aside>
  );
}
