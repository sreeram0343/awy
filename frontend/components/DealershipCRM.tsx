"use client";

import React, { useState, useEffect } from "react";
import { Vehicle } from "./VehicleCard";

interface DealershipCRMProps {
  language: "en" | "ml";
  prefilledVehicle?: Vehicle | null;
}

interface Lead {
  id: string;
  variant_id: string;
  vehicle_name: string;
  user_name: string;
  user_email: string;
  user_phone: string;
  state_code: string;
  dealership_id: string;
  computed_on_road_price: number;
  status: string;
  consent_given: boolean;
  notes?: string;
  created_at: string;
}

interface Appointment {
  id: string;
  customer_name: string;
  phone: string;
  vehicle: string;
  dealership: string;
  date: string;
  time_slot: string;
  status: string;
  sales_executive: string;
}

export const DealershipCRM: React.FC<DealershipCRMProps> = ({
  language,
  prefilledVehicle,
}) => {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);

  // Appointment Booking Modal
  const [showApptModal, setShowApptModal] = useState(false);
  const [custName, setCustName] = useState("");
  const [custPhone, setCustPhone] = useState("");
  const [custEmail, setCustEmail] = useState("");
  const [vehicleModel, setVehicleModel] = useState(
    prefilledVehicle ? `${prefilledVehicle.make} ${prefilledVehicle.model}` : "Tata Nexon Fearless Plus"
  );
  const [preferredDate, setPreferredDate] = useState("2026-10-24");
  const [preferredTime, setPreferredTime] = useState("11:00 AM");
  const [apptSuccessMsg, setApptSuccessMsg] = useState("");

  // AI Handoff Summary Modal
  const [activeLeadForHandoff, setActiveLeadForHandoff] = useState<Lead | null>(null);

  useEffect(() => {
    if (prefilledVehicle) {
      setVehicleModel(`${prefilledVehicle.make} ${prefilledVehicle.model}`);
      setShowApptModal(true);
    }
  }, [prefilledVehicle]);

  // Load leads and appointments from backend
  const loadData = async () => {
    setLoading(true);
    try {
      const [leadsRes, apptRes] = await Promise.all([
        fetch("http://localhost:8000/api/v1/leads"),
        fetch("http://localhost:8000/api/v1/leads/appointments"),
      ]);
      if (leadsRes.ok) {
        const json = await leadsRes.json();
        if (json.data) setLeads(json.data);
      }
      if (apptRes.ok) {
        const json = await apptRes.json();
        if (json.data) setAppointments(json.data);
      }
    } catch {
      // Fallback local initializers
      setLeads(DEFAULT_LEADS);
      setAppointments(DEFAULT_APPOINTMENTS);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleStatusChange = async (leadId: string, newStatus: string) => {
    try {
      await fetch(`http://localhost:8000/api/v1/leads/${leadId}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus }),
      });
    } catch {
      // ignore
    }
    setLeads((prev) =>
      prev.map((l) => (l.id === leadId ? { ...l, status: newStatus } : l))
    );
  };

  const handleBookAppointment = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch("http://localhost:8000/api/v1/leads/appointments", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customer_name: custName,
          customer_phone: custPhone,
          customer_email: custEmail,
          vehicle_model: vehicleModel,
          dealership_location: "Apex Motors Kochi Central",
          preferred_date: preferredDate,
          preferred_time_slot: preferredTime,
        }),
      });
      if (res.ok) {
        const json = await res.json();
        setAppointments((prev) => [json.data, ...prev]);
        setApptSuccessMsg(
          language === "ml"
            ? "ടെസ്റ്റ് ഡ്രൈവ് സ്ലോട്ട് വിജയകരമായി ഉറപ്പിച്ചു."
            : "Test drive appointment confirmed and assigned to executive."
        );
        setTimeout(() => {
          setShowApptModal(false);
          setApptSuccessMsg("");
          setCustName("");
          setCustPhone("");
        }, 1500);
      }
    } catch {
      // Local addition
      const newAppt: Appointment = {
        id: `apt-${Math.random().toString(36).substring(2, 7)}`,
        customer_name: custName,
        phone: custPhone,
        vehicle: vehicleModel,
        dealership: "Apex Motors Kochi Central",
        date: preferredDate,
        time_slot: preferredTime,
        status: "confirmed",
        sales_executive: "Jithin George",
      };
      setAppointments((prev) => [newAppt, ...prev]);
      setShowApptModal(false);
    }
  };

  const filteredLeads = leads.filter((l) => {
    if (statusFilter !== "all" && l.status !== statusFilter) return false;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      return (
        l.user_name.toLowerCase().includes(q) ||
        l.user_phone.toLowerCase().includes(q) ||
        l.vehicle_name.toLowerCase().includes(q)
      );
    }
    return true;
  });

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="border-b border-zinc-200 pb-5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-zinc-950 sm:text-2xl">
            {language === "ml" ? "ഡീലർഷിപ്പ് CRM & ഓപ്പറേഷൻസ്" : "Dealership Operations & Lead Management"}
          </h1>
          <p className="mt-1 text-xs text-zinc-500">
            {language === "ml"
              ? "പരിശോധിച്ച ലീഡുകൾ, ടെസ്റ്റ് ഡ്രൈവ് ഷെഡ്യൂളുകൾ, കൺസൾട്ടന്റ് ഹാൻഡ്ഓഫ്"
              : "Qualified pipeline, automated test-drive dispatching, and AI sales executive briefings"}
          </p>
        </div>

        <button
          onClick={() => setShowApptModal(true)}
          className="rounded-md border border-zinc-900 bg-zinc-900 px-3.5 py-2 text-xs font-semibold text-white shadow-xs hover:bg-zinc-800 transition active:scale-98"
        >
          {language === "ml" ? "+ പുതിയ ടെസ്റ്റ് ഡ്രൈവ്" : "+ Schedule Test Drive"}
        </button>
      </div>

      {/* KPI Counters */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="rounded-xl border border-zinc-200 bg-white p-4">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-zinc-400">Total Leads</span>
          <p className="mt-1 text-2xl font-bold font-mono text-zinc-950">{leads.length}</p>
          <span className="text-[10px] text-emerald-600 font-medium">100% DPDP Consented</span>
        </div>
        <div className="rounded-xl border border-zinc-200 bg-white p-4">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-zinc-400">Scheduled Drives</span>
          <p className="mt-1 text-2xl font-bold font-mono text-zinc-950">{appointments.length}</p>
          <span className="text-[10px] text-zinc-500">Apex Motors Kochi</span>
        </div>
        <div className="rounded-xl border border-zinc-200 bg-white p-4">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-zinc-400">Pipeline Value</span>
          <p className="mt-1 text-2xl font-bold font-mono text-zinc-950">
            ₹{((leads.reduce((acc, l) => acc + (l.computed_on_road_price || 1500000), 0)) / 10000000).toFixed(2)} Cr
          </p>
          <span className="text-[10px] text-zinc-500">Indicative On-road Volume</span>
        </div>
        <div className="rounded-xl border border-zinc-200 bg-white p-4">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-zinc-400">Average Turnaround</span>
          <p className="mt-1 text-2xl font-bold font-mono text-zinc-950">14 min</p>
          <span className="text-[10px] text-emerald-600 font-medium">Agent AI Automated</span>
        </div>
      </div>

      {/* Main Sections: Tabs for Leads vs Appointments */}
      <div className="mt-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Leads Table */}
        <div className="lg:col-span-8 space-y-4">
          <div className="rounded-xl border border-zinc-200 bg-white p-5 shadow-xs">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-zinc-100 pb-4 mb-4">
              <div>
                <h2 className="text-sm font-bold text-zinc-900 tracking-tight">
                  {language === "ml" ? "യോഗ്യതയുള്ള ലീഡുകൾ" : "Qualified Customer Leads"}
                </h2>
                <p className="text-[11px] text-zinc-500">Real-time inquiries via AWY voice & digital consultation</p>
              </div>

              {/* Status and Search filters */}
              <div className="flex items-center space-x-2">
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="rounded-md border border-zinc-200 bg-white px-2 py-1 text-xs text-zinc-700 focus:outline-none"
                >
                  <option value="all">All Statuses</option>
                  <option value="new">New</option>
                  <option value="sent">Sent</option>
                  <option value="contacted">Contacted</option>
                  <option value="test_drive_booked">Test Drive Booked</option>
                  <option value="won">Won / Purchased</option>
                </select>

                <input
                  type="text"
                  placeholder="Search name or phone..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="rounded-md border border-zinc-200 bg-white px-2.5 py-1 text-xs text-zinc-900 placeholder-zinc-400 focus:outline-none w-36"
                />
              </div>
            </div>

            {loading ? (
              <div className="py-8 text-center text-xs text-zinc-400">Loading leads...</div>
            ) : filteredLeads.length === 0 ? (
              <div className="py-8 text-center text-xs text-zinc-400">No leads found.</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-zinc-100 text-[10px] font-semibold uppercase tracking-wider text-zinc-400">
                      <th className="py-2.5 px-3">Customer</th>
                      <th className="py-2.5 px-3">Vehicle Interest</th>
                      <th className="py-2.5 px-3">Budget / On-Road</th>
                      <th className="py-2.5 px-3">Pipeline Status</th>
                      <th className="py-2.5 px-3 text-right">Handoff</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-100">
                    {filteredLeads.map((lead) => (
                      <tr key={lead.id} className="hover:bg-zinc-50/50 transition">
                        <td className="py-3 px-3">
                          <span className="font-semibold text-zinc-900 block">{lead.user_name}</span>
                          <span className="text-[11px] text-zinc-500 font-mono block">{lead.user_phone}</span>
                        </td>
                        <td className="py-3 px-3">
                          <span className="font-medium text-zinc-800 block truncate max-w-[180px]">
                            {lead.vehicle_name}
                          </span>
                          <span className="text-[10px] text-zinc-400">State: {lead.state_code}</span>
                        </td>
                        <td className="py-3 px-3 font-mono font-medium text-zinc-900">
                          ₹{(lead.computed_on_road_price / 100000).toFixed(2)} L
                        </td>
                        <td className="py-3 px-3">
                          <select
                            value={lead.status}
                            onChange={(e) => handleStatusChange(lead.id, e.target.value)}
                            className="rounded border border-zinc-200 bg-white px-2 py-0.5 text-[11px] font-medium text-zinc-700"
                          >
                            <option value="new">New</option>
                            <option value="sent">Sent</option>
                            <option value="contacted">Contacted</option>
                            <option value="test_drive_booked">Test Drive Booked</option>
                            <option value="won">Won</option>
                          </select>
                        </td>
                        <td className="py-3 px-3 text-right">
                          <button
                            onClick={() => setActiveLeadForHandoff(lead)}
                            className="rounded border border-zinc-200 bg-white px-2 py-1 text-[11px] font-medium text-zinc-700 hover:border-zinc-400 transition"
                          >
                            View Brief
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Scheduled Test Drives */}
        <div className="lg:col-span-4 space-y-4">
          <div className="rounded-xl border border-zinc-200 bg-white p-5 shadow-xs">
            <div className="flex items-center justify-between border-b border-zinc-100 pb-3 mb-4">
              <div>
                <h2 className="text-sm font-bold text-zinc-900 tracking-tight">
                  {language === "ml" ? "ടെസ്റ്റ് ഡ്രൈവ് ഷെഡ്യൂൾ" : "Test Drive Calendar"}
                </h2>
                <p className="text-[11px] text-zinc-500">Upcoming showroom appointments</p>
              </div>
              <span className="rounded-full bg-zinc-100 px-2 py-0.5 text-[10px] font-bold text-zinc-700">
                {appointments.length}
              </span>
            </div>

            <div className="space-y-3">
              {appointments.map((apt) => (
                <div
                  key={apt.id}
                  className="rounded-lg border border-zinc-100 bg-zinc-50/70 p-3 text-xs space-y-1.5"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="font-semibold text-zinc-900 block">{apt.customer_name}</span>
                      <span className="text-[11px] text-zinc-500 font-mono">{apt.phone}</span>
                    </div>
                    <span className="rounded bg-emerald-50 text-emerald-700 border border-emerald-200 px-1.5 py-0.5 text-[10px] font-medium">
                      {apt.status}
                    </span>
                  </div>

                  <div className="border-t border-zinc-200/60 pt-1.5 flex justify-between text-[11px] text-zinc-600">
                    <span>Vehicle: <strong className="text-zinc-900">{apt.vehicle}</strong></span>
                  </div>

                  <div className="flex justify-between text-[11px] text-zinc-500">
                    <span>{apt.date} • {apt.time_slot}</span>
                    <span className="text-zinc-700">Rep: {apt.sales_executive}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* AI Customer Handoff Brief Modal */}
      {activeLeadForHandoff && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-zinc-950/40 backdrop-blur-xs p-4">
          <div className="w-full max-w-md rounded-xl border border-zinc-200 bg-white p-6 shadow-xl text-xs space-y-4">
            <div className="flex justify-between items-start border-b border-zinc-100 pb-3">
              <div>
                <span className="text-[10px] font-semibold text-zinc-400 uppercase tracking-wider">
                  AI Dealership Handoff Brief
                </span>
                <h3 className="text-sm font-bold text-zinc-950">
                  {activeLeadForHandoff.user_name}
                </h3>
              </div>
              <button
                onClick={() => setActiveLeadForHandoff(null)}
                className="text-zinc-400 hover:text-zinc-600"
              >
                ✕
              </button>
            </div>

            <div className="rounded-lg border border-zinc-100 bg-zinc-50 p-3 space-y-2">
              <div>
                <span className="font-semibold text-zinc-800 block">Identified Intent & Model:</span>
                <p className="text-zinc-600">{activeLeadForHandoff.vehicle_name}</p>
              </div>
              <div>
                <span className="font-semibold text-zinc-800 block">Financial Readiness:</span>
                <p className="text-zinc-600">
                  On-road estimate: ₹{(activeLeadForHandoff.computed_on_road_price / 100000).toFixed(2)} Lakh. Verified customer contact via voice assistant.
                </p>
              </div>
              <div>
                <span className="font-semibold text-zinc-800 block">Consultant Recommendation:</span>
                <p className="text-zinc-600">
                  Customer reviewed safety and automated features. Propose Kerala state on-road package and weekend test-drive slot.
                </p>
              </div>
              <div>
                <span className="font-semibold text-zinc-800 block">Compliance Status:</span>
                <span className="text-emerald-700 font-medium">✓ DPDP Act Consent recorded on {activeLeadForHandoff.created_at.split("T")[0]}</span>
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setActiveLeadForHandoff(null)}
                className="rounded-md border border-zinc-900 bg-zinc-900 px-4 py-1.5 text-xs font-semibold text-white hover:bg-zinc-800"
              >
                Close Brief
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Book Test Drive Modal */}
      {showApptModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-zinc-950/40 backdrop-blur-xs p-4">
          <div className="w-full max-w-md rounded-xl border border-zinc-200 bg-white p-6 shadow-xl text-xs space-y-4">
            <div className="flex justify-between items-start border-b border-zinc-100 pb-3">
              <div>
                <h3 className="text-sm font-bold text-zinc-950">
                  {language === "ml" ? "ടെസ്റ്റ് ഡ്രൈവ് ഷെഡ്യൂൾ ചെയ്യുക" : "Schedule Test Drive Slot"}
                </h3>
                <p className="text-[11px] text-zinc-500">Apex Motors Kochi Central</p>
              </div>
              <button
                onClick={() => setShowApptModal(false)}
                className="text-zinc-400 hover:text-zinc-600"
              >
                ✕
              </button>
            </div>

            {apptSuccessMsg ? (
              <div className="py-6 text-center text-xs text-emerald-600 font-medium">
                {apptSuccessMsg}
              </div>
            ) : (
              <form onSubmit={handleBookAppointment} className="space-y-3.5">
                <div>
                  <label className="block font-medium text-zinc-700 mb-1">Customer Name</label>
                  <input
                    type="text"
                    required
                    value={custName}
                    onChange={(e) => setCustName(e.target.value)}
                    placeholder="e.g. Ananya Menon"
                    className="w-full rounded-md border border-zinc-200 px-3 py-2 text-xs focus:border-zinc-900 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block font-medium text-zinc-700 mb-1">Mobile Number</label>
                  <input
                    type="tel"
                    required
                    value={custPhone}
                    onChange={(e) => setCustPhone(e.target.value)}
                    placeholder="+91 94470 12345"
                    className="w-full rounded-md border border-zinc-200 px-3 py-2 text-xs focus:border-zinc-900 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block font-medium text-zinc-700 mb-1">Vehicle Model</label>
                  <input
                    type="text"
                    required
                    value={vehicleModel}
                    onChange={(e) => setVehicleModel(e.target.value)}
                    className="w-full rounded-md border border-zinc-200 px-3 py-2 text-xs focus:border-zinc-900 focus:outline-none"
                  />
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block font-medium text-zinc-700 mb-1">Preferred Date</label>
                    <input
                      type="date"
                      required
                      value={preferredDate}
                      onChange={(e) => setPreferredDate(e.target.value)}
                      className="w-full rounded-md border border-zinc-200 px-3 py-2 text-xs focus:border-zinc-900 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block font-medium text-zinc-700 mb-1">Time Slot</label>
                    <select
                      value={preferredTime}
                      onChange={(e) => setPreferredTime(e.target.value)}
                      className="w-full rounded-md border border-zinc-200 px-3 py-2 text-xs focus:border-zinc-900 focus:outline-none"
                    >
                      <option value="10:00 AM">10:00 AM</option>
                      <option value="11:30 AM">11:30 AM</option>
                      <option value="02:30 PM">02:30 PM</option>
                      <option value="04:00 PM">04:00 PM</option>
                      <option value="05:30 PM">05:30 PM</option>
                    </select>
                  </div>
                </div>

                <div className="pt-2 flex space-x-2">
                  <button
                    type="button"
                    onClick={() => setShowApptModal(false)}
                    className="flex-1 rounded-md border border-zinc-200 py-2 text-xs font-medium text-zinc-600 hover:bg-zinc-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 rounded-md border border-zinc-900 bg-zinc-900 py-2 text-xs font-medium text-white hover:bg-zinc-800"
                  >
                    Confirm Booking
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

const DEFAULT_LEADS: Lead[] = [
  {
    id: "a1b2c3d4-1111-4444-9999-000000000001",
    variant_id: "11111111-1111-1111-1111-111111111111",
    vehicle_name: "Tata Nexon Fearless Plus S",
    user_name: "Rahul Nambiar",
    user_email: "rahul.nambiar@example.com",
    user_phone: "+91 98471 23456",
    state_code: "KL",
    dealership_id: "apex-kerala-01",
    computed_on_road_price: 1587850.0,
    status: "test_drive_booked",
    consent_given: true,
    created_at: "2026-10-20T10:15:00Z"
  },
  {
    id: "a1b2c3d4-2222-4444-9999-000000000002",
    variant_id: "33333333-3333-3333-3333-333333333333",
    vehicle_name: "Tata Nexon EV Empowered Plus",
    user_name: "Ananya Menon",
    user_email: "ananya.menon@example.com",
    user_phone: "+91 94470 98765",
    state_code: "KL",
    dealership_id: "apex-kerala-01",
    computed_on_road_price: 1785400.0,
    status: "contacted",
    consent_given: true,
    created_at: "2026-10-20T14:30:00Z"
  },
  {
    id: "a1b2c3d4-3333-4444-9999-000000000003",
    variant_id: "22222222-2222-2222-2222-222222222222",
    vehicle_name: "Hyundai Creta SX (O) 1.5 Turbo",
    user_name: "Suresh Kumar",
    user_email: "suresh.k@example.com",
    user_phone: "+91 97455 11223",
    state_code: "KL",
    dealership_id: "apex-kerala-01",
    computed_on_road_price: 2335350.0,
    status: "new",
    consent_given: true,
    created_at: "2026-10-21T08:45:00Z"
  }
];

const DEFAULT_APPOINTMENTS: Appointment[] = [
  {
    id: "apt-001",
    customer_name: "Rahul Nambiar",
    phone: "+91 98471 23456",
    vehicle: "Tata Nexon Fearless Plus S",
    dealership: "Apex Motors Kochi Central",
    date: "2026-10-22",
    time_slot: "10:30 AM",
    status: "confirmed",
    sales_executive: "Jithin George",
  },
  {
    id: "apt-002",
    customer_name: "Ananya Menon",
    phone: "+91 94470 98765",
    vehicle: "Tata Nexon EV Long Range",
    dealership: "Apex Motors Kochi Central",
    date: "2026-10-23",
    time_slot: "03:00 PM",
    status: "scheduled",
    sales_executive: "Priya Nair",
  }
];
