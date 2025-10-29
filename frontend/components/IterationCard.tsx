/**
 * Component for displaying a research iteration.
 */
import React from "react";
import type { ResearchIteration } from "@/types/research";

interface IterationCardProps {
  iteration: ResearchIteration;
}

export default function IterationCard({ iteration }: IterationCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4 shadow-sm">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
          Step {iteration.step}
        </span>
        <span className="text-xs text-gray-400 dark:text-gray-500">
          {new Date(iteration.timestamp).toLocaleTimeString()}
        </span>
      </div>
      <p className="text-sm text-gray-900 dark:text-gray-100">{iteration.action}</p>
      {/* TODO: Display iteration results if available */}
    </div>
  );
}

