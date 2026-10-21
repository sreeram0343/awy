"use client";

import React, { useState } from "react";

interface AgentSidebarProps {
  language: "en" | "ml";
  onSelectPrompt: (prompt: string) => void;
  onOpenAgentsTab: () => void;
  onOpenMemoryTab: () => void;
  onResumeSession: (title: string, query: string, response: string) => void;
}

export const AgentSidebar: React.FC<AgentSidebarProps> = ({
  language,
  onOpenAgentsTab,
  onOpenMemoryTab,
  onResumeSession,
}) => {
  const [searchHistory, setSearchHistory] = useState("");

  const recentConversations = [
    {
      id: "rc-1",
      icon: "research",
      title: "Multimodal LLM Benchmark Analysis",
      subtitle: "Dense visual token synthesis & comparison",
      time: "2 hours ago",
      query: "Research recent breakthroughs in multimodal reasoning models",
      response: "I have synthesized recent breakthroughs in multimodal reasoning models: frontier architectures combine dense visual token encoders with native cross-attention, demonstrating a 40% reduction in spatial hallucination benchmarks."
    },
    {
      id: "rc-2",
      icon: "finance",
      title: "Financial Scenario & Amortization",
      subtitle: "Reducing-balance schedule & tax breakdown",
      time: "4 hours ago",
      query: "Calculate monthly installment for ₹10 Lakh at 9.5% for 5 years",
      response: "Based on our deterministic reducing-balance engine, a ₹10,00,000 principal at 9.5% annual interest over 60 months yields exactly ₹21,002 per month with ₹2,60,119 total interest cost."
    },
    {
      id: "rc-3",
      icon: "plan",
      title: "Multi-Agent Planning & Execution",
      subtitle: "Q4 objective breakdown and milestone graph",
      time: "5 hours ago",
      query: "Generate a multi-step task execution plan for Q4 goals",
      response: "I have generated an autonomous multi-step execution plan: Phase 1 establishes benchmark evaluation metrics; Phase 2 orchestrates specialist agent workflows; Phase 3 activates continuous feedback optimization."
    },
    {
      id: "rc-4",
      icon: "briefing",
      title: "Daily Autonomous Intelligence Briefing",
      subtitle: "Executive summary and persisted key decisions",
      time: "1 day ago",
      query: "Summarize conversation history and persist key decisions",
      response: "Session summary compiled and persisted to agent vector memory: logged active intent constraints, execution parameters, and consensus recommendations for seamless future retrieval."
    }
  ];

  const filteredHistory = recentConversations.filter((c) =>
    c.title.toLowerCase().includes(searchHistory.toLowerCase()) ||
    c.subtitle.toLowerCase().includes(searchHistory.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Top Card: Agent Overview */}
      <div className="rounded-2xl border border-slate-200/90 bg-white p-6 shadow-xs">
        {/* Header with Title and 'View All' */}
        <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
          <h2 className="text-sm font-bold text-slate-900 tracking-tight">
            {language === "ml" ? "ഏജന്റ് വിവരങ്ങൾ" : "Agent Insights"}
          </h2>
          <button
            onClick={onOpenAgentsTab}
            className="text-xs font-semibold text-blue-600 hover:text-blue-800 transition"
          >
            {language === "ml" ? "എല്ലാം കാണുക" : "View All"}
          </button>
        </div>

        {/* Featured Agent Card Graphic / Identity */}
        <div className="rounded-xl border border-blue-100 bg-[#f0f7ff] p-4 mb-4">
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center space-x-2">
                <span className="flex h-2 w-2 rounded-full bg-blue-600 animate-pulse" />
                <span className="text-[10px] font-bold uppercase tracking-wider text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                  Active Supervisor
                </span>
              </div>
              <h3 className="mt-1.5 text-base font-bold text-slate-900 tracking-tight">
                Supervisor Agent
              </h3>
              <p className="text-xs text-slate-500">
                Autonomous. Multi-tool. Production-ready.
              </p>
            </div>

            {/* Stylized geometric glyph badge */}
            <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-blue-200 bg-white text-blue-600 shadow-xs">
              <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
              </svg>
            </div>
          </div>
        </div>

        {/* Spec Rows Table */}
        <div className="divide-y divide-slate-100 text-xs">
          <div className="flex justify-between py-2 text-slate-500">
            <span>Model Engine</span>
            <span className="font-medium text-slate-900">Gemini 2.0 Flash</span>
          </div>
          <div className="flex justify-between py-2 text-slate-500">
            <span>Context Window</span>
            <span className="font-mono font-medium text-slate-900">1,048,576 Tokens</span>
          </div>
          <div className="flex justify-between py-2 text-slate-500">
            <span>Speech Recognition</span>
            <span className="font-medium text-slate-900">Web Speech (EN / ML)</span>
          </div>
          <div className="flex justify-between py-2 text-slate-500">
            <span>Response Latency</span>
            <span className="font-mono font-medium text-blue-600">38 ms (Sub-50ms target)</span>
          </div>
          <div className="flex justify-between py-2 text-slate-500">
            <span>Fact Verification</span>
            <span className="font-medium text-slate-900">100% Guardrail Validated</span>
          </div>
          <div className="flex justify-between py-2 text-slate-500">
            <span>Active Integrations</span>
            <span className="font-medium text-slate-900">Web, Vector Store, Python</span>
          </div>
          <div className="flex justify-between py-2 text-slate-500">
            <span>Memory Persistence</span>
            <span className="font-medium text-slate-900">Enabled (Vector + State)</span>
          </div>
          <div className="flex justify-between py-2 text-slate-500">
            <span>DPDP Compliance</span>
            <span className="font-medium text-blue-700">Active & Enforced</span>
          </div>
        </div>

        {/* Two Action Buttons */}
        <div className="mt-5 grid grid-cols-2 gap-2 pt-2">
          <button
            onClick={onOpenAgentsTab}
            className="rounded-lg border border-blue-600 bg-blue-600 py-2.5 text-xs font-semibold text-white shadow-xs hover:bg-blue-700 transition active:scale-98 text-center"
          >
            {language === "ml" ? "എല്ലാ ഏജന്റുകളും" : "View All Agents"}
          </button>
          <button
            onClick={onOpenMemoryTab}
            className="rounded-lg border border-slate-200 bg-white py-2.5 text-xs font-semibold text-slate-700 hover:border-blue-300 hover:bg-blue-50 hover:text-blue-600 transition active:scale-98 text-center"
          >
            {language === "ml" ? "മെമ്മറി കാണുക" : "Inspect Memory"}
          </button>
        </div>
      </div>

      {/* Bottom Card: Recent Conversations */}
      <div className="rounded-2xl border border-slate-200/90 bg-white p-6 shadow-xs">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
          <h2 className="text-sm font-bold text-slate-900 tracking-tight">
            {language === "ml" ? "സമീപകാല സംഭാഷണങ്ങൾ" : "Recent Conversations"}
          </h2>
          <span className="text-xs font-semibold text-blue-600">
            {recentConversations.length} total
          </span>
        </div>

        {/* Search Input for history */}
        <div className="mb-3">
          <input
            type="text"
            value={searchHistory}
            onChange={(e) => setSearchHistory(e.target.value)}
            placeholder="Search past conversations..."
            className="w-full rounded-md border border-slate-200 bg-slate-50/70 px-3 py-1.5 text-xs text-slate-900 placeholder-slate-400 focus:bg-white focus:border-blue-600 focus:ring-1 focus:ring-blue-100 focus:outline-none"
          />
        </div>

        {/* List of recent conversations with SVG icons */}
        <div className="space-y-2">
          {filteredHistory.map((item) => (
            <div
              key={item.id}
              onClick={() => onResumeSession(item.title, item.query, item.response)}
              className="group flex items-start space-x-3 rounded-xl border border-transparent p-2.5 hover:border-blue-100 hover:bg-blue-50/40 transition cursor-pointer"
            >
              {/* Icon container */}
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-blue-100 bg-blue-50/60 text-blue-600 group-hover:bg-blue-600 group-hover:text-white group-hover:border-blue-600 transition shadow-xs mt-0.5">
                {item.icon === "research" ? (
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                ) : item.icon === "finance" ? (
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                ) : item.icon === "plan" ? (
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                  </svg>
                ) : (
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                )}
              </div>

              {/* Text metadata */}
              <div className="flex-1 min-w-0">
                <div className="flex items-baseline justify-between">
                  <h4 className="text-xs font-semibold text-slate-900 truncate group-hover:text-blue-600 transition">
                    {item.title}
                  </h4>
                  <span className="text-[10px] text-slate-400 shrink-0 ml-2">
                    {item.time}
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 truncate mt-0.5">
                  {item.subtitle}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
