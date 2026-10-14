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
  // Normalize audio amplitude for 16 bars
  const bars = Array.from({ length: 16 }).map((_, idx) => {
    // Generate realistic multi-band frequency spread based on live audioLevel
    const phase = Math.sin((idx / 16) * Math.PI);
    const height = Math.max(12, Math.min(100, (audioLevel * 140 * phase) + (state === "speaking" ? 30 * phase : 8)));
    return Math.round(height);
  });

  const getStateDescription = () => {
    switch (state) {
      case "idle":
        return language === "ml"
          ? "സംസാരിക്കാൻ മൈക്രോഫോൺ ബട്ടൺ അമർത്തുക"
          : "Tap the microphone or press space to start voice conversation";
      case "requesting_mic":
        return language === "ml"
          ? "മൈക്രോഫോൺ അനുമതി പരിശോധിക്കുന്നു..."
          : "Requesting microphone permissions...";
      case "connecting":
        return language === "ml"
          ? "Apex വോയ്‌സ് സെർവറുമായി ബന്ധിപ്പിക്കുന്നു..."
          : "Connecting to Apex Voice Engine...";
      case "listening":
        return language === "ml"
          ? "നിങ്ങൾ സംസാരിക്കുന്നത് ശ്രദ്ധിക്കുന്നു..."
          : "Listening to your voice... Speak naturally";
      case "processing":
        return language === "ml"
          ? "വിവരങ്ങൾ പരിശോധിക്കുന്നു..."
          : "Consulting automotive catalog and reasoning...";
      case "speaking":
        return language === "ml"
          ? "അസിസ്റ്റന്റ് സംസാരിക്കുന്നു (തടസ്സപ്പെടുത്താൻ ക്ലിക്ക് ചെയ്യുക)"
          : "Agent is speaking • Click interrupt to speak";
      case "interrupted":
        return language === "ml"
          ? "തടസ്സപ്പെടുത്തി, സംസാരിക്കാൻ തയ്യാറാണ്..."
          : "Interrupted • Ready for your input";
      case "failed":
        return language === "ml"
          ? "ബന്ധപ്പെടാൻ സാധിച്ചില്ല. ദയവായി വീണ്ടും ശ്രമിക്കുക"
          : "Voice connection failed. Please retry";
      case "ended":
        return language === "ml"
          ? "സംഭാഷണം അവസാനിച്ചു. വീണ്ടും ആരംഭിക്കാൻ ക്ലിക്ക് ചെയ്യുക"
          : "Conversation ended. Click to restart";
    }
  };

  return (
    <div className="flex flex-col items-center justify-center py-8">
      {/* Central Visual Orb & Rings */}
      <div className="relative flex items-center justify-center">
        {/* Pulsing outer aura rings for listening/speaking */}
        {(state === "listening" || state === "speaking") && (
          <>
            <div
              className={`absolute h-48 w-48 rounded-full opacity-20 blur-xl transition-all duration-300 ${
                state === "speaking" ? "bg-blue-500 scale-125" : "bg-cyan-400 scale-110"
              }`}
            />
            <div
              className={`absolute h-40 w-40 rounded-full border border-cyan-400/40 animate-ping opacity-30 ${
                state === "speaking" ? "border-blue-500" : "border-cyan-400"
              }`}
            />
          </>
        )}

        {/* Processing Spinner Ring */}
        {state === "processing" && (
          <div className="absolute h-36 w-36 rounded-full border-2 border-transparent border-t-blue-600 border-r-cyan-400 animate-spin" />
        )}

        {/* Main Mic Button Orb */}
        <button
          onClick={state === "speaking" ? onInterrupt : onToggleMic}
          aria-label={state === "listening" ? "Stop Listening" : "Start Voice Assistant"}
          className={`relative z-10 flex h-28 w-28 items-center justify-center rounded-full shadow-xl transition-all transform active:scale-95 ${
            state === "listening"
              ? "bg-gradient-to-tr from-cyan-500 to-blue-600 text-white shadow-cyan-500/30 ring-4 ring-cyan-200"
              : state === "speaking"
              ? "bg-gradient-to-tr from-blue-600 to-indigo-700 text-white shadow-blue-500/40 ring-4 ring-blue-200"
              : state === "processing"
              ? "bg-gradient-to-tr from-indigo-500 to-blue-500 text-white shadow-indigo-500/20"
              : state === "failed"
              ? "bg-rose-500 text-white shadow-rose-500/30"
              : "bg-slate-900 text-white hover:bg-slate-800 shadow-slate-900/20"
          }`}
        >
          {state === "listening" ? (
            <svg className="h-10 w-10 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
          ) : state === "speaking" ? (
            <svg className="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
            </svg>
          ) : state === "processing" ? (
            <svg className="h-8 w-8 animate-spin" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          ) : (
            <svg className="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
          )}
        </button>
      </div>

      {/* Waveform Visualization Bars */}
      <div className="mt-6 flex h-14 items-center justify-center space-x-1.5 px-4">
        {bars.map((height, i) => (
          <div
            key={i}
            style={{
              height: `${state === "listening" || state === "speaking" ? height : 6}%`,
              transition: "height 80ms ease-in-out",
            }}
            className={`w-1.5 rounded-full ${
              state === "speaking"
                ? "bg-gradient-to-t from-blue-600 to-cyan-400"
                : state === "listening"
                ? "bg-gradient-to-t from-cyan-500 to-emerald-400"
                : "bg-slate-200"
            }`}
          />
        ))}
      </div>

      {/* Status Label */}
      <div className="mt-4 flex flex-col items-center space-y-2 text-center">
        <span
          className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${
            state === "listening"
              ? "bg-cyan-50 text-cyan-700 border border-cyan-200"
              : state === "speaking"
              ? "bg-blue-50 text-blue-700 border border-blue-200"
              : state === "processing"
              ? "bg-indigo-50 text-indigo-700 border border-indigo-200"
              : state === "failed"
              ? "bg-rose-50 text-rose-700 border border-rose-200"
              : "bg-slate-100 text-slate-600 border border-slate-200"
          }`}
        >
          {state.toUpperCase()}
        </span>
        <p className="max-w-md text-sm font-medium text-slate-600">{getStateDescription()}</p>
      </div>

      {/* Interruption CTA when speaking */}
      {state === "speaking" && (
        <button
          onClick={onInterrupt}
          className="mt-3 flex items-center space-x-1.5 rounded-full border border-amber-300 bg-amber-50 px-4 py-1.5 text-xs font-semibold text-amber-800 shadow-sm hover:bg-amber-100 transition"
        >
          <span className="h-2 w-2 rounded-full bg-amber-500"></span>
          <span>{language === "ml" ? "സംസാരം തടസ്സപ്പെടുത്തുക (Interrupt)" : "Interrupt Assistant"}</span>
        </button>
      )}
    </div>
  );
};
