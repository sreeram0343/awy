"use client";

import React, { useState } from "react";
import { Header } from "../components/Header";
import { VoiceAssistant } from "../components/VoiceAssistant";

export default function Home() {
  const [language, setLanguage] = useState<"en" | "ml">("en");
  const [connectionState, setConnectionState] = useState<string>("idle");

  return (
    <div className="flex min-h-screen flex-col bg-slate-50 selection:bg-blue-600 selection:text-white">
      {/* Top Header */}
      <Header
        language={language}
        setLanguage={setLanguage}
        connectionState={connectionState}
      />

      {/* Main Content Area */}
      <main className="flex-1 pb-16">
        <VoiceAssistant
          language={language}
          setLanguage={setLanguage}
          setGlobalConnectionState={setConnectionState}
        />
      </main>

      {/* Trust & Compliance Footer */}
      <footer className="border-t border-slate-200 bg-white py-6">
        <div className="mx-auto flex max-w-7xl flex-col sm:flex-row items-center justify-between px-4 sm:px-6 text-xs text-slate-500 gap-3">
          <div>
            <p className="font-semibold text-slate-700">
              Agent Automotive Platform • Apex Motors Kerala
            </p>
            <p className="mt-0.5 text-slate-400">
              {language === "ml"
                ? "വിവരങ്ങൾ പരിശോധിച്ച കാറ്റലോഗിനെ അടിസ്ഥാനമാക്കിയുള്ളതാണ്. EMI എസ്റ്റിമേറ്റുകൾ നിർദ്ദേശകം മാത്രമാണ്."
                : "All vehicle specifications and ex-showroom prices are indicative and verified. Subject to final dealership confirmation."}
            </p>
          </div>

          <div className="flex items-center space-x-4">
            <span className="hover:text-slate-700 cursor-pointer">
              {language === "ml" ? "സ്വകാര്യതാ നയം" : "Privacy Policy"}
            </span>
            <span>•</span>
            <span className="hover:text-slate-700 cursor-pointer">
              {language === "ml" ? "നിബന്ധനകൾ" : "Terms of Service"}
            </span>
            <span>•</span>
            <span className="hover:text-slate-700 cursor-pointer">
              DPDP Act (India) Adherent
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}
