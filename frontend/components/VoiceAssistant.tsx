"use client";

import React, { useState, useEffect, useRef } from "react";
import { AudioVisualizer } from "./AudioVisualizer";
import { AgentSidebar } from "./AgentSidebar";

interface ToolTrace {
  tool_name: string;
  status: string;
  input_parameters?: Record<string, unknown>;
  output_summary: string;
  latency_ms: number;
}

interface Message {
  id: string;
  sender: "user" | "agent";
  text: string;
  timestamp: string;
  language: "en" | "ml";
  toolTrace?: ToolTrace;
  rating?: "positive" | "negative";
}

interface VoiceAssistantProps {
  language: "en" | "ml";
  setLanguage: (lang: "en" | "ml") => void;
  setGlobalConnectionState: (state: string) => void;
  onOpenAgentsTab: () => void;
  onOpenMemoryTab: () => void;
}

interface IWindowSpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start: () => void;
  stop: () => void;
  abort: () => void;
  onresult: ((event: ISpeechRecognitionEvent) => void) | null;
  onerror: ((event: unknown) => void) | null;
  onend: (() => void) | null;
}

interface ISpeechRecognitionEvent {
  resultIndex: number;
  results: {
    length: number;
    [index: number]: {
      isFinal: boolean;
      [index: number]: {
        transcript: string;
      };
    };
  };
}

export const VoiceAssistant: React.FC<VoiceAssistantProps> = ({
  language,
  setGlobalConnectionState,
  onOpenAgentsTab,
  onOpenMemoryTab,
}) => {
  const [sessionState, setSessionState] = useState<
    "idle" | "requesting_mic" | "connecting" | "listening" | "processing" | "speaking" | "interrupted" | "failed" | "ended"
  >("idle");
  const [audioLevel, setAudioLevel] = useState<number>(0.23);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "init-u1",
      sender: "user",
      text: "Research recent breakthroughs in multimodal reasoning models and extract key takeaways.",
      timestamp: "10:24 AM",
      language: "en",
    },
    {
      id: "init-a1",
      sender: "agent",
      text:
        language === "ml"
          ? "മൾട്ടി-മോഡൽ റീസണിംഗ് മോഡലുകളെക്കുറിച്ചുള്ള പുതിയ കണ്ടെത്തലുകൾ ഞാൻ വിശകലനം ചെയ്തു: പുതിയ ആർക്കിടെക്ചറുകൾ ചിത്രങ്ങളും ടെക്സ്റ്റും ഒരേസമയം അപഗ്രഥിച്ച് 40% കൂടുതൽ കൃത്യത നൽകുന്നു. പ്രധാന കണ്ടെത്തലുകൾ വിശദീകരിക്കണോ?"
          : "Frontier multimodal reasoning models now integrate dense visual token encoders with cross-attention layers, demonstrating a 40% reduction in spatial reasoning hallucinations. Would you like me to elaborate on the architectural benchmarks or summarize specific papers?",
      timestamp: "10:24 AM",
      language: language,
      toolTrace: {
        tool_name: "web_research",
        status: "success",
        output_summary: "Synthesized 6 academic benchmark publications",
        latency_ms: 22.4,
      },
    },
  ]);
  const [inputText, setInputText] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [showContextModal, setShowContextModal] = useState(false);
  const [feedbackLoggedId, setFeedbackLoggedId] = useState<string | null>(null);

  const socketRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const micStreamRef = useRef<MediaStream | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animFrameRef = useRef<number | null>(null);
  const recognitionRef = useRef<IWindowSpeechRecognition | null>(null);
  const speechIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    setGlobalConnectionState(sessionState);
  }, [sessionState, setGlobalConnectionState]);

  useEffect(() => {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.onvoiceschanged = () => {
        window.speechSynthesis.getVoices();
      };
    }
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sessionState]);

  useEffect(() => {
    return () => {
      stopAudioRecording();
      if (socketRef.current) socketRef.current.close();
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
      if (speechIntervalRef.current) clearInterval(speechIntervalRef.current);
      if (typeof window !== "undefined" && "speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch {
          // ignore
        }
      }
    };
  }, []);

  const initSession = async (): Promise<string> => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/voice/session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ language, dealership_id: "awy-core" }),
      });
      const data = await res.json();
      const id = data.data.session_id;
      setSessionId(id);
      return id;
    } catch {
      const fallbackId = "session-" + Math.random().toString(36).substring(2, 9);
      setSessionId(fallbackId);
      return fallbackId;
    }
  };

  const speakText = (text: string, lang: "en" | "ml" = language) => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) {
      setSessionState(micStreamRef.current ? "listening" : "idle");
      return;
    }

    try {
      window.speechSynthesis.cancel();
      if (speechIntervalRef.current) clearInterval(speechIntervalRef.current);

      const cleanText = text
        .replace(/[*_#`~[\]()]/g, "")
        .replace(/https?:\/\/\S+/g, "")
        .replace(/\s+/g, " ")
        .trim();

      if (!cleanText) {
        setSessionState(micStreamRef.current ? "listening" : "idle");
        return;
      }

      const utterance = new SpeechSynthesisUtterance(cleanText);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      utterance.lang = lang === "ml" ? "ml-IN" : "en-US";

      const voices = window.speechSynthesis.getVoices();
      if (voices && voices.length > 0) {
        if (lang === "ml") {
          const mlVoice = voices.find(
            (v) =>
              v.lang.startsWith("ml") ||
              v.name.toLowerCase().includes("malayalam") ||
              v.lang.includes("IN")
          );
          if (mlVoice) utterance.voice = mlVoice;
        } else {
          const enVoice =
            voices.find(
              (v) =>
                v.lang.startsWith("en") &&
                (v.name.includes("Natural") ||
                  v.name.includes("Google") ||
                  v.name.includes("Neural") ||
                  v.name.includes("Online") ||
                  v.name.includes("Samantha") ||
                  v.name.includes("Zira"))
            ) || voices.find((v) => v.lang.startsWith("en"));
          if (enVoice) utterance.voice = enVoice;
        }
      }

      utterance.onstart = () => {
        setSessionState("speaking");
        let step = 0;
        speechIntervalRef.current = setInterval(() => {
          step++;
          setAudioLevel(0.28 + 0.38 * Math.abs(Math.sin(step * 0.35)));
        }, 80);
      };

      utterance.onend = () => {
        if (speechIntervalRef.current) clearInterval(speechIntervalRef.current);
        setAudioLevel(0.23);
        setSessionState(micStreamRef.current ? "listening" : "idle");
      };

      utterance.onerror = () => {
        if (speechIntervalRef.current) clearInterval(speechIntervalRef.current);
        setAudioLevel(0.23);
        setSessionState(micStreamRef.current ? "listening" : "idle");
      };

      window.speechSynthesis.speak(utterance);
      if (window.speechSynthesis.paused) {
        window.speechSynthesis.resume();
      }
    } catch {
      setSessionState(micStreamRef.current ? "listening" : "idle");
    }
  };

  const startVoice = async () => {
    setSessionState("requesting_mic");

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          channelCount: 1,
          sampleRate: 16000,
        },
      });
      micStreamRef.current = stream;

      const audioCtx = new (window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)();
      audioContextRef.current = audioCtx;
      const source = audioCtx.createMediaStreamSource(stream);
      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      analyserRef.current = analyser;

      const dataArray = new Uint8Array(analyser.frequencyBinCount);
      const updateVolume = () => {
        analyser.getByteFrequencyData(dataArray);
        let sum = 0;
        for (let i = 0; i < dataArray.length; i++) {
          sum += dataArray[i];
        }
        const avg = sum / dataArray.length;
        setAudioLevel(Math.min(avg / 128, 1));
        animFrameRef.current = requestAnimationFrame(updateVolume);
      };
      updateVolume();

      const SpeechRec =
        (window as unknown as { SpeechRecognition?: new () => IWindowSpeechRecognition; webkitSpeechRecognition?: new () => IWindowSpeechRecognition }).SpeechRecognition ||
        (window as unknown as { webkitSpeechRecognition?: new () => IWindowSpeechRecognition }).webkitSpeechRecognition;

      if (SpeechRec) {
        try {
          const rec = new SpeechRec();
          rec.continuous = true;
          rec.interimResults = true;
          rec.lang = language === "ml" ? "ml-IN" : "en-IN";

          rec.onresult = (evt: ISpeechRecognitionEvent) => {
            let interim = "";
            let finalTranscript = "";
            for (let i = evt.resultIndex; i < evt.results.length; i++) {
              if (evt.results[i].isFinal) {
                finalTranscript += evt.results[i][0].transcript;
              } else {
                interim += evt.results[i][0].transcript;
              }
            }
            if (interim) {
              setInputText(interim);
              if (window.speechSynthesis && window.speechSynthesis.speaking) {
                handleInterrupt();
              }
            }
            if (finalTranscript.trim()) {
              setInputText(finalTranscript);
              handleTextSubmit(undefined, finalTranscript.trim());
            }
          };

          rec.onerror = () => {
            // ignore
          };

          rec.start();
          recognitionRef.current = rec;
        } catch {
          // ignore
        }
      }

      setSessionState("connecting");
      const currentSessionId = sessionId || (await initSession());

      const wsUrl = `ws://localhost:8000/api/v1/voice/stream/${currentSessionId}`;
      const ws = new WebSocket(wsUrl);
      socketRef.current = ws;

      ws.onopen = () => {
        setSessionState("listening");
        ws.send(JSON.stringify({ type: "start", language }));
      };

      ws.onmessage = async (evt) => {
        try {
          const payload = JSON.parse(evt.data);

          if (payload.type === "state_change") {
            setSessionState(payload.state);
          } else if (payload.type === "user_transcript") {
            addMessage("user", payload.text);
          } else if (payload.type === "agent_transcript") {
            addMessage("agent", payload.text);
            speakText(payload.text, language);
          } else if (payload.type === "tool_executed" && payload.tool) {
            setMessages((prev) => {
              if (prev.length === 0) return prev;
              const updated = [...prev];
              const last = updated[updated.length - 1];
              last.toolTrace = payload.tool;
              return updated;
            });
          }
        } catch (e) {
          console.error("Error parsing WebSocket message:", e);
        }
      };

      ws.onerror = () => {
        setSessionState("listening");
      };

      ws.onclose = () => {
        if (sessionState !== "ended" && sessionState !== "idle") {
          setSessionState("idle");
        }
      };
    } catch {
      setSessionState("failed");
    }
  };

  const stopAudioRecording = () => {
    if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    if (speechIntervalRef.current) clearInterval(speechIntervalRef.current);
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch {
        // ignore
      }
      recognitionRef.current = null;
    }
    if (micStreamRef.current) {
      micStreamRef.current.getTracks().forEach((track) => track.stop());
      micStreamRef.current = null;
    }
    if (socketRef.current) {
      try {
        socketRef.current.send(JSON.stringify({ type: "stop" }));
        socketRef.current.close();
      } catch {
        // ignore
      }
      socketRef.current = null;
    }
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
    setSessionState("idle");
    setAudioLevel(0);
  };

  const handleInterrupt = () => {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
    if (speechIntervalRef.current) clearInterval(speechIntervalRef.current);
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ type: "interrupt" }));
    }
    setSessionState("interrupted");
    setTimeout(() => {
      setSessionState(micStreamRef.current ? "listening" : "idle");
      setAudioLevel(0.23);
    }, 150);
  };

  const addMessage = (
    sender: "user" | "agent",
    text: string,
    toolTrace?: ToolTrace
  ) => {
    const newMsg: Message = {
      id: Math.random().toString(36).substring(2, 9),
      sender,
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      language,
      toolTrace,
    };
    setMessages((prev) => [...prev, newMsg]);
  };

  const handleTextSubmit = async (e?: React.FormEvent, customQuery?: string) => {
    if (e) e.preventDefault();
    const query = (customQuery || inputText).trim();
    if (!query) return;

    setInputText("");
    addMessage("user", query);

    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(
        JSON.stringify({
          type: "text_input",
          text: query,
          language,
        })
      );
      return;
    }

    setSessionState("processing");
    try {
      const currentSessionId = sessionId || (await initSession());
      const res = await fetch("http://localhost:8000/api/v1/voice/text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: currentSessionId,
          text: query,
          language,
        }),
      });

      const json = await res.json();
      const data = json.data;

      addMessage("agent", data.response_text, data.tool_executed);
      speakText(data.response_text, language);
    } catch {
      const errText =
        language === "ml"
          ? "ക്ഷമിക്കണം, സെർവറുമായി ബന്ധപ്പെടാൻ സാധിച്ചില്ല. ദയവായി വീണ്ടും ശ്രമിക്കുക."
          : "Apologies, could not reach the agent server. Please try again.";
      addMessage("agent", errText);
      speakText(errText, language);
    }
  };

  const handleFeedback = async (msgId: string, rating: "positive" | "negative", queryText: string, respText: string) => {
    setMessages((prev) =>
      prev.map((m) => (m.id === msgId ? { ...m, rating } : m))
    );
    setFeedbackLoggedId(msgId);
    setTimeout(() => setFeedbackLoggedId(null), 2000);

    try {
      await fetch("http://localhost:8000/api/v1/voice/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          query: queryText,
          response_text: respText,
          rating,
          category: rating === "positive" ? "accurate_synthesis" : "clarification_needed",
          language,
        }),
      });
    } catch {
      // ignore
    }
  };

  const handleReplay = (msg: Message) => {
    speakText(msg.text, msg.language);
  };

  const exportTranscript = () => {
    const textData = messages
      .map((m) => `[${m.timestamp}] ${m.sender.toUpperCase()}: ${m.text}`)
      .join("\n\n");
    const blob = new Blob([textData], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `AWY-Transcript-${new Date().toISOString().split("T")[0]}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const resumeSessionFromSidebar = (title: string, query: string, response: string) => {
    addMessage("user", query);
    setTimeout(() => {
      addMessage("agent", response, {
        tool_name: "vector_memory_retrieval",
        status: "success",
        output_summary: `Resumed session: ${title}`,
        latency_ms: 18.4,
      });
      speakText(response, language);
    }, 200);
  };

  const suggestedPrompts = [
    "Research recent breakthroughs in multimodal reasoning models",
    "Analyze document structure and extract key action items",
    "Generate a multi-step task execution plan for Q4 goals",
    "Summarize conversation history and persist key decisions",
  ];

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Two-Column Responsive Layout in White and Blue theme */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column (Main Voice Workspace + Live Transcript) */}
        <div className="lg:col-span-8 space-y-6">
          {/* Top Main Workspace Card */}
          <div className="rounded-2xl border border-slate-200/90 bg-white p-7 shadow-xs">
            {/* Header with Title and Right Action Buttons */}
            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
              <div>
                <span className="block text-[11px] font-semibold uppercase tracking-wider text-blue-600 mb-1">
                  {language === "ml"
                    ? "വോയ്‌സ്-ഫസ്റ്റ് മൾട്ടി-ഏജന്റ് അസിസ്റ്റന്റ്"
                    : "VOICE-FIRST MULTI-AGENT ASSISTANT"}
                </span>
                <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
                  {language === "ml"
                    ? "കൺവർസേഷണൽ ഏജന്റ് ഇന്റലിജൻസ്"
                    : "Conversational Autonomous Intelligence"}
                </h1>
                <p className="mt-1 text-xs text-slate-500 max-w-2xl">
                  {language === "ml"
                    ? "സ്വാഭാവിക മലയാളത്തിലോ ഇംഗ്ലീഷിലോ സംസാരിക്കുക. ആഴത്തിലുള്ള വെബ് റിസർച്ച്, പ്ലാനിംഗ്, റിയൽ-ടൈം ടാസ്ക് എക്സിക്യൂഷൻ."
                    : "Speak naturally in English or Malayalam. Verified autonomous reasoning, persistent vector memory, and real-time tool coordination."}
                </p>
              </div>

              {/* Action Buttons: [Agent Context] and [Export] in white & blue */}
              <div className="flex items-center space-x-2 shrink-0">
                <button
                  onClick={() => setShowContextModal(true)}
                  className="flex items-center space-x-1.5 rounded-lg border border-blue-200 bg-white px-3 py-1.5 text-xs font-semibold text-blue-700 shadow-xs hover:bg-blue-50/70 hover:border-blue-300 transition"
                >
                  <svg className="h-3.5 w-3.5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span>Agent Context</span>
                </button>

                <button
                  onClick={exportTranscript}
                  className="flex items-center space-x-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 shadow-xs hover:border-slate-300 hover:bg-slate-50 transition"
                >
                  <svg className="h-3.5 w-3.5 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  <span>Export</span>
                </button>
              </div>
            </div>

            {/* Central Voice Visualizer */}
            <div className="mt-6 pt-4 border-t border-slate-100">
              <AudioVisualizer
                state={sessionState}
                audioLevel={audioLevel}
                language={language}
                onToggleMic={
                  sessionState === "idle" || sessionState === "ended" || sessionState === "failed"
                    ? startVoice
                    : stopAudioRecording
                }
                onInterrupt={handleInterrupt}
              />
            </div>

            {/* SUGGESTED PROMPTS Section */}
            <div className="mt-6 border-t border-slate-100 pt-5">
              <span className="block text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-3">
                SUGGESTED PROMPTS
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                {suggestedPrompts.map((prompt, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleTextSubmit(undefined, prompt)}
                    className="rounded-xl border border-slate-200/90 bg-white p-3 text-left text-xs font-medium text-slate-800 shadow-xs hover:border-blue-300 hover:bg-blue-50/40 hover:text-blue-900 transition active:scale-99"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Bottom Card: Live Transcript */}
          <div className="rounded-2xl border border-slate-200/90 bg-white p-6 shadow-xs">
            {/* Header: ● CONSULTATION TRANSCRIPT with Clear button */}
            <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
              <div className="flex items-center space-x-2">
                <span className="h-2 w-2 rounded-full bg-blue-600 animate-pulse" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900">
                  CONSULTATION TRANSCRIPT
                </h3>
              </div>
              <button
                onClick={() => setMessages([])}
                className="flex items-center space-x-1 text-xs text-slate-400 hover:text-slate-700 transition"
              >
                <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                <span>Clear</span>
              </button>
            </div>

            {/* Messages Stream */}
            <div className="max-h-96 overflow-y-auto space-y-4 pr-1">
              {messages.map((msg) => (
                <div key={msg.id} className="flex items-start space-x-3 text-xs">
                  {/* Avatar */}
                  {msg.sender === "user" ? (
                    <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-blue-200 bg-blue-50 text-xs font-bold text-blue-700 shadow-xs mt-0.5">
                      R
                    </div>
                  ) : (
                    <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-blue-200 bg-white text-blue-600 shadow-xs mt-0.5">
                      <svg className="h-4 w-4 text-blue-600" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 2.5a2 2 0 0 0-1.732 1l-7.794 13.5A2 2 0 0 0 4.206 20h15.588a2 2 0 0 0 1.732-3L13.732 3.5A2 2 0 0 0 12 2.5Zm0 3.866 5.88 10.184H6.12L12 6.366Z" />
                      </svg>
                    </div>
                  )}

                  {/* Message Bubble */}
                  <div className="flex-1 space-y-1">
                    <div
                      className={`rounded-xl p-3.5 leading-relaxed ${
                        msg.sender === "user"
                          ? "border border-slate-200 bg-slate-50/80 text-slate-900"
                          : "border border-blue-100 bg-[#f0f7ff] text-slate-900 shadow-xs"
                      }`}
                    >
                      <p>{msg.text}</p>

                      {/* Tool Execution Badge */}
                      {msg.toolTrace && (
                        <div className="mt-2.5 rounded-lg border border-blue-200/80 bg-white p-2 text-[11px] font-mono text-slate-700">
                          <div className="flex justify-between items-center text-slate-900 font-semibold mb-0.5">
                            <span className="flex items-center space-x-1">
                              <span className="h-1.5 w-1.5 rounded-full bg-blue-600" />
                              <span className="text-blue-900 font-mono">Tool: {msg.toolTrace.tool_name}</span>
                            </span>
                            <span className="text-blue-600 font-bold text-[10px]">
                              {msg.toolTrace.latency_ms} ms
                            </span>
                          </div>
                          <p className="font-sans text-[11px] text-slate-500">
                            {msg.toolTrace.output_summary}
                          </p>
                        </div>
                      )}
                    </div>

                    {/* Timestamp & Actions */}
                    <div className="flex items-center space-x-3 text-[10px] text-slate-400 px-1">
                      <span>{msg.timestamp}</span>
                      {msg.sender === "agent" && (
                        <>
                          <span>•</span>
                          <button
                            onClick={() => handleReplay(msg)}
                            className="hover:text-blue-600 transition font-medium"
                          >
                            Replay Voice
                          </button>
                          <span>•</span>
                          <button
                            onClick={() => navigator.clipboard.writeText(msg.text)}
                            className="hover:text-blue-600 transition font-medium"
                          >
                            Copy
                          </button>
                          <span>•</span>
                          <button
                            onClick={() =>
                              handleFeedback(
                                msg.id,
                                "positive",
                                "User query",
                                msg.text
                              )
                            }
                            className={`hover:text-blue-600 transition ${
                              msg.rating === "positive" ? "text-blue-600 font-bold" : ""
                            }`}
                          >
                            ✓ Helpful
                          </button>
                          <button
                            onClick={() =>
                              handleFeedback(
                                msg.id,
                                "negative",
                                "User query",
                                msg.text
                              )
                            }
                            className={`hover:text-rose-600 transition ${
                              msg.rating === "negative" ? "text-rose-600 font-bold" : ""
                            }`}
                          >
                            ✕
                          </button>
                        </>
                      )}
                    </div>

                    {feedbackLoggedId === msg.id && (
                      <span className="text-[10px] text-blue-600 font-medium block px-1">
                        Feedback logged to agent self-improvement pipeline
                      </span>
                    )}
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* Typed Chat Input Form */}
            <form
              onSubmit={(e) => handleTextSubmit(e)}
              className="mt-4 flex items-center space-x-2 border-t border-slate-100 pt-3"
            >
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder={
                  language === "ml"
                    ? "സന്ദേശം ടൈപ്പ് ചെയ്യുക അല്ലെങ്കിൽ മൈക്രോഫോൺ ഉപയോഗിക്കുക..."
                    : "Type your query or click microphone above (e.g. Research AI breakthroughs, analyze documents)..."
                }
                className="flex-1 rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-xs text-slate-900 placeholder-slate-400 focus:border-blue-600 focus:ring-1 focus:ring-blue-100 focus:outline-none"
              />
              <button
                type="submit"
                disabled={!inputText.trim()}
                className="rounded-xl border border-blue-600 bg-blue-600 px-4 py-2.5 text-xs font-semibold text-white shadow-xs hover:bg-blue-700 disabled:opacity-40 transition active:scale-98"
              >
                Send
              </button>
            </form>
          </div>
        </div>

        {/* Right Column: AgentSidebar */}
        <div className="lg:col-span-4">
          <AgentSidebar
            language={language}
            onSelectPrompt={(p) => handleTextSubmit(undefined, p)}
            onOpenAgentsTab={onOpenAgentsTab}
            onOpenMemoryTab={onOpenMemoryTab}
            onResumeSession={resumeSessionFromSidebar}
          />
        </div>
      </div>

      {/* Agent Context Modal */}
      {showContextModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 backdrop-blur-xs p-4">
          <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-6 shadow-xl text-xs space-y-4">
            <div className="flex items-start justify-between border-b border-slate-100 pb-3">
              <div>
                <span className="text-[10px] font-semibold uppercase tracking-wider text-blue-600">
                  Agent State Inspector
                </span>
                <h3 className="text-base font-bold text-slate-900">Active Session Context</h3>
              </div>
              <button
                onClick={() => setShowContextModal(false)}
                className="text-slate-400 hover:text-slate-600 text-sm"
              >
                ✕
              </button>
            </div>

            <div className="rounded-xl border border-blue-100 bg-blue-50/40 p-3.5 space-y-2">
              <div className="flex justify-between">
                <span className="text-slate-500">Active Supervisor</span>
                <span className="font-semibold text-slate-900">AWY LangGraph Orchestrator</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Multilingual State</span>
                <span className="font-medium text-slate-900">{language === "ml" ? "Malayalam (ml-IN)" : "English (en-IN)"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Speech Synthesis</span>
                <span className="font-semibold text-blue-600">Natural Human Voice (Active)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Vector Store Checkpoints</span>
                <span className="font-mono text-slate-900">Qdrant Active</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Turn Count</span>
                <span className="font-mono text-slate-900">{messages.length} messages</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Guardrails Mode</span>
                <span className="font-medium text-blue-700">Deterministic Fact-Check Active</span>
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setShowContextModal(false)}
                className="rounded-lg border border-blue-600 bg-blue-600 px-4 py-2 text-xs font-semibold text-white hover:bg-blue-700 shadow-xs"
              >
                Close Context
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
