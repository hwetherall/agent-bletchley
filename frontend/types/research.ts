/**
 * TypeScript types for research jobs and related data structures.
 */

export enum ResearchJobStatus {
  PENDING = "pending",
  RUNNING = "running",
  COMPLETED = "completed",
  FAILED = "failed",
  CANCELLED = "cancelled",
}

export interface ResearchJobCreate {
  query: string;
  context?: Record<string, unknown>;
}

export interface ResearchJob {
  id: string;
  query: string;
  status: ResearchJobStatus;
  progress: number;
  created_at: string;
  updated_at?: string;
  completed_at?: string;
  sources: Source[];
  iterations: ResearchIteration[];
  report?: string;
  error?: string;
}

export interface Source {
  url: string;
  title: string;
  snippet?: string;
  fetched_at?: string;
  content?: string;
}

export interface ResearchIteration {
  id: string;
  step: number;
  action: string;
  timestamp: string;
  results?: unknown;
}

export interface WebSocketMessage {
  type: "status" | "progress" | "iteration" | "source" | "report" | "error";
  job_id: string;
  data: unknown;
}

