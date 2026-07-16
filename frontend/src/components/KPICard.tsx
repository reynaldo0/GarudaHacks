"use client";

import clsx from "clsx";

interface KPICardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  trend?: "up" | "down" | "neutral";
  trendValue?: string;
  variant?: "default" | "success" | "warning" | "danger";
  delay?: number;
}

const variantConfig = {
  default: {
    iconBg: "bg-primary/10",
    iconText: "text-primary",
    border: "border-primary/10",
  },
  success: {
    iconBg: "bg-green-50",
    iconText: "text-green-600",
    border: "border-green-200",
  },
  warning: {
    iconBg: "bg-amber-50",
    iconText: "text-amber-600",
    border: "border-amber-200",
  },
  danger: {
    iconBg: "bg-red-50",
    iconText: "text-red-600",
    border: "border-red-200",
  },
};

export function KPICard({
  title,
  value,
  subtitle,
  icon,
  trend,
  trendValue,
  variant = "default",
  delay = 0,
}: KPICardProps) {
  const config = variantConfig[variant];

  return (
    <div
      className={clsx(
        "glass glass-hover rounded-2xl p-6 transition-all duration-300 hover:scale-[1.02] hover:shadow-lg animate-fade-in group",
        config.border
      )}
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-muted-foreground font-medium">{title}</p>
          <p className="text-3xl font-bold mt-2 text-foreground tracking-tight">{value}</p>
          {subtitle && (
            <p className="text-sm text-muted-foreground mt-1">{subtitle}</p>
          )}
        </div>
        <div
          className={clsx(
            "p-3 rounded-xl transition-transform duration-300 group-hover:scale-110",
            config.iconBg,
            config.iconText
          )}
        >
          {icon}
        </div>
      </div>
      {trend && (
        <div className="mt-4 flex items-center gap-2">
          <span
            className={clsx(
              "text-sm font-medium",
              trend === "up" && "text-green-600",
              trend === "down" && "text-red-600",
              trend === "neutral" && "text-muted-foreground"
            )}
          >
            {trendValue}
          </span>
        </div>
      )}
    </div>
  );
}
