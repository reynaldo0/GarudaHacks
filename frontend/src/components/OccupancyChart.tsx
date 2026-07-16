"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

interface OccupancyChartProps {
  data: Array<{
    carId: number;
    occupancy: number;
    status: string;
  }>;
}

const statusColors: Record<string, string> = {
  LOW: "#16A34A",
  NORMAL: "#22C55E",
  HIGH: "#F59E0B",
  FULL: "#F97316",
  OVERCAPACITY: "#ED242B",
};

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{ payload: { name: string; occupancy: number; status: string } }>;
}

function CustomTooltip({ active, payload }: CustomTooltipProps) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="glass rounded-lg px-3 py-2 shadow-xl">
      <p className="text-sm font-medium text-foreground">{d.name}</p>
      <p className="text-xs text-muted-foreground">
        Occupancy: <span className="text-primary font-medium">{d.occupancy.toFixed(1)}%</span>
      </p>
      <p className="text-xs text-muted-foreground">
        Status: <span className="text-foreground">{d.status}</span>
      </p>
    </div>
  );
}

export function OccupancyChart({ data }: OccupancyChartProps) {
  const chartData = data.map((d) => ({
    name: `Car ${d.carId}`,
    occupancy: d.occupancy,
    status: d.status,
  }));

  return (
    <div className="glass rounded-2xl p-6 animate-fade-in">
      <h3 className="text-lg font-semibold text-foreground mb-4">Occupancy by Car</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} barCategoryGap="20%">
            <defs>
              <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#2D2A70" stopOpacity={0.9} />
                <stop offset="100%" stopColor="#EC6C25" stopOpacity={0.6} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(45,42,112,0.08)" />
            <XAxis
              dataKey="name"
              stroke="#94A3B8"
              fontSize={11}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              stroke="#94A3B8"
              fontSize={11}
              domain={[0, 100]}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(45,42,112,0.04)" }} />
            <Bar dataKey="occupancy" radius={[6, 6, 0, 0]} maxBarSize={48}>
              {chartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={statusColors[entry.status] || "url(#barGradient)"}
                  fillOpacity={0.85}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
