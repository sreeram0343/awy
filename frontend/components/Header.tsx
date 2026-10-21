"use client";

import React, { useState } from "react";

export type NavTab = "voice" | "chat" | "agents" | "memory" | "integrations";

interface HeaderProps {
  activeTab: NavTab;
  setActiveTab: (tab: NavTab) => void;
  language: "en" | "ml";
  setLanguage: (lang: "en" | "ml") => void;
  connectionState: string;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  setActiveTab,
  language,
  setLanguage,
  connectionState,
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [langDropdownOpen, setLangDropdownOpen] = useState(false);

  const navItems: { id: NavTab; labelEn: string; labelMl: string }[] = [
    { id: "voice", labelEn: "Voice Assistant", labelMl: "വോയ്‌സ് അസിസ്റ്റന്റ്" },
    { id: "chat", labelEn: "Chat", labelMl: "ചാറ്റ്" },
    { id: "agents", labelEn: "Agents", labelMl: "ഏജന്റുകൾ" },
    { id: "memory", labelEn: "Memory", labelMl: "മെമ്മറി" },
    { id: "integrations", labelEn: "Integrations", labelMl: "ഇന്റഗ്രേഷൻസ്" },
  ];

  const isConnected = connectionState === "listening" || connectionState === "speaking";

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-200/80 bg-white/95 backdrop-blur-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        {/* Left: AWY Branding */}
        <div
          className="flex items-center space-x-3 cursor-pointer select-none"
          onClick={() => setActiveTab("voice")}
        >
          {/* Geometric delta mark in vibrant blue */}
          <div className="flex h-8 w-8 items-center justify-center">
            <svg
              className="h-6 w-6 text-blue-600"
              viewBox="0 0 24 24"
              fill="currentColor"
            >
              <path d="M12 2.5a2 2 0 0 0-1.732 1l-7.794 13.5A2 2 0 0 0 4.206 20h15.588a2 2 0 0 0 1.732-3L13.732 3.5A2 2 0 0 0 12 2.5Zm0 3.866 5.88 10.184H6.12L12 6.366Z" />
            </svg>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-base font-bold tracking-tight text-slate-900">
                AWY
              </span>
              <span className="text-slate-300 font-light">/</span>
              <span className="text-xs font-semibold text-blue-600">
                Agent With You
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-normal">
              Autonomous Multilingual AI Platform
            </p>
          </div>
        </div>

        {/* Center: Navigation Tabs in white and blue styling */}
        <nav className="hidden md:flex items-center space-x-1 rounded-lg border border-slate-200/80 bg-slate-50/80 p-1">
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`rounded-md px-3.5 py-1.5 text-xs font-medium transition-all ${
                  isActive
                    ? "bg-white text-blue-600 shadow-xs border border-blue-200/90 font-semibold"
                    : "text-slate-600 hover:text-blue-600 hover:bg-white/60"
                }`}
              >
                {language === "ml" ? item.labelMl : item.labelEn}
              </button>
            );
          })}
        </nav>

        {/* Right: Listening Status, Language Selector, User Avatar */}
        <div className="flex items-center space-x-3">
          {/* Listening Status Badge */}
          <div className="flex items-center space-x-1.5 rounded-full border border-blue-200/80 bg-blue-50/50 px-3 py-1 text-xs text-blue-700 shadow-xs">
            <span
              className={`h-2 w-2 rounded-full ${
                isConnected
                  ? "bg-blue-600 animate-pulse"
                  : connectionState === "processing"
                  ? "bg-amber-500 animate-spin"
                  : connectionState === "connecting"
                  ? "bg-blue-600 animate-ping"
                  : "bg-slate-300"
              }`}
            />
            <span className="text-[11px] font-semibold text-blue-800 capitalize">
              {connectionState === "idle" ? "Standby" : connectionState}
            </span>
          </div>

          {/* Language Selector Dropdown */}
          <div className="relative">
            <button
              onClick={() => setLangDropdownOpen(!langDropdownOpen)}
              className="flex items-center space-x-1 rounded-md border border-slate-200 bg-white px-2.5 py-1 text-xs font-medium text-slate-700 shadow-xs hover:border-blue-300 hover:text-blue-600 transition"
            >
              <span className="font-semibold text-blue-600">
                {language === "en" ? "EN" : "മലയാളം"}
              </span>
              <span className="text-slate-300">|</span>
              <span className="text-[11px] text-slate-500">
                {language === "en" ? "മലയാളം" : "EN"}
              </span>
              <svg
                className="h-3.5 w-3.5 text-slate-400 ml-0.5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {langDropdownOpen && (
              <div className="absolute right-0 mt-1 w-36 rounded-md border border-slate-200 bg-white py-1 shadow-lg text-xs z-50">
                <button
                  onClick={() => {
                    setLanguage("en");
                    setLangDropdownOpen(false);
                  }}
                  className={`w-full text-left px-3 py-1.5 hover:bg-blue-50/60 flex items-center justify-between ${
                    language === "en" ? "font-semibold text-blue-600" : "text-slate-600"
                  }`}
                >
                  <span>English (EN)</span>
                  {language === "en" && <span className="text-blue-600">✓</span>}
                </button>
                <button
                  onClick={() => {
                    setLanguage("ml");
                    setLangDropdownOpen(false);
                  }}
                  className={`w-full text-left px-3 py-1.5 hover:bg-blue-50/60 flex items-center justify-between ${
                    language === "ml" ? "font-semibold text-blue-600" : "text-slate-600"
                  }`}
                >
                  <span>മലയാളം (ML)</span>
                  {language === "ml" && <span className="text-blue-600">✓</span>}
                </button>
              </div>
            )}
          </div>

          {/* User Avatar */}
          <div className="flex h-8 w-8 items-center justify-center rounded-full border border-blue-200 bg-blue-50 text-xs font-bold text-blue-700 shadow-xs">
            R
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="flex h-8 w-8 items-center justify-center rounded-md border border-slate-200 bg-white text-slate-700 md:hidden hover:bg-slate-50"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? (
              <svg className="h-4 w-4 text-slate-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg className="h-4 w-4 text-slate-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            )}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="border-t border-slate-200 bg-white px-4 py-3 md:hidden">
          <div className="flex flex-col space-y-1">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => {
                  setActiveTab(item.id);
                  setMobileMenuOpen(false);
                }}
                className={`flex items-center justify-between rounded-md px-3 py-2 text-sm font-medium transition ${
                  activeTab === item.id
                    ? "bg-blue-50 text-blue-700 font-semibold"
                    : "text-slate-600 hover:bg-slate-50"
                }`}
              >
                <span>{language === "ml" ? item.labelMl : item.labelEn}</span>
                {activeTab === item.id && (
                  <span className="h-1.5 w-1.5 rounded-full bg-blue-600" />
                )}
              </button>
            ))}
          </div>
        </div>
      )}
    </header>
  );
};
