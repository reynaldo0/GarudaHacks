"use client";

import { Clock, ArrowRight, AlertTriangle, CheckCircle, Radio } from "lucide-react";
import { useAppStore } from "@/store/useAppStore";
import clsx from "clsx";

export function Timeline() {
  const { systemState, warnings, timeline } = useAppStore();

  const events = [...timeline];

  if (warnings && warnings.length > 0) {
    warnings.forEach((w) => {
      const exists = events.some(
        (e) => e.id === `warn-${w.id}` || (e.type === "warning" && e.message.includes(`Car ${w.carId}`))
      );
      if (!exists) {
        events.push({
          id: `warn-${w.id}`,
          timestamp: w.timestamp || new Date().toISOString(),
          type: "warning",
          message: w.message || `Car ${w.carId}: ${w.warningType}`,
          severity: w.severity === "CRITICAL" ? "warning" : "info",
        });
      }
    });
  }

  if (systemState) {
    events.push({
      id: "sys-1",
      timestamp: systemState.timestamp || new Date().toISOString(),
      type: "system",
      message: `System active \u2014 ${systemState.system?.activeCameras || 0} cameras online`,
      severity: "success",
    });
  }

  events.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

  const iconMap = {
    warning: <AlertTriangle className="w-4 h-4 text-secondary" />,
    success: <CheckCircle className="w-4 h-4 text-green-600" />,
    info: <ArrowRight className="w-4 h-4 text-primary" />,
  };

  const dotColorMap = {
    warning: "bg-secondary",
    success: "bg-green-500",
    info: "bg-primary",
  };

  return (
    <div className="glass rounded-2xl p-6 animate-fade-in">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Clock className="w-5 h-5 text-primary" />
          <h3 className="text-lg font-semibold text-foreground">Timeline</h3>
        </div>
        <span className="text-xs text-muted-foreground bg-muted px-2.5 py-1 rounded-full">
          {events.length} events
        </span>
      </div>

      <div className="space-y-1 max-h-80 overflow-y-auto scrollbar-thin">
        {events.length === 0 ? (
          <div className="text-center py-8">
            <Radio className="w-6 h-6 text-muted-foreground mx-auto mb-2" />
            <p className="text-sm text-muted-foreground">No recent events</p>
          </div>
        ) : (
          events.slice(0, 12).map((event, idx) => (
            <div
              key={event.id || idx}
              className="flex items-start gap-3 p-3 rounded-xl hover:bg-muted/50 transition-colors group"
            >
              <div className="flex flex-col items-center">
                <div className={clsx("w-2 h-2 rounded-full mt-1.5", dotColorMap[event.severity] || "bg-muted-foreground")} />
                {idx < Math.min(events.length, 12) - 1 && (
                  <div className="w-[1px] flex-1 bg-border mt-1" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  {iconMap[event.severity] || iconMap.info}
                  <p className="text-sm text-foreground truncate">{event.message}</p>
                </div>
                <p className="text-[10px] text-muted-foreground mt-0.5 ml-6">
                  {new Date(event.timestamp).toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
