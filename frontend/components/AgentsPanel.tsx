"use client";

import React, { useState } from "react";

interface AgentsPanelProps {
  language: "en" | "ml";
  onSelectAgentPrompt: (prompt: string) => void;
}

interface AgentInfo {
  id: string;
  name: string;
  role: string;
  description: string;
  model: string;
  status: "active" | "idle";
  tools: string[];
  latency_target: string;
  samplePrompt: string;
}

export const AgentsPanel: React.FC<AgentsPanelProps> = ({
  language,
  onSelectAgentPrompt,
}) => {
  const [selectedAgentId, setSelectedAgentId] = useState<string>("supervisor");

  const agents: AgentInfo[] = [
    {
      id: "supervisor",
      name: "Supervisor Agent",
      role: "Intent Triage & Orchestration",
      description: "Coordinates specialist agents, triages user intents, enforces execution boundaries, and synthesizes consensus answers.",
      model: "Gemini 2.0 Flash",
      status: "active",
      tools: ["intent_router", "state_synthesizer", "handoff_controller"],
      latency_target: "< 25ms",
      samplePrompt: "Orchestrate a comprehensive research and execution plan for launching our autonomous agent API."
    },
    {
      id: "research",
      name: "Research Agent",
      role: "Autonomous Web & Literature Retrieval",
      description: "Conducts deep multi-source retrieval, analyzes academic papers, checks citations, and extracts verified findings.",
      model: "Gemini 2.0 Flash + Web API",
      status: "active",
      tools: ["web_search", "academic_arxiv_parser", "citation_verifier"],
      latency_target: "< 45ms",
      samplePrompt: "Research recent breakthroughs in multimodal reasoning models and extract key takeaways."
    },
    {
      id: "planning",
      name: "Planning Agent",
      role: "Hierarchical Task Decomposition",
      description: "Decomposes complex ambiguous goals into deterministic milestone graphs with clear dependency ordering.",
      model: "Gemini 2.0 Flash",
      status: "active",
      tools: ["dag_planner", "dependency_resolver", "milestone_tracker"],
      latency_target: "< 20ms",
      samplePrompt: "Generate a multi-step task execution plan for Q4 engineering objectives with dependencies."
    },
    {
      id: "analyst",
      name: "Document & Code Agent",
      role: "Code Execution & Document Analysis",
      description: "Parses complex documents, extracts structured data, runs sandboxed Python code, and computes exact figures.",
      model: "Gemini 2.0 Flash + Python Sandbox",
      status: "active",
      tools: ["python_sandbox", "pdf_ast_extractor", "table_summarizer"],
      latency_target: "< 35ms",
      samplePrompt: "Analyze document structure, parse tabular data, and extract high-priority action items."
    },
    {
      id: "memory",
      name: "Memory & Context Agent",
      role: "Vector Checkpointing & Recall",
      description: "Indexes conversation turns into semantic vector storage, maintains user profiles, and resolves cross-session references.",
      model: "Gemini 2.0 Flash + Qdrant",
      status: "active",
      tools: ["vector_index_search", "profile_updater", "session_checkpoint"],
      latency_target: "< 18ms",
      samplePrompt: "Summarize conversation history and persist key decisions to vector storage."
    },
    {
      id: "verification",
      name: "Verification & Guardrail Agent",
      role: "Fact-Checking & Safety Verification",
      description: "Validates agent outputs against deterministic truth sources, flags hallucinations, and enforces DPDP compliance walls.",
      model: "Deterministic Logic Engine",
      status: "active",
      tools: ["fact_checker", "dpdp_pii_filter", "latency_guard"],
      latency_target: "< 10ms",
      samplePrompt: "Verify factual claims and ensure zero hallucination in generated summaries."
    }
  ];

  const selectedAgent = agents.find((a) => a.id === selectedAgentId) || agents[0];

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="border-b border-slate-200/80 pb-5">
        <h1 className="text-xl font-bold tracking-tight text-slate-900 sm:text-2xl">
          {language === "ml" ? "ഏജന്റ് സ്ക്വാഡ് & ശേഷികൾ" : "Agent Squad & Orchestration"}
        </h1>
        <p className="mt-1 text-xs text-slate-500">
          {language === "ml"
            ? "ലഭ്യമായ സ്പെഷ്യലിസ്റ്റ് AI ഏജന്റുകൾ, അവയുടെ ശേഷികൾ, ടാസ്ക് എക്സിക്യൂഷൻ"
            : "Manage autonomous specialist agents, inspect capabilities, and dispatch targeted workflows"}
        </p>
      </div>

      <div className="mt-8 grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: List of Agents */}
        <div className="lg:col-span-5 space-y-3">
          {agents.map((agent) => {
            const isSelected = selectedAgentId === agent.id;
            return (
              <div
                key={agent.id}
                onClick={() => setSelectedAgentId(agent.id)}
                className={`rounded-xl border p-4 cursor-pointer transition ${
                  isSelected
                    ? "border-blue-600 bg-blue-50/20 shadow-xs ring-1 ring-blue-500"
                    : "border-slate-200 bg-white hover:border-blue-200 hover:bg-slate-50/60"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className={`h-2 w-2 rounded-full ${isSelected ? "bg-blue-600 animate-pulse" : "bg-blue-500"}`} />
                      <h3 className={`text-xs font-bold ${isSelected ? "text-blue-950 font-bold" : "text-slate-900"}`}>{agent.name}</h3>
                    </div>
                    <p className="text-[11px] font-medium text-slate-500 mt-0.5">{agent.role}</p>
                  </div>
                  <span className="rounded border border-blue-200 bg-blue-50/70 px-2 py-0.5 text-[10px] font-mono font-semibold text-blue-700">
                    {agent.latency_target}
                  </span>
                </div>
                <p className="mt-2 text-xs text-slate-600 line-clamp-2 leading-relaxed">{agent.description}</p>
              </div>
            );
          })}
        </div>

        {/* Right Column: Detailed Inspector */}
        <div className="lg:col-span-7">
          <div className="rounded-2xl border border-slate-200/90 bg-white p-6 shadow-xs space-y-6">
            <div className="flex items-start justify-between border-b border-slate-100 pb-4">
              <div>
                <div className="flex items-center space-x-2">
                  <span className="h-2 w-2 rounded-full bg-blue-600 animate-pulse" />
                  <span className="text-[10px] font-bold uppercase tracking-wider text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                    {selectedAgent.status.toUpperCase()}
                  </span>
                </div>
                <h2 className="mt-2 text-lg font-bold text-slate-900">{selectedAgent.name}</h2>
                <p className="text-xs text-slate-500">{selectedAgent.role}</p>
              </div>

              <span className="rounded-lg border border-blue-100 bg-blue-50/50 px-3 py-1 text-xs font-mono font-semibold text-blue-700">
                {selectedAgent.model}
              </span>
            </div>

            <p className="text-xs leading-relaxed text-slate-700">{selectedAgent.description}</p>

            {/* Available Tools */}
            <div>
              <span className="block text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-2">
                Connected Business Tools
              </span>
              <div className="flex flex-wrap gap-1.5">
                {selectedAgent.tools.map((t, idx) => (
                  <span
                    key={idx}
                    className="rounded-md border border-blue-200/80 bg-blue-50/60 px-2.5 py-1 text-xs font-mono text-blue-900"
                  >
                    {t}
                  </span>
                ))}
              </div>
            </div>

            {/* Test Execution Prompt */}
            <div className="rounded-xl border border-blue-100 bg-[#f0f7ff] p-4 space-y-3">
              <span className="block text-[10px] font-semibold uppercase tracking-wider text-blue-600">
                Sample Task Prompt
              </span>
              <p className="text-xs font-medium text-slate-800">&quot;{selectedAgent.samplePrompt}&quot;</p>
              <button
                onClick={() => onSelectAgentPrompt(selectedAgent.samplePrompt)}
                className="w-full rounded-lg border border-blue-600 bg-blue-600 py-2.5 text-xs font-semibold text-white shadow-xs hover:bg-blue-700 transition active:scale-98"
              >
                Dispatch Task to {selectedAgent.name}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
