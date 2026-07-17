export interface CarSpatialOccupancy {
  carId: number;
  occupancyRatio: number;
  freeSpaceRatio: number;
  densityIndicator: "GREEN" | "YELLOW" | "RED";
  spatialOccupancyScore: number;
  cameraStatus?: string;
  cameraId?: string;
  riskScore?: number;
  prediction?: {
    trend: string;
    predictedOccupancyRatio: number;
    confidence: number;
    horizonMinutes: number;
  } | null;
}

export interface OccupancyData {
  trainId: string;
  station: string;
  timestamp: string;
  cars: CarSpatialOccupancy[];
}

export interface TrainInfo {
  id: string;
  formation: string;
  totalCars: number;
  avgOccupancyRatio: number;
  greenCars: number;
  yellowCars: number;
  redCars: number;
}

export interface SystemState {
  timestamp: string;
  station: {
    id: string;
    name: string;
  };
  train: TrainInfo;
  occupancy: {
    avgOccupancyRatio: number;
    greenCars: number;
    yellowCars: number;
    redCars: number;
  };
  warning: Warning | null;
  system: {
    trains: number;
    activeWarnings: number;
    totalDecisions: number;
    activeCameras: number;
    uptimeSeconds: number;
  };
}

export interface Warning {
  id: string;
  trainId: string;
  carId: number;
  warningType: string;
  severity: string;
  message: string;
  timestamp: string;
  isActive?: boolean;
}

export interface RecommendationItem {
  action: string;
  fromCarId: number;
  toCarId: number;
  confidence: number;
  reason: string;
  priority: number;
  label: string;
  isWomenPriority: boolean;
  score: number;
}

export interface Recommendation {
  fromCarId: number;
  fromOccupancy: number;
  congestionAvg: number;
  highestOccupancy: number;
  recommendedCars: number[];
  recommendations: RecommendationItem[];
  timestamp: string;
}

export interface TimelineEvent {
  id: string;
  timestamp: string;
  type: string;
  message: string;
  severity: "info" | "warning" | "success";
}

export interface SystemHealthItem {
  label: string;
  status: "ok" | "warning" | "error";
  value: string;
  icon: string;
}

export interface HistoryRecord {
  timestamp: string;
  carId: number;
  occupancyRatio: number;
  densityIndicator: string;
}

export interface HistorySummary {
  averageOccupancy: number;
  peakOccupancy: number;
  peakTime: string;
  totalRecords: number;
}

export interface PipelineResult {
  carId: string;
  occupancyRatio: number;
  freeSpaceRatio: number;
  densityIndicator: "GREEN" | "YELLOW" | "RED";
  spatialOccupancyScore: number;
  recommendedTarget: number | null;
  doorAction: string;
  announcement: string | null;
  calesScore: number;
  healthIndex: number;
  damageMultiplier: number;
  inspectionPriority: number;
  recommendedAction: string;
  timestamp: string;
}
