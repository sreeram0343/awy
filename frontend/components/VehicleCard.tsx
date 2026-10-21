"use client";

import React from "react";

export interface Vehicle {
  id: string;
  make: string;
  model: string;
  variant: string;
  category: string;
  body_type?: string;
  fuel_type: string;
  transmission: string;
  ex_showroom_price: number;
  ncap_rating?: number;
  mileage_kpl?: number;
  ev_range_km?: number;
  seating_capacity?: number;
  engine_capacity_cc?: number;
  battery_capacity_kwh?: number;
  airbags_count?: number;
  ground_clearance_mm?: number;
  boot_space_litres?: number;
  warranty_years?: number;
  key_features?: string[];
  verified_source?: string;
}

interface VehicleCardProps {
  vehicle: Vehicle;
  onAction?: (action: "test_drive" | "finance" | "details", vehicle: Vehicle) => void;
  language: "en" | "ml";
  isComparing?: boolean;
  onToggleCompare?: (vehicle: Vehicle) => void;
}

export const VehicleCard: React.FC<VehicleCardProps> = ({
  vehicle,
  onAction,
  language,
  isComparing = false,
  onToggleCompare,
}) => {
  const formatINR = (amount: number) => {
    const lakhs = amount / 100000;
    return `₹${lakhs.toFixed(2)} Lakh`;
  };

  return (
    <div className="group relative flex flex-col justify-between rounded-xl border border-zinc-200/90 bg-white p-5 shadow-xs transition-all hover:border-zinc-400 hover:shadow-sm">
      {/* Top Header & Badges */}
      <div>
        <div className="flex items-start justify-between gap-2">
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-zinc-500">
                {vehicle.make}
              </span>
              <span className="text-zinc-300">•</span>
              <span className="rounded border border-zinc-200 bg-zinc-50 px-1.5 py-0.2 text-[10px] font-medium text-zinc-600">
                {vehicle.category}
              </span>
            </div>
            <h3 className="mt-1 text-base font-semibold text-zinc-950 group-hover:text-zinc-800 transition">
              {vehicle.model}
            </h3>
            <p className="text-xs text-zinc-500 font-normal">{vehicle.variant}</p>
          </div>

          <div className="flex flex-col items-end gap-1.5">
            {vehicle.ncap_rating && (
              <div className="flex items-center space-x-1 rounded border border-zinc-200 bg-zinc-50 px-2 py-0.5 text-xs font-semibold text-zinc-800">
                <span>{vehicle.ncap_rating}★</span>
                <span className="text-[10px] text-zinc-400 uppercase">NCAP</span>
              </div>
            )}
            {onToggleCompare && (
              <label className="flex items-center space-x-1.5 text-[11px] text-zinc-500 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={isComparing}
                  onChange={() => onToggleCompare(vehicle)}
                  className="h-3.5 w-3.5 rounded border-zinc-300 text-zinc-900 focus:ring-0 cursor-pointer"
                />
                <span>{language === "ml" ? "താരതമ്യം" : "Compare"}</span>
              </label>
            )}
          </div>
        </div>

        {/* Pricing Segment */}
        <div className="mt-4 rounded-lg border border-zinc-100 bg-zinc-50/70 p-3">
          <span className="text-[10px] font-medium tracking-wide uppercase text-zinc-500 block">
            {language === "ml" ? "എക്സ്-ഷോറൂം വില" : "Ex-Showroom Price"}
          </span>
          <div className="mt-0.5 flex items-baseline justify-between">
            <span className="text-lg font-bold font-mono tracking-tight text-zinc-950">
              {formatINR(vehicle.ex_showroom_price)}
            </span>
            <span className="text-[10px] text-zinc-400">Verified Kerala baseline</span>
          </div>
        </div>

        {/* Specs Grid */}
        <div className="mt-3.5 grid grid-cols-2 gap-2 text-xs">
          <div className="rounded border border-zinc-100 bg-white p-2">
            <span className="block text-[10px] text-zinc-400 font-medium">
              {language === "ml" ? "ഇന്ധനം & ഗിയർബോക്സ്" : "Powertrain"}
            </span>
            <span className="mt-0.5 block font-medium text-zinc-800 truncate">
              {vehicle.fuel_type} • {vehicle.transmission}
            </span>
          </div>

          <div className="rounded border border-zinc-100 bg-white p-2">
            <span className="block text-[10px] text-zinc-400 font-medium">
              {vehicle.ev_range_km
                ? language === "ml" ? "സാക്ഷ്യപ്പെടുത്തിയ റേഞ്ച്" : "ARAI Range"
                : language === "ml" ? "മൈലേജ്" : "Efficiency"}
            </span>
            <span className="mt-0.5 block font-mono font-medium text-zinc-800">
              {vehicle.ev_range_km
                ? `${vehicle.ev_range_km} km`
                : vehicle.mileage_kpl
                ? `${vehicle.mileage_kpl} km/l`
                : "Verified"}
            </span>
          </div>
        </div>

        {/* Feature Highlights if present */}
        {vehicle.key_features && vehicle.key_features.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1">
            {vehicle.key_features.slice(0, 2).map((feat, idx) => (
              <span
                key={idx}
                className="rounded border border-zinc-100 bg-zinc-50 px-2 py-0.5 text-[10px] font-medium text-zinc-600"
              >
                {feat}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="mt-5 border-t border-zinc-100 pt-3">
        <div className="flex items-center space-x-2">
          <button
            onClick={() => onAction && onAction("test_drive", vehicle)}
            className="flex-1 rounded-md border border-zinc-900 bg-zinc-900 px-3 py-1.5 text-xs font-medium text-white shadow-xs hover:bg-zinc-800 active:scale-98 transition"
          >
            {language === "ml" ? "ടെസ്റ്റ് ഡ്രൈവ്" : "Book Test Drive"}
          </button>
          <button
            onClick={() => onAction && onAction("finance", vehicle)}
            className="rounded-md border border-zinc-200 bg-white px-3 py-1.5 text-xs font-medium text-zinc-700 hover:border-zinc-300 hover:bg-zinc-50 active:scale-98 transition"
          >
            {language === "ml" ? "EMI" : "EMI Plan"}
          </button>
          {onAction && (
            <button
              onClick={() => onAction("details", vehicle)}
              className="rounded-md border border-zinc-200 bg-white px-2 py-1.5 text-xs font-medium text-zinc-500 hover:text-zinc-950 hover:bg-zinc-50 transition"
              title="View full specifications"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </button>
          )}
        </div>

        {vehicle.verified_source && (
          <p className="mt-2 text-center text-[10px] text-zinc-400">
            {vehicle.verified_source}
          </p>
        )}
      </div>
    </div>
  );
};
