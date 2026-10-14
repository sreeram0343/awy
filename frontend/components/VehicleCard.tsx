"use client";

import React from "react";

export interface Vehicle {
  id: string;
  make: string;
  model: string;
  variant: string;
  category: string;
  fuel_type: string;
  transmission: string;
  ex_showroom_price: number;
  ncap_rating?: number;
  mileage_kpl?: number;
  ev_range_km?: number;
  seating_capacity?: number;
  verified_source?: string;
}

interface VehicleCardProps {
  vehicle: Vehicle;
  onAction?: (action: string, vehicle: Vehicle) => void;
  language: "en" | "ml";
}

export const VehicleCard: React.FC<VehicleCardProps> = ({ vehicle, onAction, language }) => {
  const formatINR = (amount: number) => {
    const lakhs = amount / 100000;
    return `₹${lakhs.toFixed(2)} Lakh`;
  };

  return (
    <div className="group relative flex flex-col justify-between overflow-hidden rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:shadow-md hover:border-blue-300">
      {/* Top Banner & Safety Badge */}
      <div>
        <div className="flex items-start justify-between">
          <div>
            <span className="inline-block rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-semibold text-slate-700">
              {vehicle.category}
            </span>
            <h3 className="mt-1.5 text-lg font-bold text-slate-900 group-hover:text-blue-600 transition">
              {vehicle.make} {vehicle.model}
            </h3>
            <p className="text-xs text-slate-500 font-medium">{vehicle.variant}</p>
          </div>

          {vehicle.ncap_rating && (
            <div className="flex items-center space-x-1 rounded-lg bg-emerald-50 px-2 py-1 border border-emerald-200">
              <span className="text-xs font-bold text-emerald-700">{vehicle.ncap_rating}★</span>
              <span className="text-[10px] font-semibold text-emerald-600 uppercase tracking-wider">NCAP</span>
            </div>
          )}
        </div>

        {/* Price Section */}
        <div className="mt-4 rounded-xl bg-slate-50 p-3 border border-slate-100">
          <p className="text-[11px] font-medium text-slate-500 uppercase tracking-wider">
            {language === "ml" ? "എക്സ്-ഷോറൂം വില" : "Ex-Showroom Price"}
          </p>
          <p className="text-xl font-extrabold text-blue-700">{formatINR(vehicle.ex_showroom_price)}</p>
          <p className="text-[10px] text-slate-400 mt-0.5">Indicative Kerala baseline • Excludes on-road taxes</p>
        </div>

        {/* Key Specifications Grid */}
        <div className="mt-4 grid grid-cols-2 gap-2 text-xs">
          <div className="rounded-lg bg-slate-50/80 p-2 border border-slate-100/80">
            <span className="text-slate-400 block text-[10px]">{language === "ml" ? "ഇന്ധനം" : "Fuel & Gearbox"}</span>
            <span className="font-semibold text-slate-700">{vehicle.fuel_type} • {vehicle.transmission}</span>
          </div>

          <div className="rounded-lg bg-slate-50/80 p-2 border border-slate-100/80">
            <span className="text-slate-400 block text-[10px]">{language === "ml" ? "മൈലേജ് / റേഞ്ച്" : "Efficiency"}</span>
            <span className="font-semibold text-slate-700">
              {vehicle.ev_range_km ? `${vehicle.ev_range_km} km (ARAI)` : vehicle.mileage_kpl ? `${vehicle.mileage_kpl} km/l` : "Verified"}
            </span>
          </div>
        </div>
      </div>

      {/* Footer & Quick Actions */}
      <div className="mt-5 pt-3 border-t border-slate-100">
        <div className="flex items-center justify-between space-x-2">
          <button
            onClick={() => onAction && onAction("test_drive", vehicle)}
            className="flex-1 rounded-xl bg-blue-600 px-3 py-2 text-xs font-semibold text-white shadow-sm hover:bg-blue-700 active:scale-95 transition"
          >
            {language === "ml" ? "ടെസ്റ്റ് ഡ്രൈവ്" : "Book Test Drive"}
          </button>
          <button
            onClick={() => onAction && onAction("finance", vehicle)}
            className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 active:scale-95 transition"
          >
            {language === "ml" ? "EMI കാൽക്കുലേറ്റർ" : "EMI Calculator"}
          </button>
        </div>

        {vehicle.verified_source && (
          <p className="mt-2 text-center text-[10px] text-slate-400 font-medium">
            ✓ {vehicle.verified_source}
          </p>
        )}
      </div>
    </div>
  );
};
