"use client";

import React from "react";

interface AudioVisualizerProps {
  state: "idle" | "requesting_mic" | "connecting" | "listening" | "processing" | "speaking" | "interrupted" | "failed" | "ended";
  audioLevel: number; // 0 to 1
  language: "en" | "ml";
  onToggleMic: () => void;
  onInterrupt: () => void;
}

export const AudioVisualizer: React.FC<AudioVisualizerProps> = ({
  state,
  audioLevel,
  language,
  onToggleMic,
  onInterrupt,
}) => {
  // Generate 28 precision vertical waveform bars in white & blue styling
  const bars = Array.from({ length: 28 }).map((_, idx) => {
    const center = 14;
    const distance = Math.abs(idx - center);
    const weight = Math.max(0.15, 1 - distance / 15);
    const dynamicHeight = (audioLevel * 100 * weight) + (state === "speaking" ? 32 * weight : 6);
    return Math.max(6, Math.min(100, Math.round(dynamicHeight)));
  });

  const getStatusText = () => {
    switch (state) {
      case "idle":
        return language === "ml"
          ? "വോയ്‌സ് സംഭാഷണം ആരംഭിക്കാൻ മൈക്രോഫോൺ ക്ലിക്ക് ചെയ്യുക"
          : "Click microphone to start hands-free voice consultation";
      case "requesting_mic":
        return language === "ml"
          ? "മൈക്രോഫോൺ അനുമതി കാക്കുന്നു..."
          : "Requesting microphone hardware access...";
      case "connecting":
        return language === "ml"
          ? "വോയ്‌സ് എഞ്ചിനിലേക്ക് ബന്ധിപ്പിക്കുന്നു..."
          : "Connecting to low-latency voice engine...";
      case "listening":
        return language === "ml"
          ? "നിങ്ങൾ സംസാരിക്കുന്നത് ശ്രദ്ധിക്കുന്നു... സ്വാഭാവികമായി സംസാരിക്കുക"
          : "Listening... Speak naturally in English or Malayalam";
      case "processing":
        return language === "ml"
          ? "വിവരങ്ങൾ വിശകലനം ചെയ്യുന്നു..."
          : "Reasoning across agent tools...";
      case "speaking":
        return language === "ml"
          ? "ഏജന്റ് സംസാരിക്കുന്നു • തടസ്സപ്പെടുത്താൻ ക്ലിക്ക് ചെയ്യുക"
          : "Agent speaking • Click to interrupt or speak over";
      case "interrupted":
        return language === "ml"
          ? "തടസ്സപ്പെടുത്തി • സംസാരിക്കാം"
          : "Interrupted • Ready for next input";
      case "failed":
        return language === "ml"
          ? "ബന്ധപ്പെടാൻ സാധിച്ചില്ല. വീണ്ടും ശ്രമിക്കുക"
          : "Voice connection failed. Please retry";
      case "ended":
        return language === "ml"
          ? "സെഷൻ പൂർത്തിയായി"
          : "Session concluded";
    }
  };

  const isActive = state === "listening" || state === "speaking" || state === "processing";
  const displayInputLevel = Math.min(99, Math.max(12, Math.round(audioLevel * 100) || (state === "listening" ? 23 : 0)));

  return (
    <div className="flex flex-col items-center justify-center py-4">
      {/* Top Status Line in White and Blue theme */}
      <div className="mb-6 flex items-center space-x-2 text-xs font-medium text-slate-600">
        <span
          className={`h-2 w-2 rounded-full ${
            state === "listening"
              ? "bg-blue-600 animate-pulse"
              : state === "speaking"
              ? "bg-blue-600 animate-pulse"
              : state === "processing"
              ? "bg-amber-500 animate-spin"
              : "bg-slate-300"
          }`}
        />
        <span className="font-semibold text-blue-900 capitalize">
          {state === "speaking"
            ? language === "ml" ? "സംസാരിക്കുന്നു" : "Speaking"
            : state === "listening"
            ? language === "ml" ? "ശ്രദ്ധിക്കുന്നു" : "Listening"
            : state === "processing"
            ? language === "ml" ? "വിശകലനം" : "Thinking"
            : language === "ml" ? "തയ്യാറാണ്" : "Standby"}
        </span>
        <span className="text-slate-300">•</span>
        <span className="text-slate-500 font-normal">
          Input Level: {displayInputLevel}%
        </span>
      </div>

      {/* Center Microphone Button with Sapphire Blue Halo */}
      <div className="relative flex items-center justify-center">
        {/* Outer soft blue concentric ring */}
        <div
          className={`flex h-28 w-28 items-center justify-center rounded-full border border-blue-200 bg-blue-50/60 transition-all duration-300 ${
            isActive ? "scale-105" : "scale-100"
          }`}
        >
          {/* Inner Cobalt Blue Button */}
          <button
            onClick={state === "speaking" ? onInterrupt : onToggleMic}
            aria-label={
              state === "listening"
                ? "Stop listening"
                : state === "speaking"
                ? "Interrupt agent"
                : "Start voice conversation"
            }
            className={`flex h-20 w-20 items-center justify-center rounded-full text-white shadow-md shadow-blue-500/20 transition-all active:scale-95 ${
              state === "speaking"
                ? "bg-blue-700 hover:bg-blue-800 ring-4 ring-blue-100"
                : state === "processing"
                ? "bg-blue-600 hover:bg-blue-700 animate-pulse"
                : "bg-blue-600 hover:bg-blue-700 ring-4 ring-blue-50"
            }`}
          >
            {state === "processing" ? (
              <svg
                className="h-7 w-7 animate-spin text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            ) : state === "speaking" ? (
              <svg
                className="h-7 w-7 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg
                className="h-7 w-7 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                />
              </svg>
            )}
          </button>
        </div>
      </div>

      {/* Sapphire Blue Waveform */}
      <div className="mt-7 flex h-10 items-center justify-center space-x-1 px-4">
        {bars.map((height, i) => (
          <div
            key={i}
            style={{
              height: `${isActive ? height : 6}%`,
              transition: "height 75ms ease-in-out",
            }}
            className={`w-1 rounded-full ${
              isActive ? "bg-blue-600" : "bg-blue-200"
            }`}
          />
        ))}
      </div>

      {/* Subtitle guidance text */}
      <p className="mt-4 text-center text-xs text-slate-500 font-normal">
        {getStatusText()}
      </p>
    </div>
  );
};
