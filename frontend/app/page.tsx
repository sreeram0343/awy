"use client";

import React, { useState } from "react";
import { Header, NavTab } from "../components/Header";
import { VoiceAssistant } from "../components/VoiceAssistant";
import { ChatView } from "../components/ChatView";
import { AgentsPanel } from "../components/AgentsPanel";
import { MemoryPanel } from "../components/MemoryPanel";
import { IntegrationsPanel } from "../components/IntegrationsPanel";

export default function Home() {
  const [activeTab, setActiveTab] = useState<NavTab>("voice");
  const [language, setLanguage] = useState<"en" | "ml">("en");
  const [connectionState, setConnectionState] = useState<string>("listening");

  const handleSelectAgentPrompt = (prompt: string) => {
    setActiveTab("voice");
  };

  return (
    <div className="flex min-h-screen flex-col bg-white text-slate-900 selection:bg-blue-600 selection:text-white">
      {/* Precision Header matching screenshot */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        language={language}
        setLanguage={setLanguage}
        connectionState={connectionState}
      />

      {/* Main Dynamic View Area */}
      <main className="flex-1 pb-16">
        {activeTab === "voice" && (
          <VoiceAssistant
            language={language}
            setLanguage={setLanguage}
            setGlobalConnectionState={setConnectionState}
            onOpenAgentsTab={() => setActiveTab("agents")}
            onOpenMemoryTab={() => setActiveTab("memory")}
          />
        )}

        {activeTab === "chat" && (
          <ChatView language={language} />
        )}

        {activeTab === "agents" && (
          <AgentsPanel
            language={language}
            onSelectAgentPrompt={handleSelectAgentPrompt}
          />
        )}

        {activeTab === "memory" && (
          <MemoryPanel language={language} />
        )}

        {activeTab === "integrations" && (
          <IntegrationsPanel language={language} />
        )}
      </main>

      {/* Minimalist White Footer matching design aesthetic */}
      <footer className="border-t border-slate-200/80 bg-white py-6">
        <div className="mx-auto flex max-w-7xl flex-col sm:flex-row items-center justify-between px-4 sm:px-6 lg:px-8 text-xs text-slate-500 gap-3">
          <div>
            <p className="font-semibold text-slate-800">
              AWY • Agent With You — Autonomous AI Platform
            </p>
            <p className="mt-0.5 text-[11px] text-slate-400">
              {language === "ml"
                ? "വോയ്‌സ്-ഫസ്റ്റ് മൾട്ടി-ഏജന്റ് ഇന്റലിജൻസ്, പെർസിസ്റ്റന്റ് മെമ്മറി, റിയൽ-ടൈം ടൂൾ കോർഡിനേഷൻ."
                : "Voice-first multi-agent intelligence with persistent vector memory and real-time tool coordination."}
            </p>
          </div>

          <div className="flex items-center space-x-4 text-[11px]">
            <span className="hover:text-blue-600 transition cursor-pointer">
              {language === "ml" ? "സ്വകാര്യതാ നയം" : "Privacy Policy"}
            </span>
            <span>•</span>
            <span className="hover:text-blue-600 transition cursor-pointer">
              {language === "ml" ? "നിബന്ധനകൾ" : "Terms of Service"}
            </span>
            <span>•</span>
            <span className="font-medium text-blue-700">
              DPDP Act (India) Adherent
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}
