/**
 * Component for displaying the final research output.
 */
import React from "react";

interface OutputViewerProps {
  report: string;
}

export default function OutputViewer({ report }: OutputViewerProps) {
  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
        Research Report
      </h3>
      <div className="prose dark:prose-invert max-w-none">
        <div className="whitespace-pre-wrap text-gray-700 dark:text-gray-300">
          {report}
        </div>
      </div>
    </div>
  );
}

