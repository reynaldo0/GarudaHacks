"use client";

import { useEffect, useState } from "react";
import { WifiOff, Loader2 } from "lucide-react";
import { apiClient } from "@/lib/api";
import { HistoryRecord, HistorySummary } from "@/types";
import clsx from "clsx";

export default function HistoryPage() {
  const [records, setRecords] = useState<HistoryRecord[]>([]);
  const [summary, setSummary] = useState<HistorySummary | null>(null);
  const [hours, setHours] = useState(24);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    async function fetchHistory() {
      setLoading(true);
      setError(false);
      try {
        const data = await apiClient.getHistory(hours);
        if (data?.records) {
          setRecords(data.records);
        }
        if (data?.summary) {
          setSummary(data.summary);
        }
      } catch {
        setError(true);
        setRecords([]);
        setSummary(null);
      } finally {
        setLoading(false);
      }
    }
    fetchHistory();
  }, [hours]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
          <p className="text-muted-foreground text-sm">Loading history...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="animate-fade-in">
          <h1 className="text-2xl font-bold text-foreground tracking-tight">History</h1>
          <p className="text-muted-foreground text-sm mt-1">Historical occupancy data</p>
        </div>
        <div className="flex items-center justify-center min-h-[40vh]">
          <div className="glass rounded-2xl p-10 max-w-md text-center animate-fade-in">
            <div className="w-16 h-16 rounded-2xl bg-red-50 flex items-center justify-center mx-auto mb-4">
              <WifiOff className="w-8 h-8 text-accent" />
            </div>
            <h2 className="text-xl font-bold text-foreground mb-2">Backend Offline</h2>
            <p className="text-muted-foreground text-sm">
              Unable to fetch history data. Ensure the backend is running.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between animate-fade-in">
        <div>
          <h1 className="text-2xl font-bold text-foreground tracking-tight">History</h1>
          <p className="text-muted-foreground text-sm mt-1">Historical spatial occupancy data</p>
        </div>
        <select
          value={hours}
          onChange={(e) => setHours(Number(e.target.value))}
          className="glass rounded-xl px-4 py-2 text-sm text-foreground bg-surface border border-border focus:outline-none focus:ring-2 focus:ring-primary/30 cursor-pointer"
        >
          <option value={6}>Last 6 hours</option>
          <option value={12}>Last 12 hours</option>
          <option value={24}>Last 24 hours</option>
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: "Average Occupancy", value: summary ? `${(summary.averageOccupancy * 100).toFixed(0)}%` : "--", color: "text-foreground" },
          { label: "Peak Occupancy", value: summary ? `${(summary.peakOccupancy * 100).toFixed(0)}%` : "--", color: "text-secondary" },
          { label: "Peak Time", value: summary?.peakTime || "--", color: "text-foreground" },
          { label: "Total Records", value: String(records.length), color: "text-foreground" },
        ].map((card, i) => (
          <div key={i} className="glass glass-hover rounded-2xl p-6 animate-fade-in" style={{ animationDelay: `${i * 50}ms` }}>
            <p className="text-sm text-muted-foreground font-medium">{card.label}</p>
            <p className={`text-3xl font-bold mt-2 tracking-tight ${card.color}`}>{card.value}</p>
          </div>
        ))}
      </div>

      <div className="glass rounded-2xl overflow-hidden animate-fade-in">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left p-4 text-xs font-medium text-muted-foreground uppercase tracking-wider">Timestamp</th>
                <th className="text-left p-4 text-xs font-medium text-muted-foreground uppercase tracking-wider">Car</th>
                <th className="text-left p-4 text-xs font-medium text-muted-foreground uppercase tracking-wider">Occupancy</th>
                <th className="text-left p-4 text-xs font-medium text-muted-foreground uppercase tracking-wider">Density</th>
              </tr>
            </thead>
            <tbody>
              {records.length === 0 ? (
                <tr>
                  <td colSpan={4} className="p-8 text-center text-muted-foreground text-sm">
                    No records found for this time range
                  </td>
                </tr>
              ) : (
                records.slice(-50).reverse().map((record, idx) => {
                  const occ = record.occupancyRatio;
                  return (
                    <tr
                      key={idx}
                      className="border-b border-border/50 last:border-0 hover:bg-muted/30 transition-colors"
                    >
                      <td className="p-4 text-sm text-foreground">
                        {new Date(record.timestamp).toLocaleTimeString()}
                      </td>
                      <td className="p-4 text-sm text-foreground font-medium">Car {record.carId}</td>
                      <td className="p-4 text-sm">
                        <div className="flex items-center gap-2">
                          <div className="w-16 h-1.5 rounded-full bg-muted overflow-hidden">
                            <div
                              className={clsx(
                                "h-full rounded-full",
                                record.densityIndicator === "RED" ? "bg-red-500" :
                                record.densityIndicator === "YELLOW" ? "bg-amber-500" : "bg-green-500"
                              )}
                              style={{ width: `${Math.min(occ * 100, 100)}%` }}
                            />
                          </div>
                          <span className="text-foreground">{(occ * 100).toFixed(0)}%</span>
                        </div>
                      </td>
                      <td className="p-4">
                        <span className={clsx(
                          "px-2.5 py-1 rounded-lg text-xs font-medium",
                          record.densityIndicator === "RED" && "bg-red-50 text-red-600",
                          record.densityIndicator === "YELLOW" && "bg-amber-50 text-amber-600",
                          record.densityIndicator === "GREEN" && "bg-green-50 text-green-600",
                        )}>
                          {record.densityIndicator}
                        </span>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
