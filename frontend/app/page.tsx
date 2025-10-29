/**
 * Home page displaying greeting.
 */
"use client";

import React from "react";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
          Hello Agent Bletchley
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-400">
          Agentic web research system for investment due diligence
        </p>
      </div>
    </main>
  );
}

