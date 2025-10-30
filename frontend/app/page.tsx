"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import type { ResearchJob, ResearchJobStatus } from "@/types/research";
import { createResearchJob, listResearchJobs } from "@/lib/api";

const EXAMPLE_QUERIES = [
  "Analyze the competitive landscape for quantum computing startups",
  "What are the key risks and opportunities in African fintech?",
  "Deep dive on AI regulation in healthcare",
  "Evaluate market opportunity for eVTOL aircraft",
  "Research semiconductor supply chain vulnerabilities",
  "Climate tech investment trends in 2025",
];

function formatRelativeTime(timestamp: string): string {
  const now = new Date();
  const time = new Date(timestamp);
  const diffInSeconds = Math.floor((now.getTime() - time.getTime()) / 1000);

  if (diffInSeconds < 60) {
    return "just now";
  }

  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) {
    return `${diffInMinutes} minute${diffInMinutes > 1 ? "s" : ""} ago`;
  }

  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) {
    return `${diffInHours} hour${diffInHours > 1 ? "s" : ""} ago`;
  }

  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 7) {
    return `${diffInDays} day${diffInDays > 1 ? "s" : ""} ago`;
  }

  const diffInWeeks = Math.floor(diffInDays / 7);
  if (diffInWeeks < 4) {
    return `${diffInWeeks} week${diffInWeeks > 1 ? "s" : ""} ago`;
  }

  const diffInMonths = Math.floor(diffInDays / 30);
  return `${diffInMonths} month${diffInMonths > 1 ? "s" : ""} ago`;
}

function getStatusBadgeClass(status: ResearchJobStatus): string {
  switch (status) {
    case "pending":
      return "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200";
    case "running":
      return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200";
    case "completed":
      return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
    case "failed":
      return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200";
    case "cancelled":
      return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200";
    default:
      return "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200";
  }
}

export default function Home() {
  const router = useRouter();
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [query, setQuery] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recentJobs, setRecentJobs] = useState<ResearchJob[]>([]);
  const [loading, setLoading] = useState(true);

  // Auto-focus textarea on mount
  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  // Fetch recent jobs on mount
  useEffect(() => {
    const fetchJobs = async () => {
      try {
        setLoading(true);
        const jobs = await listResearchJobs(10);
        setRecentJobs(jobs);
      } catch (err) {
        console.error("Failed to fetch recent jobs:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
  }, []);

  // Clear error when user types
  useEffect(() => {
    if (error && query.length > 0) {
      setError(null);
    }
  }, [query, error]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (query.length < 20) {
      setError("Query must be at least 20 characters");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const job = await createResearchJob({ query });
      router.push(`/research/${job.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start research");
      setIsSubmitting(false);
    }
  };

  const handleExampleClick = (exampleQuery: string) => {
    setQuery(exampleQuery);
    setError(null);
    textareaRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      if (query.length >= 20 && !isSubmitting) {
        handleSubmit(e);
      }
    }
  };

  const truncatedQuery = (text: string) => {
    return text.length > 100 ? text.substring(0, 100) + "..." : text;
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="container mx-auto px-4 py-12 max-w-6xl">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-purple-600 via-purple-500 to-blue-600 bg-clip-text text-transparent">
            Agent Bletchley
          </h1>
          <h2 className="text-2xl font-semibold text-gray-700 dark:text-gray-300 mb-3">
            Autonomous Investment Research Powered by AI
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Deep research in minutes, not hours. Powered by Tongyi DeepResearch.
          </p>
        </div>

        {/* Research Query Form */}
        <div className="mb-12">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <textarea
                ref={textareaRef}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={5}
                placeholder="Enter your research query here... e.g., 'Analyze the competitive landscape for quantum computing startups'"
                className="w-full px-4 py-3 text-lg border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 resize-none transition-all duration-200"
              />
              <div className="mt-2 flex items-center justify-between">
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {query.length < 20 ? (
                    <span className="text-orange-600 dark:text-orange-400">
                      Minimum 20 characters ({query.length}/20)
                    </span>
                  ) : (
                    <span className="text-green-600 dark:text-green-400">
                      {query.length} characters
                    </span>
                  )}
                </p>
                <p className="text-xs text-gray-400 dark:text-gray-500">
                  Press Cmd/Ctrl+Enter to submit
                </p>
              </div>
            </div>

            {error && (
              <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                <p className="text-red-800 dark:text-red-200 text-sm">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={query.length < 20 || isSubmitting}
              className="w-full py-4 px-6 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <svg
                    className="animate-spin h-5 w-5 text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  <span>Researching...</span>
                </>
              ) : (
                <>
                  <span>Start Research</span>
                  <span>→</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Example Queries */}
        <div className="mb-12">
          <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-4">
            Example Queries
          </h3>
          <div className="flex flex-wrap gap-3">
            {EXAMPLE_QUERIES.map((exampleQuery, index) => (
              <button
                key={index}
                onClick={() => handleExampleClick(exampleQuery)}
                className="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-full text-sm text-gray-700 dark:text-gray-300 hover:bg-purple-50 dark:hover:bg-purple-900/20 hover:border-purple-300 dark:hover:border-purple-700 hover:text-purple-700 dark:hover:text-purple-400 transition-all duration-200 cursor-pointer"
              >
                {exampleQuery}
              </button>
            ))}
          </div>
        </div>

        {/* Recent Research Section */}
        <div>
          <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
            Recent Research
          </h3>

          {loading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="animate-pulse bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 h-24"
                ></div>
              ))}
            </div>
          ) : recentJobs.length === 0 ? (
            <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
              <p className="text-gray-500 dark:text-gray-400">
                No research jobs yet. Start your first investigation above!
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {recentJobs.map((job) => (
                <button
                  key={job.id}
                  onClick={() => router.push(`/research/${job.id}`)}
                  className="text-left p-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md transition-all duration-200 hover:border-purple-300 dark:hover:border-purple-700 cursor-pointer group"
                >
                  <div className="flex items-start justify-between mb-3">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusBadgeClass(
                        job.status
                      )}`}
                    >
                      {job.status}
                    </span>
                    <span className="text-xs text-gray-400 dark:text-gray-500">
                      {formatRelativeTime(job.created_at)}
                    </span>
                  </div>
                  <p className="text-gray-900 dark:text-white group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors duration-200">
                    {truncatedQuery(job.query)}
                  </p>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
