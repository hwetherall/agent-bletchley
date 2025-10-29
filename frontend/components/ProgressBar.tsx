/**
 * Animated progress bar component.
 */
"use client";

import React from "react";
import { motion } from "framer-motion";

interface ProgressBarProps {
  progress: number;
  status?: string;
}

export default function ProgressBar({ progress, status }: ProgressBarProps) {
  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
          {status || "Progress"}
        </span>
        <span className="text-sm text-gray-500 dark:text-gray-400">{Math.round(progress)}%</span>
      </div>
      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
        <motion.div
          className="h-full bg-blue-600 dark:bg-blue-500 rounded-full"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.3, ease: "easeOut" }}
        />
      </div>
    </div>
  );
}

