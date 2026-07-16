"use client";

import { Recommendation } from "@/types";

interface TransferAnimationProps {
  recommendation: Recommendation | null;
  carCount: number;
}

const PARTICLE_COUNT = 8;

export function TransferAnimation({ recommendation, carCount }: TransferAnimationProps) {
  if (!recommendation) return null;

  const fromIdx = recommendation.fromCarId - 1;
  const toIdx = recommendation.toCarId - 1;
  if (fromIdx < 0 || fromIdx >= carCount || toIdx < 0 || toIdx >= carCount) return null;

  const gap = 12;
  const cardW = 112;
  const svgH = 180;
  const fromX = fromIdx * (cardW + gap) + cardW / 2;
  const toX = toIdx * (cardW + gap) + cardW / 2;
  const midX = (fromX + toX) / 2;
  const totalW = carCount * cardW + (carCount - 1) * gap;
  const arcY = svgH * 0.15;
  const cy = svgH * 0.65;

  const pathD = `M ${fromX} ${cy} C ${fromX} ${arcY}, ${toX} ${arcY}, ${toX} ${cy}`;
  const dur = 2.0;

  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden" style={{ zIndex: 10 }}>
      <svg
        className="absolute top-0 left-0"
        width={totalW}
        height={svgH}
        viewBox={`0 0 ${totalW} ${svgH}`}
        style={{ overflow: "visible" }}
      >
        <defs>
          <linearGradient id="tg" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#ED242B" />
            <stop offset="50%" stopColor="#EC6C25" />
            <stop offset="100%" stopColor="#16A34A" />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <path
          d={pathD}
          fill="none"
          stroke="url(#tg)"
          strokeWidth="2"
          strokeDasharray="8 5"
          opacity="0.4"
        >
          <animate attributeName="stroke-dashoffset" values="0;-26" dur="1.2s" repeatCount="indefinite" />
        </path>

        {Array.from({ length: PARTICLE_COUNT }).map((_, i) => {
          const delay = (i / PARTICLE_COUNT) * dur;
          return (
            <g key={i} filter="url(#glow)">
              <circle r="4" fill="#EC6C25" opacity="0.95">
                <animateMotion
                  dur={`${dur}s`}
                  begin={`${delay}s`}
                  repeatCount="indefinite"
                  path={pathD}
                />
                <animate attributeName="r" values="2.5;5;2.5" dur={`${dur}s`} begin={`${delay}s`} repeatCount="indefinite" />
              </circle>
              <circle r="8" fill="#EC6C25" opacity="0.12">
                <animateMotion
                  dur={`${dur}s`}
                  begin={`${delay}s`}
                  repeatCount="indefinite"
                  path={pathD}
                />
                <animate attributeName="r" values="6;12;6" dur={`${dur}s`} begin={`${delay}s`} repeatCount="indefinite" />
                <animate attributeName="opacity" values="0.12;0.03;0.12" dur={`${dur}s`} begin={`${delay}s`} repeatCount="indefinite" />
              </circle>
            </g>
          );
        })}

        <circle cx={fromX} cy={cy} r="20" fill="#ED242B" opacity="0.08">
          <animate attributeName="r" values="16;24;16" dur="2s" repeatCount="indefinite" />
          <animate attributeName="opacity" values="0.08;0.02;0.08" dur="2s" repeatCount="indefinite" />
        </circle>
        <circle cx={toX} cy={cy} r="20" fill="#16A34A" opacity="0.08">
          <animate attributeName="r" values="16;24;16" dur="2s" begin="1s" repeatCount="indefinite" />
          <animate attributeName="opacity" values="0.08;0.02;0.08" dur="2s" begin="1s" repeatCount="indefinite" />
        </circle>

        <rect
          x={midX - 52}
          y={arcY - 2}
          width="104"
          height="20"
          rx="10"
          fill="white"
          opacity="0.85"
        />
        <text
          x={midX}
          y={arcY + 13}
          textAnchor="middle"
          fill="#2D2A70"
          fontSize="11"
          fontWeight="700"
          fontFamily="system-ui, sans-serif"
        >
          {recommendation.passengersToMove
            ? `~${recommendation.passengersToMove} penumpang`
            : "Pindahkan penumpang"}
        </text>
      </svg>
    </div>
  );
}
