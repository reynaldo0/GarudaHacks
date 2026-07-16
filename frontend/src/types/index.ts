export interface CarOccupancy {
  carId: number;
  occupancyPct: number;
  status: string;
  passengers: number;
  capacity: number;
  prediction?: {
    trend: string;
    predictedOccupancy: number;
    confidence: number;
  } | null;
  cameraStatus?: string;
  recommendation?: {
    action: string;
    confidence: number;
  } | null;
}

export interface TrainState {
  trainId: string;
  formation: string;
  totalCars: number;
  cars: CarOccupancy[];
  timestamp: string;
}

export interface Warning {
  id: string;
  trainId: string;
  carId: number;
  warningType: string;
  severity: string;
  message: string;
  timestamp: string;
  isActive: boolean;
}

export interface Recommendation {
  action: string;
  fromCarId: number;
  toCarId: number;
  confidence: number;
  reason: string;
}

export interface SystemState {
  timestamp: string;
  station: {
    id: string;
    name: string;
  };
  train: {
    id: string;
    formation: string;
    totalPassengers: number;
    totalCapacity: number;
    percentage: number;
    status: string;
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

export interface OccupancyCarResponse {
  carId: number;
  occupancyPct: number;
  status: string;
  passengers: number;
  capacity: number;
  prediction?: {
    trend: string;
    predictedOccupancy: number;
    confidence: number;
    horizonMinutes?: number;
  } | null;
  cameraStatus?: string;
  cameraId?: string;
  riskScore?: number;
  recommendation?: Record<string, unknown> | null;
}
