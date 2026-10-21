"use client";

import React, { useState } from "react";

interface MemoryPanelProps {
  language: "en" | "ml";
}

interface MemoryEntry {
  id: string;
  category: "User Profile" | "Preferences" | "Context Checkpoint" | "Task Decisions";
  key: string;
  value: string;
  timestamp: string;
}

export const MemoryPanel: React.FC<MemoryPanelProps> = ({ language }) => {
  const [search, setSearch] = useState("");
  const [newKey, setNewKey] = useState("");
  const [newValue, setNewValue] = useState("");
  const [newCategory, setNewCategory] = useState<"User Profile" | "Preferences" | "Context Checkpoint" | "Task Decisions">("Preferences");
  const [showAddForm, setShowAddForm] = useState(false);

  const [memoryEntries, setMemoryEntries] = useState<MemoryEntry[]>([
    {
      id: "mem-1",
      category: "User Profile",
      key: "preferred_name",
      value: "Rahul Nambiar",
      timestamp: "2026-10-21 09:15"
    },
    {
      id: "mem-2",
      category: "Preferences",
      key: "language_mode",
      value: "Bilingual (English + Malayalam code-switching)",
      timestamp: "2026-10-21 09:16"
    },
    {
      id: "mem-3",
      category: "Preferences",
      key: "research_focus",
      value: "Multimodal AI reasoning, reducing-balance amortized finance",
      timestamp: "2026-10-21 09:20"
    },
    {
      id: "mem-4",
      category: "Context Checkpoint",
      key: "active_task_graph",
      value: "LangGraph 3-phase execution plan for autonomous benchmarks",
      timestamp: "2026-10-21 09:35"
    },
    {
      id: "mem-5",
      category: "Task Decisions",
      key: "dpdp_compliance_enforced",
      value: "Strict zero PII retention without explicit consent",
      timestamp: "2026-10-21 09:40"
    }
  ]);

  const handleAddMemory = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newKey.trim() || !newValue.trim()) return;

    const newEntry: MemoryEntry = {
      id: `mem-${Date.now()}`,
      category: newCategory,
      key: newKey.trim(),
      value: newValue.trim(),
      timestamp: new Date().toISOString().replace("T", " ").substring(0, 16)
    };

    setMemoryEntries([newEntry, ...memoryEntries]);
    setNewKey("");
    setNewValue("");
    setShowAddForm(false);
  };

  const handleDelete = (id: string) => {
    setMemoryEntries(memoryEntries.filter((m) => m.id !== id));
  };

  const filtered = memoryEntries.filter(
    (m) =>
      m.key.toLowerCase().includes(search.toLowerCase()) ||
      m.value.toLowerCase().includes(search.toLowerCase()) ||
      m.category.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="border-b border-slate-200/80 pb-5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900 sm:text-2xl">
            {language === "ml" ? "ഏജന്റ് മെമ്മറി & കോൺടെക്സ്റ്റ്" : "Persistent Vector & Session Memory"}
          </h1>
          <p className="mt-1 text-xs text-slate-500">
            {language === "ml"
              ? "ക്രോസ്-സെഷൻ ഓർമ്മകൾ, പ്രൊഫൈൽ വിവരങ്ങൾ, സ്ഥിരപ്പെടുത്തിയ തീരുമാനങ്ങൾ"
              : "Inspect, manage, and query long-term semantic embeddings and active session memory"}
          </p>
        </div>

        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="rounded-lg border border-blue-600 bg-blue-600 px-3.5 py-2 text-xs font-semibold text-white shadow-xs hover:bg-blue-700 transition active:scale-98"
        >
          {showAddForm ? "Cancel" : "+ Add Memory Key"}
        </button>
      </div>

      {/* KPI Stats */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="rounded-xl border border-slate-200/90 bg-white p-4 shadow-xs">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">Total Entries</span>
          <p className="mt-1 text-2xl font-bold font-mono text-slate-900">{memoryEntries.length}</p>
          <span className="text-[10px] text-slate-500">Across 4 categories</span>
        </div>
        <div className="rounded-xl border border-slate-200/90 bg-white p-4 shadow-xs">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">Vector Storage</span>
          <p className="mt-1 text-2xl font-bold font-mono text-slate-900">Qdrant</p>
          <span className="text-[10px] text-blue-600 font-semibold">384-Dim Embeddings</span>
        </div>
        <div className="rounded-xl border border-slate-200/90 bg-white p-4 shadow-xs">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">Recall Latency</span>
          <p className="mt-1 text-2xl font-bold font-mono text-slate-900">14.2 ms</p>
          <span className="text-[10px] text-blue-600 font-semibold">Sub-20ms Indexed</span>
        </div>
        <div className="rounded-xl border border-slate-200/90 bg-white p-4 shadow-xs">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">Persistence State</span>
          <p className="mt-1 text-2xl font-bold font-mono text-slate-900">Active</p>
          <span className="text-[10px] text-slate-500">Zero session loss</span>
        </div>
      </div>

      {/* Add Form */}
      {showAddForm && (
        <form onSubmit={handleAddMemory} className="mt-6 rounded-2xl border border-blue-200 bg-[#f0f7ff] p-5 shadow-xs space-y-4 text-xs">
          <h3 className="font-bold text-slate-900 text-sm">Add New Memory Key</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div>
              <label className="block text-slate-600 mb-1 font-medium">Category</label>
              <select
                value={newCategory}
                onChange={(e) => setNewCategory(e.target.value as any)}
                className="w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-xs focus:border-blue-600 focus:ring-1 focus:ring-blue-100 focus:outline-none"
              >
                <option value="Preferences">Preferences</option>
                <option value="User Profile">User Profile</option>
                <option value="Context Checkpoint">Context Checkpoint</option>
                <option value="Task Decisions">Task Decisions</option>
              </select>
            </div>
            <div>
              <label className="block text-slate-600 mb-1 font-medium">Key Identifier</label>
              <input
                type="text"
                required
                placeholder="e.g. preferred_model_depth"
                value={newKey}
                onChange={(e) => setNewKey(e.target.value)}
                className="w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-xs focus:border-blue-600 focus:ring-1 focus:ring-blue-100 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-slate-600 mb-1 font-medium">Value Content</label>
              <input
                type="text"
                required
                placeholder="e.g. Dense technical citations with links"
                value={newValue}
                onChange={(e) => setNewValue(e.target.value)}
                className="w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-xs focus:border-blue-600 focus:ring-1 focus:ring-blue-100 focus:outline-none"
              />
            </div>
          </div>
          <div className="flex justify-end space-x-2">
            <button
              type="button"
              onClick={() => setShowAddForm(false)}
              className="rounded-md border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-700 hover:bg-slate-50 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="rounded-md border border-blue-600 bg-blue-600 px-4 py-1.5 text-xs font-semibold text-white hover:bg-blue-700 shadow-xs transition"
            >
              Save to Memory
            </button>
          </div>
        </form>
      )}

      {/* Search and Table */}
      <div className="mt-8 rounded-2xl border border-slate-200/90 bg-white p-6 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-100 pb-4 mb-4">
          <h2 className="text-sm font-bold text-slate-900 tracking-tight">
            Persisted Memory Records
          </h2>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search keys, values, or category..."
            className="rounded-md border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-900 placeholder-slate-400 focus:border-blue-600 focus:ring-1 focus:ring-blue-100 focus:outline-none w-64"
          />
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-100 text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                <th className="py-2.5 px-3">Category</th>
                <th className="py-2.5 px-3">Key</th>
                <th className="py-2.5 px-3">Persisted Value</th>
                <th className="py-2.5 px-3">Timestamp</th>
                <th className="py-2.5 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map((item) => (
                <tr key={item.id} className="hover:bg-slate-50/70 transition">
                  <td className="py-3 px-3">
                    <span className="rounded border border-blue-200 bg-blue-50/70 px-2 py-0.5 text-[10px] font-medium text-blue-800">
                      {item.category}
                    </span>
                  </td>
                  <td className="py-3 px-3 font-mono font-semibold text-slate-900">
                    {item.key}
                  </td>
                  <td className="py-3 px-3 text-slate-700 max-w-md">
                    {item.value}
                  </td>
                  <td className="py-3 px-3 font-mono text-[11px] text-slate-400">
                    {item.timestamp}
                  </td>
                  <td className="py-3 px-3 text-right">
                    <button
                      onClick={() => handleDelete(item.id)}
                      className="text-slate-400 hover:text-rose-600 transition text-[11px]"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
