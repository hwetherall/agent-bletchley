/**
 * Research dashboard page for viewing a specific research job.
 */
"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import type { ResearchJob } from "@/types/research";
import ProgressBar from "@/components/ProgressBar";
import IterationCard from "@/components/IterationCard";
import SourcePanel from "@/components/SourcePanel";
import OutputViewer from "@/components/OutputViewer";
import { useWebSocket } from "@/lib/websocket";

export default function ResearchJobPage() {
  const params = useParams();
  const jobId = params.jobId as string;
  const [job, setJob] = useState<ResearchJob | null>(null);
  const [loading, setLoading] = useState(true);

  // TODO: Fetch job data from API
  useEffect(() => {
    // TODO: Implement API call to fetch job
    setLoading(false);
  }, [jobId]);

  // WebSocket connection for real-time updates
  const { isConnected, lastMessage } = useWebSocket({
    jobId,
    onMessage: (message) => {
      // TODO: Update job state based on WebSocket messages
      console.log("WebSocket message:", message);
    },
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-500 dark:text-gray-400">Loading...</div>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-500 dark:text-gray-400">Job not found</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Research: {job.query}
        </h1>
        <div className="flex items-center gap-4">
          <span
            className={`px-3 py-1 rounded-full text-sm font-medium ${
              isConnected
                ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                : "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200"
            }`}
          >
            {isConnected ? "Connected" : "Disconnected"}
          </span>
        </div>
      </div>

      <div className="mb-6">
        <ProgressBar progress={job.progress} status={job.status} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Research Iterations
          </h2>
          <div className="space-y-3">
            {job.iterations.map((iteration) => (
              <IterationCard key={iteration.id} iteration={iteration} />
            ))}
          </div>
        </div>

        <div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Sources
          </h2>
          <SourcePanel sources={job.sources} />
        </div>
      </div>

      {job.report && (
        <div className="mt-6">
          <OutputViewer report={job.report} />
        </div>
      )}

      {job.error && (
        <div className="mt-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-red-800 dark:text-red-200">{job.error}</p>
        </div>
      )}
    </div>
  );
}

