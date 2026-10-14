"use client";

import React from "react";

interface HeaderProps {
  language: "en" | "ml";
  setLanguage: (lang: "en" | "ml") => void;
  connectionState: string;
}

export const Header: React.FC<HeaderProps> = ({ language, setLanguage, connectionState }) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200 bg-white/90 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
        {/* Brand & Dealership Identity */}
        <div className="flex items-center space-x-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-blue-700 to-indigo-600 shadow-md shadow-blue-500/20">
            <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xl font-bold tracking-tight text-slate-900">Agent</span>
              <span className="rounded-md bg-blue-50 px-2 py-0.5 text-xs font-semibold text-blue-700 border border-blue-200">
                Voice AI
              </span>
            </div>
            <p className="text-xs font-medium text-slate-500">
              {language === "ml" ? "അപെക്സ് മോട്ടോഴ്സ് കേരള (അംഗീകൃത ഡീലർ)" : "Apex Motors Kerala • Authorized Dealership"}
            </p>
          </div>
        </div>

        {/* Center / Nav Status */}
        <div className="hidden md:flex items-center space-x-6 text-sm font-medium text-slate-600">
          <span className="flex items-center text-blue-600 font-semibold cursor-pointer">
            <span className="mr-1.5 flex h-2 w-2 rounded-full bg-blue-600"></span>
            {language === "ml" ? "വോയ്‌സ് അസിസ്റ്റന്റ്" : "Voice Assistant"}
          </span>
          <span className="text-slate-400 hover:text-slate-700 cursor-pointer transition">
            {language === "ml" ? "വാഹനങ്ങൾ" : "Vehicles"}
          </span>
          <span className="text-slate-400 hover:text-slate-700 cursor-pointer transition">
            {language === "ml" ? "ഫിനാൻസ് EMI" : "Finance & EMI"}
          </span>
          <span className="text-slate-400 hover:text-slate-700 cursor-pointer transition">
            {language === "ml" ? "ഡീലർഷിപ്പ്" : "Dealership CRM"}
          </span>
        </div>

        {/* Right: Language Selector & Connection Badge */}
        <div className="flex items-center space-x-3">
          {/* Connection state pill */}
          <div className="flex items-center space-x-1.5 rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700 border border-slate-200">
            <span
              className={`h-2 w-2 rounded-full ${
                connectionState === "listening" || connectionState === "speaking"
                  ? "bg-emerald-500 animate-pulse"
                  : connectionState === "processing"
                  ? "bg-amber-500 animate-spin"
                  : connectionState === "connecting"
                  ? "bg-blue-500 animate-ping"
                  : "bg-slate-400"
              }`}
            />
            <span className="capitalize">{connectionState}</span>
          </div>

          {/* Language Switcher */}
          <div className="flex items-center rounded-lg border border-slate-200 bg-slate-50 p-0.5">
            <button
              onClick={() => setLanguage("en")}
              className={`rounded-md px-2.5 py-1 text-xs font-semibold transition ${
                language === "en" ? "bg-white text-blue-700 shadow-sm" : "text-slate-600 hover:text-slate-900"
              }`}
            >
              EN
            </button>
            <button
              onClick={() => setLanguage("ml")}
              className={`rounded-md px-2.5 py-1 text-xs font-semibold transition ${
                language === "ml" ? "bg-white text-blue-700 shadow-sm" : "text-slate-600 hover:text-slate-900"
              }`}
            >
              മലയാളം
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
