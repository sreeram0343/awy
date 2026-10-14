"use client";

import React, { useState, useEffect, useRef } from "react";
import { AudioVisualizer } from "./AudioVisualizer";
import { VehicleCard, Vehicle } from "./VehicleCard";

interface Message {
  id: string;
  sender: "user" | "agent";
  text: string;
  timestamp: string;
  language: "en" | "ml";
}

interface VoiceAssistantProps {
  language: "en" | "ml";
  setLanguage: (lang: "en" | "ml") => void;
  setGlobalConnectionState: (state: string) => void;
}

export const VoiceAssistant: React.FC<VoiceAssistantProps> = ({
  language,
  setLanguage,
  setGlobalConnectionState,
}) => {
  const [sessionState, setSessionState] = useState<
    "idle" | "requesting_mic" | "connecting" | "listening" | "processing" | "speaking" | "interrupted" | "failed" | "ended"
  >("idle");
  const [audioLevel, setAudioLevel] = useState<number>(0);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "init",
      sender: "agent",
      text:
        language === "ml"
          ? "നമസ്കാരം! ഞാൻ Apex Motors-ന്റെ AI വെഹിക്കിൾ അസിസ്റ്റന്റാണ്. വാഹനങ്ങളുടെ വില, സ്പെസിഫിക്കേഷനുകൾ, EMI അല്ലെങ്കിൽ ടെസ്റ്റ് ഡ്രൈവ് എന്നിവയിൽ എങ്ങനെ സഹായിക്കണം?"
          : "Hello and welcome to Apex Motors! I am your AI automotive sales consultant. Ask me about vehicle specs, pricing, indicative EMI calculations, or test drive bookings.",
      timestamp: "Just now",
      language: language,
    },
  ]);
  const [inputText, setInputText] = useState("");
  const [recommendedVehicles, setRecommendedVehicles] = useState<Vehicle[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);

  const socketRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const micStreamRef = useRef<MediaStream | null>(null);
  const currentAudioSourceRef = useRef<AudioBufferSourceNode | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animFrameRef = useRef<number | null>(null);

  // Sync global state
  useEffect(() => {
    setGlobalConnectionState(sessionState);
  }, [sessionState, setGlobalConnectionState]);

  // Clean up audio on unmount
  useEffect(() => {
    return () => {
      stopAudioRecording();
      if (socketRef.current) socketRef.current.close();
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    };
  }, []);

  // Initialize or recreate voice session
  const initSession = async (): Promise<string> => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/voice/session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ language, dealership_id: "apex-kerala-01" }),
      });
      const data = await res.json();
      const id = data.data.session_id;
      setSessionId(id);
      return id;
    } catch (err) {
      console.warn("Could not reach backend session endpoint, using local session ID:", err);
      const fallbackId = "session-" + Math.random().toString(36).substring(2, 9);
      setSessionId(fallbackId);
      return fallbackId;
    }
  };

  // Playback base64 WAV audio through Web Audio API
  const playAudioChunk = async (base64Data: string) => {
    try {
      if (!audioContextRef.current) {
        audioContextRef.current = new (window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)();
      }
      if (audioContextRef.current.state === "suspended") {
        await audioContextRef.current.resume();
      }

      // Convert base64 to ArrayBuffer
      const binaryStr = atob(base64Data);
      const len = binaryStr.length;
      const bytes = new Uint8Array(len);
      for (let i = 0; i < len; i++) {
        bytes[i] = binaryStr.charCodeAt(i);
      }

      const audioBuffer = await audioContextRef.current.decodeAudioData(bytes.buffer);
      
      // Stop previous playback if active
      if (currentAudioSourceRef.current) {
        try {
          currentAudioSourceRef.current.stop();
        } catch {
          // ignore already stopped
        }
      }

      const source = audioContextRef.current.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(audioContextRef.current.destination);
      currentAudioSourceRef.current = source;

      setSessionState("speaking");
      source.start();

      // Simulate visualizer amplitude during playback
      let step = 0;
      const interval = setInterval(() => {
        step++;
        setAudioLevel(0.2 + 0.35 * Math.sin(step * 0.4));
      }, 70);

      source.onended = () => {
        clearInterval(interval);
        setAudioLevel(0);
        if (sessionState === "speaking") {
          setSessionState("listening");
        }
      };
    } catch (err) {
      console.error("Audio playback error:", err);
      setSessionState("listening");
    }
  };

  // Start Voice Conversation
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

      // Setup audio analysis for live waveform visualization
      const audioCtx = new (window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)();
      audioContextRef.current = audioCtx;
      const source = audioCtx.createMediaStreamSource(stream);
      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      analyserRef.current = analyser;

      // Monitor microphone volume
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

      setSessionState("connecting");
      const currentSessionId = sessionId || (await initSession());

      // Connect WebSocket
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
          } else if (payload.type === "audio_chunk" && payload.data) {
            await playAudioChunk(payload.data);
          } else if (payload.type === "vehicle_cards" && payload.vehicles) {
            setRecommendedVehicles(payload.vehicles);
          }
        } catch (e) {
          console.error("Error parsing WebSocket message:", e);
        }
      };

      ws.onerror = () => {
        console.warn("WebSocket stream unavailable. Operating in high-reliability REST fallback mode.");
        setSessionState("listening");
      };

      ws.onclose = () => {
        if (sessionState !== "ended" && sessionState !== "idle") {
          setSessionState("idle");
        }
      };
    } catch (err) {
      console.error("Microphone access error:", err);
      setSessionState("failed");
    }
  };

  // Stop Voice Session
  const stopAudioRecording = () => {
    if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
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
    if (currentAudioSourceRef.current) {
      try {
        currentAudioSourceRef.current.stop();
      } catch {
        // ignore
      }
    }
    setSessionState("idle");
    setAudioLevel(0);
  };

  // Handle Interruption
  const handleInterrupt = () => {
    if (currentAudioSourceRef.current) {
      try {
        currentAudioSourceRef.current.stop();
      } catch {
        // ignore
      }
    }
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ type: "interrupt" }));
    }
    setSessionState("interrupted");
    setTimeout(() => {
      setSessionState("listening");
    }, 200);
  };

  // Helper to append message to live transcript
  const addMessage = (sender: "user" | "agent", text: string) => {
    const newMsg: Message = {
      id: Math.random().toString(36).substring(2, 9),
      sender,
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      language,
    };
    setMessages((prev) => [...prev, newMsg]);
  };

  // Handle Typed Chat Submission
  const handleTextSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputText.trim()) return;

    const query = inputText.trim();
    setInputText("");
    addMessage("user", query);

    // If WebSocket is open, send via stream
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

    // Otherwise use REST fallback endpoint
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
      addMessage("agent", data.response_text);

      if (data.recommended_vehicles && data.recommended_vehicles.length > 0) {
        setRecommendedVehicles(data.recommended_vehicles);
      }

      if (data.audio_base64) {
        await playAudioChunk(data.audio_base64);
      } else {
        setSessionState("idle");
      }
    } catch (err) {
      console.error("Text query error:", err);
      addMessage(
        "agent",
        language === "ml"
          ? "ക്ഷമിക്കണം, സെർവറുമായി ബന്ധപ്പെടാൻ സാധിച്ചില്ല. വീണ്ടും ശ്രമിക്കുക."
          : "Apologies, could not reach the automotive server. Please try again."
      );
      setSessionState("idle");
    }
  };

  // Trigger quick prompt
  const handleQuickPrompt = (prompt: string) => {
    setInputText(prompt);
  };

  const quickPrompts =
    language === "ml"
      ? [
          "15 ലക്ഷത്തിൽ താഴെയുള്ള SUV കാണിക്കൂ",
          "Tata Nexon EV യുടെ റേഞ്ചും വിലയും എത്രയാണ്?",
          "10 ലക്ഷം രൂപ ലോണിന് പ്രതിമാസ EMI എത്ര വരും?",
          "അപെക്സ് മോട്ടോഴ്സിൽ ടെസ്റ്റ് ഡ്രൈവ് ബുക്ക് ചെയ്യണം",
        ]
      : [
          "Show me top SUVs under 15 Lakhs with 5-star NCAP",
          "What is the real-world range and price of Tata Nexon EV?",
          "Calculate monthly EMI for ₹10 Lakhs loan at 9.5% interest",
          "Schedule a test drive for Tata Nexon Fearless Plus",
        ];

  return (
    <div className="mx-auto max-w-5xl px-4 py-6 sm:px-6">
      {/* Top Welcome Card */}
      <div className="mb-6 rounded-3xl border border-blue-100 bg-gradient-to-r from-blue-50/60 via-indigo-50/40 to-white p-6 shadow-sm">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className="flex h-2.5 w-2.5 rounded-full bg-blue-600"></span>
              <span className="text-xs font-bold uppercase tracking-wider text-blue-700">
                {language === "ml" ? "ലൈവ് വോയ്‌സ് അസിസ്റ്റന്റ്" : "Voice-First Automotive Sales Assistant"}
              </span>
            </div>
            <h1 className="mt-1 text-2xl sm:text-3xl font-extrabold text-slate-900">
              {language === "ml" ? "നിങ്ങളുടെ സ്വപ്ന വാഹനം കണ്ടെത്താം" : "Discover & Compare Your Next Vehicle"}
            </h1>
            <p className="mt-1 text-sm text-slate-600 max-w-2xl">
              {language === "ml"
                ? "സ്വാഭാവിക മലയാളത്തിലോ ഇംഗ്ലീഷിലോ സംസാരിക്കുക. കൃത്യമായ വില, ടെക്നിക്കൽ സ്പെസിഫിക്കേഷൻസ്, ലോൺ EMI, ടെസ്റ്റ് ഡ്രൈവ് ബുക്കിംഗ് എന്നിവ ഇവിടെ ലഭ്യമാണ്."
                : "Speak naturally in English or Malayalam. Get verified specifications, real pricing, indicative finance calculations, and instant test drive coordination."}
            </p>
          </div>

          <div className="flex items-center space-x-2 rounded-2xl bg-white p-2 shadow-sm border border-slate-200">
            <span className="text-xs font-semibold text-slate-500 pl-2">Language:</span>
            <button
              onClick={() => setLanguage("en")}
              className={`rounded-xl px-3 py-1.5 text-xs font-bold transition ${
                language === "en" ? "bg-blue-600 text-white shadow-sm" : "text-slate-600 hover:bg-slate-100"
              }`}
            >
              English
            </button>
            <button
              onClick={() => setLanguage("ml")}
              className={`rounded-xl px-3 py-1.5 text-xs font-bold transition ${
                language === "ml" ? "bg-blue-600 text-white shadow-sm" : "text-slate-600 hover:bg-slate-100"
              }`}
            >
              മലയാളം
            </button>
          </div>
        </div>
      </div>

      {/* Main Interactive Voice Visualizer Section */}
      <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <AudioVisualizer
          state={sessionState}
          audioLevel={audioLevel}
          language={language}
          onToggleMic={sessionState === "idle" || sessionState === "ended" || sessionState === "failed" ? startVoice : stopAudioRecording}
          onInterrupt={handleInterrupt}
        />

        {/* Quick Action Chips */}
        <div className="mt-4 border-t border-slate-100 pt-4">
          <p className="text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">
            {language === "ml" ? "വേഗത്തിലുള്ള നിർദ്ദേശങ്ങൾ:" : "Suggested Questions:"}
          </p>
          <div className="flex flex-wrap gap-2">
            {quickPrompts.map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => handleQuickPrompt(prompt)}
                className="rounded-full border border-slate-200 bg-slate-50 px-3.5 py-1.5 text-xs font-medium text-slate-700 hover:border-blue-300 hover:bg-blue-50/50 hover:text-blue-700 transition active:scale-95 text-left"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Vehicle Recommendation Cards (If Returned) */}
      {recommendedVehicles.length > 0 && (
        <div className="mt-8">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-slate-900">
                {language === "ml" ? "ശുപാർശ ചെയ്യുന്ന വാഹനങ്ങൾ" : "Recommended Vehicles"}
              </h2>
              <p className="text-xs text-slate-500">
                {language === "ml"
                  ? "Apex Motors-ന്റെ പരിശോധിച്ച കാറ്റലോഗിൽ നിന്നുള്ള കൃത്യമായ വിവരങ്ങൾ"
                  : "Verified vehicle models from Apex Motors inventory"}
              </p>
            </div>
            <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700 border border-blue-200">
              {recommendedVehicles.length} {language === "ml" ? "മോഡലുകൾ" : "Options"}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {recommendedVehicles.map((vehicle) => (
              <VehicleCard
                key={vehicle.id}
                vehicle={vehicle}
                language={language}
                onAction={(action, v) => {
                  if (action === "test_drive") {
                    setInputText(
                      language === "ml"
                        ? `${v.make} ${v.model}-ന്റെ ടെസ്റ്റ് ഡ്രൈവ് എനിക്ക് ബുക്ക് ചെയ്യണം`
                        : `I would like to book a test drive for the ${v.make} ${v.model}`
                    );
                  } else if (action === "finance") {
                    setInputText(
                      language === "ml"
                        ? `${v.make} ${v.model}-ന്റെ EMI എത്രയാണ്? 20% ഡൗൺപേയ്മെന്റും 5 വർഷവും`
                        : `What is the monthly EMI for ${v.make} ${v.model} with 20% down payment over 5 years?`
                    );
                  }
                }}
              />
            ))}
          </div>
        </div>
      )}

      {/* Live Transcript & Conversation History */}
      <div className="mt-8 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
          <div className="flex items-center space-x-2">
            <span className="h-2 w-2 rounded-full bg-emerald-500"></span>
            <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
              {language === "ml" ? "സംഭാഷണ രേഖ (Live Transcript)" : "Live Conversation Transcript"}
            </h3>
          </div>
          <span className="text-xs text-slate-400 font-medium">{messages.length} messages</span>
        </div>

        <div className="max-h-80 overflow-y-auto space-y-4 pr-1">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex items-start space-x-3 ${msg.sender === "user" ? "flex-row-reverse space-x-reverse" : ""}`}
            >
              <div
                className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold ${
                  msg.sender === "user"
                    ? "bg-slate-900 text-white"
                    : "bg-gradient-to-tr from-blue-600 to-indigo-600 text-white shadow-sm"
                }`}
              >
                {msg.sender === "user" ? "You" : "AI"}
              </div>

              <div
                className={`max-w-xl rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                  msg.sender === "user"
                    ? "bg-blue-600 text-white shadow-sm rounded-tr-none"
                    : "bg-slate-50 text-slate-800 border border-slate-100 rounded-tl-none"
                }`}
              >
                <p>{msg.text}</p>
                <span
                  className={`block mt-1 text-[10px] ${
                    msg.sender === "user" ? "text-blue-200 text-right" : "text-slate-400"
                  }`}
                >
                  {msg.timestamp}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Typed Chat Fallback Bar */}
        <form onSubmit={handleTextSubmit} className="mt-5 flex items-center space-x-2 border-t border-slate-100 pt-4">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder={
              language === "ml"
                ? "ടൈപ്പ് ചെയ്യുക അല്ലെങ്കിൽ മൈക്രോഫോൺ ഉപയോഗിക്കുക (ഉദാഹരണം: Nexon EV യുടെ റേഞ്ച് എത്രയാണ്?)..."
                : "Type your query or use voice (e.g. Compare Tata Nexon and Creta, calculate EMI)..."
            }
            className="flex-1 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 placeholder-slate-400 focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-100 transition"
          />
          <button
            type="submit"
            disabled={!inputText.trim()}
            className="flex h-11 items-center justify-center rounded-2xl bg-blue-600 px-5 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 active:scale-95 disabled:opacity-40 disabled:pointer-events-none transition"
          >
            {language === "ml" ? "അയക്കുക" : "Send"}
          </button>
        </form>
      </div>
    </div>
  );
};
