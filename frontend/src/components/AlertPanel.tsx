"use client";

import { AlertTriangle, Info, AlertCircle } from "lucide-react";
import clsx from "clsx";

interface Warning {
  id: string;
  trainId: string;
  carId: number;
  warningType: string;
  severity: string;
  message: string;
  timestamp: string;
}

interface AlertPanelProps {
  warnings: Warning[];
}

const severityConfig: Record<string, { icon: React.ReactNode; bg: string; border: string; text: string; dot: string }> = {
  CRITICAL: {
    icon: <AlertCircle className="w-4 h-4" />,
    bg: "bg-red-50",
    border: "border-red-200",
    text: "text-red-600",
    dot: "bg-red-500",
  },
  WARNING: {
    icon: <AlertTriangle className="w-4 h-4" />,
    bg: "bg-amber-50",
    border: "border-amber-200",
    text: "text-amber-600",
    dot: "bg-amber-500",
  },
  INFO: {
    icon: <Info className="w-4 h-4" />,
    bg: "bg-blue-50",
    border: "border-blue-200",
    text: "text-blue-600",
    dot: "bg-blue-500",
  },
};

export function AlertPanel({ warnings }: AlertPanelProps) {
  return (
    <div className="glass rounded-2xl p-6 animate-fade-in">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-secondary" />
          <h3 className="text-lg font-semibold text-foreground">Active Alerts</h3>
        </div>
        <span className="text-xs text-muted-foreground bg-muted px-2.5 py-1 rounded-full">
          {warnings.length}
        </span>
      </div>

      <div className="space-y-2 max-h-80 overflow-y-auto scrollbar-thin">
        {warnings.length === 0 ? (
          <div className="text-center py-8">
            <div className="w-10 h-10 rounded-full bg-green-50 flex items-center justify-center mx-auto mb-3">
              <Info className="w-5 h-5 text-green-600" />
            </div>
            <p className="text-sm text-muted-foreground">No active alerts</p>
          </div>
        ) : (
          warnings.map((warning, idx) => {
            const config = severityConfig[warning.severity] || severityConfig.INFO;
            return (
              <div
                key={warning.id || idx}
                className={clsx(
                  "border rounded-xl p-3.5 flex items-start gap-3 transition-all duration-200 hover:bg-muted/50",
                  config.bg,
                  config.border
                )}
              >
                <div className={clsx("mt-0.5", config.text)}>{config.icon}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-sm font-medium text-foreground">Car {warning.carId}</span>
                    <div className="flex items-center gap-1.5">
                      <div className={clsx("w-1.5 h-1.5 rounded-full", config.dot)} />
                      <span className={clsx("text-[10px] uppercase tracking-wider font-medium", config.text)}>
                        {warning.severity}
                      </span>
                    </div>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{warning.message}</p>
                  <p className="text-[10px] text-muted-foreground mt-1">
                    {new Date(warning.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
