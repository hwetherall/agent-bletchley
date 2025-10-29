/**
 * Component for displaying research sources.
 */
import React from "react";
import type { Source } from "@/types/research";

interface SourcePanelProps {
  sources: Source[];
}

export default function SourcePanel({ sources }: SourcePanelProps) {
  if (sources.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500 dark:text-gray-400">
        No sources found yet.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {sources.map((source, index) => (
        <div
          key={index}
          className="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4 hover:shadow-md transition-shadow"
        >
          <a
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-medium text-blue-600 dark:text-blue-400 hover:underline block mb-1"
          >
            {source.title}
          </a>
          {source.snippet && (
            <p className="text-xs text-gray-600 dark:text-gray-300 line-clamp-2">
              {source.snippet}
            </p>
          )}
          {source.fetched_at && (
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-2">
              Fetched: {new Date(source.fetched_at).toLocaleString()}
            </p>
          )}
        </div>
      ))}
    </div>
  );
}

