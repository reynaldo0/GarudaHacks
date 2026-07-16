"use client";

import { Recommendation } from "@/types";

interface TransferAnimationProps {
  recommendation: Recommendation | null;
  carCount: number;
  showWomenAlternative?: boolean;
}

const CARD_W = 112;
const GAP = 12;
const PARTICLE_COUNT = 12;
const SVG_H = 200;

function buildPath(fromX: number, toX: number, cy: number): string {
  const dx = toX - fromX;
  const dist = Math.abs(dx);
  const arcHeight = Math.min(SVG_H * 0.55, 40 + dist * 0.18);
  const cp1x = fromX;
  const cp1y = cy - arcHeight;
  const cp2x = toX;
  const cp2y = cy - arcHeight;
  return `M ${fromX} ${cy} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${toX} ${cy}`;
}

export function TransferAnimation({ recommendation, carCount, showWomenAlternative }: TransferAnimationProps) {
  if (!recommendation || carCount < 2) return null;

  const primaryRec = showWomenAlternative && recommendation.womenAlternative
    ? recommendation.womenAlternative
    : recommendation;

  const fromIdx = primaryRec.fromCarId - 1;
  const toIdx = primaryRec.toCarId - 1;
  if (fromIdx < 0 || fromIdx >= carCount || toIdx < 0 || toIdx >= carCount) return null;
  if (fromIdx === toIdx) return null;

  const totalW = carCount * CARD_W + (carCount - 1) * GAP;
  const cy = SVG_H - 36;
  const fromX = fromIdx * (CARD_W + GAP) + CARD_W / 2;
  const toX = toIdx * (CARD_W + GAP) + CARD_W / 2;
  const midX = (fromX + toX) / 2;

  const pathD = buildPath(fromX, toX, cy);
  const dist = Math.abs(toX - fromX);
  const dur = Math.max(1.4, Math.min(2.8, dist / 180));

  const dir = toX > fromX ? 1 : -1;
  const isWomen = primaryRec.isWomenPriority;
  const gradId = isWomen ? "womenTransferGrad" : "transferGrad";
  const sourceColor = isWomen ? "#EC4899" : "#EF4444";
  const trailColor = isWomen ? "#F472B6" : "#F97316";
  const targetColor = isWomen ? "#DB2777" : "#22C55E";

  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden" style={{ zIndex: 10 }}>
      <svg
        className="absolute top-0 left-0"
        width={totalW}
        height={SVG_H}
        viewBox={`0 0 ${totalW} ${SVG_H}`}
        style={{ overflow: "visible" }}
      >
        <defs>
          <linearGradient id="transferGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#EF4444" />
            <stop offset="40%" stopColor="#F97316" />
            <stop offset="100%" stopColor="#22C55E" />
          </linearGradient>
          <linearGradient id="womenTransferGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#EC4899" />
            <stop offset="40%" stopColor="#F472B6" />
            <stop offset="100%" stopColor="#DB2777" />
          </linearGradient>
          <filter id="particleGlow">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <filter id="softGlow">
            <feGaussianBlur stdDeviation="6" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <radialGradient id="sourcePulse" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor={sourceColor} stopOpacity="0.35" />
            <stop offset="100%" stopColor={sourceColor} stopOpacity="0" />
          </radialGradient>
          <radialGradient id="targetPulse" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor={targetColor} stopOpacity="0.35" />
            <stop offset="100%" stopColor={targetColor} stopOpacity="0" />
          </radialGradient>
        </defs>

        <path
          d={pathD}
          fill="none"
          stroke={`url(#${gradId})`}
          strokeWidth="1.5"
          strokeDasharray="6 6"
          opacity="0.25"
        >
          <animate attributeName="stroke-dashoffset" values={`0;${-24}`} dur="1s" repeatCount="indefinite" />
        </path>

        <circle r="10" fill={trailColor} opacity="0.18" filter="url(#softGlow)">
          <animateMotion dur={`${dur}s`} repeatCount="indefinite" path={pathD} rotate="auto" />
          <animate attributeName="r" values="8;14;8" dur={`${dur * 0.6}s`} repeatCount="indefinite" />
          <animate attributeName="opacity" values="0.18;0.06;0.18" dur={`${dur * 0.6}s`} repeatCount="indefinite" />
        </circle>

        {Array.from({ length: PARTICLE_COUNT }).map((_, i) => {
          const t = i / PARTICLE_COUNT;
          const delay = t * dur;
          const size = 2 + (1 - t) * 4;
          const opacity = 0.3 + (1 - t) * 0.7;
          let color: string;
          if (isWomen) {
            color = t < 0.3 ? "#EC4899" : t < 0.7 ? "#F472B6" : "#DB2777";
          } else {
            color = t < 0.3 ? "#EF4444" : t < 0.7 ? "#F97316" : "#22C55E";
          }
          return (
            <g key={i} filter="url(#particleGlow)">
              <circle r={size} fill={color} opacity={opacity}>
                <animateMotion dur={`${dur}s`} begin={`${delay}s`} repeatCount="indefinite" path={pathD} rotate="auto" />
                <animate attributeName="r" values={`${size * 0.6};${size * 1.3};${size * 0.6}`} dur={`${dur * 0.5}s`} begin={`${delay}s`} repeatCount="indefinite" />
                <animate attributeName="opacity" values={`${opacity};${opacity * 0.3};${opacity}`} dur={`${dur * 0.5}s`} begin={`${delay}s`} repeatCount="indefinite" />
              </circle>
              <circle r={size * 2.5} fill={color} opacity={opacity * 0.12}>
                <animateMotion dur={`${dur}s`} begin={`${delay}s`} repeatCount="indefinite" path={pathD} rotate="auto" />
                <animate attributeName="r" values={`${size * 1.8};${size * 3};${size * 1.8}`} dur={`${dur * 0.5}s`} begin={`${delay}s}`} repeatCount="indefinite" />
              </circle>
            </g>
          );
        })}

        {/* source marker */}
        <circle cx={fromX} cy={cy} r="30" fill="url(#sourcePulse)">
          <animate attributeName="r" values="22;38;22" dur="2s" repeatCount="indefinite" />
        </circle>
        <circle cx={fromX} cy={cy} r="5" fill={sourceColor} opacity="0.9">
          <animate attributeName="r" values="4;6;4" dur="1.2s" repeatCount="indefinite" />
        </circle>

        {/* target marker */}
        <circle cx={toX} cy={cy} r="30" fill="url(#targetPulse)">
          <animate attributeName="r" values="22;38;22" dur="2s" begin="0.8s" repeatCount="indefinite" />
        </circle>
        <circle cx={toX} cy={cy} r="5" fill={targetColor} opacity="0.9">
          <animate attributeName="r" values="4;6;4" dur="1.2s" begin="0.8s" repeatCount="indefinite" />
        </circle>

        {/* arrow at target */}
        <polygon
          points={`${toX + dir * 4},${cy - 6} ${toX + dir * 14},${cy} ${toX + dir * 4},${cy + 6}`}
          fill={targetColor}
          opacity="0.85"
        >
          <animate attributeName="opacity" values="0.85;0.4;0.85" dur="1.2s" repeatCount="indefinite" />
        </polygon>

        {/* label */}
        <rect x={midX - 58} y={cy - 62} width="116" height="24" rx="12" fill="white" opacity="0.92" filter="url(#particleGlow)" />
        <rect x={midX - 58} y={cy - 62} width="116" height="24" rx="12" fill="none" stroke={`url(#${gradId})`} strokeWidth="1" opacity="0.3" />
        <text x={midX} y={cy - 47} textAnchor="middle" fill="#1E293B" fontSize="11" fontWeight="700" fontFamily="system-ui, -apple-system, sans-serif">
          {primaryRec.passengersToMove
            ? `~${primaryRec.passengersToMove} penumpang`
            : "Pindahkan penumpang"}
        </text>

        <text x={fromX} y={cy + 24} textAnchor="middle" fill={sourceColor} fontSize="10" fontWeight="600" fontFamily="system-ui, sans-serif" opacity="0.8">
          Gerbong {primaryRec.fromCarId}
        </text>
        <text x={toX} y={cy + 24} textAnchor="middle" fill={targetColor} fontSize="10" fontWeight="600" fontFamily="system-ui, sans-serif" opacity="0.8">
          {isWomen ? "Gerbong Wanita " : ""}Gerbong {primaryRec.toCarId}
        </text>
      </svg>
    </div>
  );
}
