"use client";

import React, { useState, useRef, useEffect } from "react";

interface ChatViewProps {
  language: "en" | "ml";
}

interface ChatMessage {
  id: string;
  sender: "user" | "agent";
  text: string;
  timestamp: string;
  toolTrace?: {
    tool_name: string;
    output_summary: string;
    latency_ms: number;
  };
}

export const ChatView: React.FC<ChatViewProps> = ({ language }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "c-1",
      sender: "agent",
      text:
        language === "ml"
          ? "നമസ്കാരം! ഞാൻ AWY, നിങ്ങളുടെ ഓട്ടോണമസ് AI അസിസ്റ്റന്റാണ്. സങ്കീർണ്ണമായ ഗവേഷണങ്ങൾ, പ്ലാനിംഗ്, കോഡിംഗ് എന്നിവയിൽ ഞാൻ എങ്ങനെ സഹായിക്കണം?"
          : "Hello! I am AWY, your autonomous AI assistant. How can I assist you with deep research, complex planning, document analysis, or code execution today?",
      timestamp: "Just now",
    },
  ]);
  const [inputText, setInputText] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSubmit = async (e?: React.FormEvent, customText?: string) => {
    if (e) e.preventDefault();
    const query = (customText || inputText).trim();
    if (!query) return;

    setInputText("");
    const userMsg: ChatMessage = {
      id: `u-${Date.now()}`,
      sender: "user",
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/api/v1/voice/text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: "chat-session-" + Math.random().toString(36).substring(2, 7),
          text: query,
          language,
        }),
      });
      const json = await res.json();
      const agentMsg: ChatMessage = {
        id: `a-${Date.now()}`,
        sender: "agent",
        text: json.data.response_text,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        toolTrace: json.data.tool_executed,
      };
      setMessages((prev) => [...prev, agentMsg]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: `a-${Date.now()}`,
          sender: "agent",
          text:
            language === "ml"
              ? "ക്ഷമിക്കണം, കണക്ഷൻ തകരാറിലായി. വീണ്ടും ശ്രമിക്കുക."
              : "Apologies, could not reach the agent server. Please retry.",
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="border-b border-slate-200/80 pb-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900">
            {language === "ml" ? "ഡീപ് ചാറ്റ് വർക്ക്‌സ്‌പേസ്" : "Direct Agent Chat"}
          </h1>
          <p className="mt-0.5 text-xs text-slate-500">
            High-bandwidth conversation with tool calling and markdown formatting
          </p>
        </div>
        <button
          onClick={() => setMessages([])}
          className="text-xs text-slate-400 hover:text-blue-600 transition font-medium"
        >
          Clear Chat
        </button>
      </div>

      {/* Messages */}
      <div className="mt-6 rounded-2xl border border-slate-200/90 bg-white p-6 shadow-xs min-h-[480px] flex flex-col justify-between">
        <div className="space-y-4 max-h-[500px] overflow-y-auto pr-1">
          {messages.map((m) => (
            <div
              key={m.id}
              className={`flex items-start space-x-3 text-xs ${
                m.sender === "user" ? "justify-end" : "justify-start"
              }`}
            >
              {m.sender === "agent" && (
                <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-blue-200 bg-white text-blue-600 shadow-xs mt-0.5">
                  <svg className="h-4 w-4 text-blue-600" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2.5a2 2 0 0 0-1.732 1l-7.794 13.5A2 2 0 0 0 4.206 20h15.588a2 2 0 0 0 1.732-3L13.732 3.5A2 2 0 0 0 12 2.5Zm0 3.866 5.88 10.184H6.12L12 6.366Z" />
                  </svg>
                </div>
              )}

              <div
                className={`max-w-xl rounded-xl p-3.5 leading-relaxed ${
                  m.sender === "user"
                    ? "bg-blue-600 text-white shadow-xs"
                    : "border border-blue-100 bg-[#f0f7ff] text-slate-900 shadow-xs"
                }`}
              >
                <p>{m.text}</p>
                {m.toolTrace && (
                  <div className="mt-2.5 rounded-lg border border-blue-200/80 bg-white p-2 text-[10px] font-mono text-slate-700">
                    <div className="flex justify-between items-center text-slate-900 font-semibold mb-0.5">
                      <span className="flex items-center space-x-1">
                        <span className="h-1.5 w-1.5 rounded-full bg-blue-600" />
                        <span className="text-blue-900 font-mono">Tool: {m.toolTrace.tool_name}</span>
                      </span>
                      <span className="text-blue-600 font-bold text-[10px]">{m.toolTrace.latency_ms} ms</span>
                    </div>
                    <p className="font-sans text-slate-500 text-[10px]">{m.toolTrace.output_summary}</p>
                  </div>
                )}
                <span className={`block mt-1.5 text-[10px] ${m.sender === "user" ? "text-blue-100 text-right" : "text-slate-400"}`}>
                  {m.timestamp}
                </span>
              </div>

              {m.sender === "user" && (
                <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-blue-200 bg-blue-50 text-xs font-bold text-blue-700 shadow-xs mt-0.5">
                  R
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex items-center space-x-2 text-xs text-blue-600 font-medium py-2">
              <div className="h-2 w-2 rounded-full bg-blue-600 animate-pulse" />
              <span>AWY is reasoning...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <form onSubmit={handleSubmit} className="mt-4 pt-3 border-t border-slate-100 flex items-center space-x-2">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-xs text-slate-900 placeholder-slate-400 focus:border-blue-600 focus:ring-1 focus:ring-blue-100 focus:outline-none"
          />
          <button
            type="submit"
            disabled={!inputText.trim() || loading}
            className="rounded-xl border border-blue-600 bg-blue-600 px-4 py-2.5 text-xs font-semibold text-white shadow-xs hover:bg-blue-700 disabled:opacity-40 transition active:scale-98"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
};
