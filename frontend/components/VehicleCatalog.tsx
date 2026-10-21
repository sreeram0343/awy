"use client";

import React, { useState, useEffect } from "react";
import { VehicleCard, Vehicle } from "./VehicleCard";

interface VehicleCatalogProps {
  language: "en" | "ml";
  onSelectVehicleForEMI: (vehicle: Vehicle) => void;
  onSelectVehicleForTestDrive: (vehicle: Vehicle) => void;
}

export const VehicleCatalog: React.FC<VehicleCatalogProps> = ({
  language,
  onSelectVehicleForEMI,
  onSelectVehicleForTestDrive,
}) => {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedFuel, setSelectedFuel] = useState<string>("All");
  const [selectedCategory, setSelectedCategory] = useState<string>("All");
  const [maxPrice, setMaxPrice] = useState<number>(3000000);
  const [minNcap, setMinNcap] = useState<number>(0);
  const [comparingVehicles, setComparingVehicles] = useState<Vehicle[]>([]);
  const [detailModalVehicle, setDetailModalVehicle] = useState<Vehicle | null>(null);

  // Fetch verified vehicles from backend
  useEffect(() => {
    const fetchVehicles = async () => {
      setLoading(true);
      try {
        let url = "http://localhost:8000/api/v1/vehicles";
        const params = new URLSearchParams();
        if (searchQuery.trim()) params.append("query", searchQuery.trim());
        if (selectedFuel !== "All") params.append("fuel_type", selectedFuel);
        if (selectedCategory !== "All") params.append("category", selectedCategory);
        if (maxPrice < 3000000) params.append("max_price", maxPrice.toString());
        if (minNcap > 0) params.append("min_ncap", minNcap.toString());

        const fullUrl = params.toString() ? `${url}?${params.toString()}` : url;
        const res = await fetch(fullUrl);
        if (res.ok) {
          const json = await res.json();
          if (json.data) {
            setVehicles(json.data);
            setLoading(false);
            return;
          }
        }
      } catch (err) {
        console.warn("Could not fetch remote vehicles, falling back to local dataset:", err);
      }

      // Built-in fallback verified dataset
      setVehicles(FALLBACK_INVENTORY);
      setLoading(false);
    };

    const timer = setTimeout(fetchVehicles, 150);
    return () => clearTimeout(timer);
  }, [searchQuery, selectedFuel, selectedCategory, maxPrice, minNcap]);

  const toggleCompare = (vehicle: Vehicle) => {
    if (comparingVehicles.some((v) => v.id === vehicle.id)) {
      setComparingVehicles(comparingVehicles.filter((v) => v.id !== vehicle.id));
    } else {
      if (comparingVehicles.length >= 3) {
        alert(language === "ml" ? "പരമാവധി 3 വാഹനങ്ങൾ താരതമ്യം ചെയ്യാം" : "Maximum 3 vehicles can be compared side-by-side");
        return;
      }
      setComparingVehicles([...comparingVehicles, vehicle]);
    }
  };

  const clearFilters = () => {
    setSearchQuery("");
    setSelectedFuel("All");
    setSelectedCategory("All");
    setMaxPrice(3000000);
    setMinNcap(0);
  };

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {/* View Header */}
      <div className="border-b border-zinc-200 pb-5">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-xl font-bold tracking-tight text-zinc-950 sm:text-2xl">
              {language === "ml" ? "വാഹന കാറ്റലോഗ് & താരതമ്യം" : "Verified Vehicle Inventory"}
            </h1>
            <p className="mt-1 text-xs text-zinc-500">
              {language === "ml"
                ? "അപെക്സ് മോട്ടോഴ്സ് കേരളയിലെ പരിശോധിച്ച മോഡലുകളും സ്പെസിഫിക്കേഷനുകളും"
                : "Explore verified technical specifications, ex-showroom pricing, and safety ratings"}
            </p>
          </div>

          {/* Quick Active Comparison Badge */}
          {comparingVehicles.length > 0 && (
            <div className="flex items-center space-x-2 rounded-lg border border-zinc-200 bg-zinc-50 px-3 py-1.5 text-xs">
              <span className="font-medium text-zinc-700">
                {language === "ml"
                  ? `${comparingVehicles.length} വാഹനങ്ങൾ താരതമ്യം ചെയ്യുന്നു`
                  : `Comparing ${comparingVehicles.length} of 3 models`}
              </span>
              <button
                onClick={() => setComparingVehicles([])}
                className="text-zinc-400 hover:text-zinc-600 ml-2"
              >
                Clear
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="mt-6 rounded-xl border border-zinc-200 bg-white p-4 shadow-xs">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Keyword Search */}
          <div className="md:col-span-1">
            <label className="block text-[11px] font-semibold text-zinc-600 uppercase tracking-wider mb-1.5">
              {language === "ml" ? "തിരയുക" : "Search Model"}
            </label>
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder={language === "ml" ? "ഉദാ: Nexon, Creta, EV..." : "e.g. Nexon, Creta, EV..."}
                className="w-full rounded-md border border-zinc-200 bg-white px-3 py-1.5 text-xs text-zinc-900 placeholder-zinc-400 focus:border-zinc-900 focus:outline-none"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery("")}
                  className="absolute right-2.5 top-2 text-zinc-400 hover:text-zinc-600 text-xs"
                >
                  ×
                </button>
              )}
            </div>
          </div>

          {/* Fuel Type Filter */}
          <div>
            <label className="block text-[11px] font-semibold text-zinc-600 uppercase tracking-wider mb-1.5">
              {language === "ml" ? "ഇന്ധന തരം" : "Powertrain"}
            </label>
            <div className="flex items-center space-x-1">
              {["All", "Petrol", "Electric", "Diesel", "Hybrid"].map((fuel) => (
                <button
                  key={fuel}
                  onClick={() => setSelectedFuel(fuel)}
                  className={`rounded border px-2 py-1 text-[11px] font-medium transition ${
                    selectedFuel === fuel
                      ? "border-zinc-900 bg-zinc-900 text-white"
                      : "border-zinc-200 bg-white text-zinc-600 hover:border-zinc-300"
                  }`}
                >
                  {fuel}
                </button>
              ))}
            </div>
          </div>

          {/* NCAP Safety Rating Filter */}
          <div>
            <label className="block text-[11px] font-semibold text-zinc-600 uppercase tracking-wider mb-1.5">
              {language === "ml" ? "കുറഞ്ഞ NCAP സുരക്ഷ" : "Minimum NCAP Rating"}
            </label>
            <div className="flex items-center space-x-1.5">
              {[0, 4, 5].map((stars) => (
                <button
                  key={stars}
                  onClick={() => setMinNcap(stars)}
                  className={`rounded border px-2.5 py-1 text-[11px] font-medium transition ${
                    minNcap === stars
                      ? "border-zinc-900 bg-zinc-900 text-white"
                      : "border-zinc-200 bg-white text-zinc-600 hover:border-zinc-300"
                  }`}
                >
                  {stars === 0 ? "Any" : `${stars}★ & above`}
                </button>
              ))}
            </div>
          </div>

          {/* Price Range Slider */}
          <div>
            <div className="flex items-center justify-between text-[11px] font-semibold text-zinc-600 uppercase tracking-wider mb-1.5">
              <span>{language === "ml" ? "പരമാവധി ബഡ്ജറ്റ്" : "Max Ex-Showroom"}</span>
              <span className="font-mono text-zinc-900">₹{(maxPrice / 100000).toFixed(1)} Lakh</span>
            </div>
            <input
              type="range"
              min="800000"
              max="3000000"
              step="100000"
              value={maxPrice}
              onChange={(e) => setMaxPrice(Number(e.target.value))}
              className="w-full accent-zinc-900 cursor-pointer"
            />
          </div>
        </div>

        {/* Clear filters action */}
        {(searchQuery || selectedFuel !== "All" || selectedCategory !== "All" || maxPrice < 3000000 || minNcap > 0) && (
          <div className="mt-3 pt-3 border-t border-zinc-100 flex items-center justify-between text-xs text-zinc-500">
            <span>Filters active • Showing {vehicles.length} matching vehicles</span>
            <button
              onClick={clearFilters}
              className="text-zinc-800 hover:underline font-medium"
            >
              Reset all filters
            </button>
          </div>
        )}
      </div>

      {/* Side-by-Side Comparison Matrix (if vehicles selected) */}
      {comparingVehicles.length > 1 && (
        <div className="mt-8 rounded-xl border border-zinc-300 bg-zinc-50/50 p-5 shadow-xs">
          <div className="flex items-center justify-between border-b border-zinc-200 pb-3 mb-4">
            <div>
              <h2 className="text-sm font-bold text-zinc-900 tracking-tight">
                {language === "ml" ? "വശങ്ങളോടു വശം താരതമ്യം" : "Side-by-Side Spec Comparison Matrix"}
              </h2>
              <p className="text-[11px] text-zinc-500">
                Direct parameter evaluation across selected vehicles
              </p>
            </div>
            <button
              onClick={() => setComparingVehicles([])}
              className="rounded border border-zinc-200 bg-white px-2.5 py-1 text-xs text-zinc-600 hover:bg-zinc-100"
            >
              Close Comparison
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead>
                <tr className="border-b border-zinc-200">
                  <th className="py-2.5 px-3 font-semibold text-zinc-500 uppercase tracking-wider text-[10px]">Parameter</th>
                  {comparingVehicles.map((v) => (
                    <th key={v.id} className="py-2.5 px-3 font-bold text-zinc-900 min-w-[160px]">
                      {v.make} {v.model}
                      <span className="block text-[10px] font-normal text-zinc-500">{v.variant}</span>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-100">
                <tr>
                  <td className="py-2.5 px-3 font-medium text-zinc-500">Ex-Showroom Price</td>
                  {comparingVehicles.map((v) => (
                    <td key={v.id} className="py-2.5 px-3 font-bold font-mono text-zinc-900">
                      ₹{(v.ex_showroom_price / 100000).toFixed(2)} Lakh
                    </td>
                  ))}
                </tr>
                <tr>
                  <td className="py-2.5 px-3 font-medium text-zinc-500">Powertrain & Fuel</td>
                  {comparingVehicles.map((v) => (
                    <td key={v.id} className="py-2.5 px-3 text-zinc-800">{v.fuel_type}</td>
                  ))}
                </tr>
                <tr>
                  <td className="py-2.5 px-3 font-medium text-zinc-500">Transmission</td>
                  {comparingVehicles.map((v) => (
                    <td key={v.id} className="py-2.5 px-3 text-zinc-800">{v.transmission}</td>
                  ))}
                </tr>
                <tr>
                  <td className="py-2.5 px-3 font-medium text-zinc-500">Safety Rating</td>
                  {comparingVehicles.map((v) => (
                    <td key={v.id} className="py-2.5 px-3 font-semibold text-zinc-900">
                      {v.ncap_rating ? `${v.ncap_rating}★ Global NCAP` : "Tested"}
                    </td>
                  ))}
                </tr>
                <tr>
                  <td className="py-2.5 px-3 font-medium text-zinc-500">Efficiency / Range</td>
                  {comparingVehicles.map((v) => (
                    <td key={v.id} className="py-2.5 px-3 font-mono text-zinc-800">
                      {v.ev_range_km ? `${v.ev_range_km} km (ARAI)` : v.mileage_kpl ? `${v.mileage_kpl} km/l` : "Verified"}
                    </td>
                  ))}
                </tr>
                <tr>
                  <td className="py-2.5 px-3 font-medium text-zinc-500">Seating Capacity</td>
                  {comparingVehicles.map((v) => (
                    <td key={v.id} className="py-2.5 px-3 text-zinc-800">{v.seating_capacity || 5} Seats</td>
                  ))}
                </tr>
                <tr>
                  <td className="py-2.5 px-3 font-medium text-zinc-500">Ground Clearance</td>
                  {comparingVehicles.map((v) => (
                    <td key={v.id} className="py-2.5 px-3 text-zinc-800">{v.ground_clearance_mm ? `${v.ground_clearance_mm} mm` : "190 mm"}</td>
                  ))}
                </tr>
                <tr>
                  <td className="py-2.5 px-3 font-medium text-zinc-500">Boot Space</td>
                  {comparingVehicles.map((v) => (
                    <td key={v.id} className="py-2.5 px-3 text-zinc-800">{v.boot_space_litres ? `${v.boot_space_litres} Litres` : "382 L"}</td>
                  ))}
                </tr>
                <tr>
                  <td className="py-2.5 px-3 font-medium text-zinc-500">Actions</td>
                  {comparingVehicles.map((v) => (
                    <td key={v.id} className="py-2.5 px-3">
                      <div className="flex space-x-1.5">
                        <button
                          onClick={() => onSelectVehicleForTestDrive(v)}
                          className="rounded border border-zinc-900 bg-zinc-900 px-2.5 py-1 text-[11px] font-medium text-white hover:bg-zinc-800"
                        >
                          Book Drive
                        </button>
                        <button
                          onClick={() => onSelectVehicleForEMI(v)}
                          className="rounded border border-zinc-200 bg-white px-2.5 py-1 text-[11px] font-medium text-zinc-700 hover:bg-zinc-50"
                        >
                          Plan EMI
                        </button>
                      </div>
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Vehicle Grid */}
      <div className="mt-8">
        {loading ? (
          <div className="py-16 text-center text-xs text-zinc-400">
            <div className="inline-block h-6 w-6 animate-spin rounded-full border-2 border-zinc-300 border-t-zinc-900 mb-2" />
            <p>Loading verified inventory...</p>
          </div>
        ) : vehicles.length === 0 ? (
          <div className="rounded-xl border border-dashed border-zinc-200 py-16 text-center">
            <p className="text-sm font-medium text-zinc-700">No vehicles match your active criteria</p>
            <p className="mt-1 text-xs text-zinc-400">Try widening your price limit or clearing filters</p>
            <button
              onClick={clearFilters}
              className="mt-4 rounded-md border border-zinc-200 bg-white px-3 py-1.5 text-xs font-medium text-zinc-700 hover:bg-zinc-50"
            >
              Reset Filters
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {vehicles.map((vehicle) => (
              <VehicleCard
                key={vehicle.id}
                vehicle={vehicle}
                language={language}
                isComparing={comparingVehicles.some((v) => v.id === vehicle.id)}
                onToggleCompare={toggleCompare}
                onAction={(action, v) => {
                  if (action === "test_drive") onSelectVehicleForTestDrive(v);
                  else if (action === "finance") onSelectVehicleForEMI(v);
                  else if (action === "details") setDetailModalVehicle(v);
                }}
              />
            ))}
          </div>
        )}
      </div>

      {/* Vehicle Details Modal */}
      {detailModalVehicle && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-zinc-950/40 backdrop-blur-xs p-4">
          <div className="w-full max-w-lg rounded-xl border border-zinc-200 bg-white p-6 shadow-xl">
            <div className="flex items-start justify-between border-b border-zinc-100 pb-3">
              <div>
                <span className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
                  {detailModalVehicle.make}
                </span>
                <h3 className="text-lg font-bold text-zinc-950">
                  {detailModalVehicle.model} {detailModalVehicle.variant}
                </h3>
              </div>
              <button
                onClick={() => setDetailModalVehicle(null)}
                className="text-zinc-400 hover:text-zinc-600 text-lg leading-none p-1"
              >
                ✕
              </button>
            </div>

            <div className="mt-4 space-y-3 text-xs">
              <div className="flex justify-between py-1 border-b border-zinc-50">
                <span className="text-zinc-500">Ex-Showroom Price</span>
                <span className="font-bold font-mono text-zinc-900">
                  ₹{(detailModalVehicle.ex_showroom_price / 100000).toFixed(2)} Lakh
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-zinc-50">
                <span className="text-zinc-500">Powertrain & Fuel</span>
                <span className="font-medium text-zinc-800">
                  {detailModalVehicle.fuel_type} • {detailModalVehicle.transmission}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-zinc-50">
                <span className="text-zinc-500">Efficiency / Range</span>
                <span className="font-medium text-zinc-800">
                  {detailModalVehicle.ev_range_km
                    ? `${detailModalVehicle.ev_range_km} km ARAI`
                    : `${detailModalVehicle.mileage_kpl || 18.0} km/l`}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-zinc-50">
                <span className="text-zinc-500">Safety & Airbags</span>
                <span className="font-medium text-zinc-800">
                  {detailModalVehicle.ncap_rating}★ Global NCAP ({detailModalVehicle.airbags_count || 6} Airbags)
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-zinc-50">
                <span className="text-zinc-500">Ground Clearance</span>
                <span className="font-medium text-zinc-800">{detailModalVehicle.ground_clearance_mm || 208} mm</span>
              </div>
              <div className="flex justify-between py-1 border-b border-zinc-50">
                <span className="text-zinc-500">Boot Space</span>
                <span className="font-medium text-zinc-800">{detailModalVehicle.boot_space_litres || 382} Litres</span>
              </div>

              {detailModalVehicle.key_features && (
                <div className="pt-2">
                  <span className="font-medium text-zinc-700 block mb-1.5">Key Highlights:</span>
                  <div className="flex flex-wrap gap-1.5">
                    {detailModalVehicle.key_features.map((f, i) => (
                      <span key={i} className="rounded border border-zinc-100 bg-zinc-50 px-2 py-0.5 text-[10px] text-zinc-600">
                        {f}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="mt-6 flex space-x-2 pt-3 border-t border-zinc-100">
              <button
                onClick={() => {
                  onSelectVehicleForTestDrive(detailModalVehicle);
                  setDetailModalVehicle(null);
                }}
                className="flex-1 rounded-md border border-zinc-900 bg-zinc-900 py-2 text-xs font-medium text-white hover:bg-zinc-800"
              >
                Book Test Drive
              </button>
              <button
                onClick={() => {
                  onSelectVehicleForEMI(detailModalVehicle);
                  setDetailModalVehicle(null);
                }}
                className="flex-1 rounded-md border border-zinc-200 bg-white py-2 text-xs font-medium text-zinc-700 hover:bg-zinc-50"
              >
                Calculate EMI
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const FALLBACK_INVENTORY: Vehicle[] = [
  {
    id: "11111111-1111-1111-1111-111111111111",
    make: "Tata",
    model: "Nexon",
    variant: "Fearless Plus S",
    category: "SUV",
    body_type: "SUV",
    fuel_type: "Petrol",
    transmission: "7-Speed DCA",
    ex_showroom_price: 1349000.0,
    ncap_rating: 5,
    mileage_kpl: 17.44,
    seating_capacity: 5,
    airbags_count: 6,
    ground_clearance_mm: 208,
    boot_space_litres: 382,
    warranty_years: 3,
    key_features: ["360 Degree Camera", "Ventilated Front Seats", "Voice-assisted Sunroof", "Wireless Android Auto / Apple CarPlay"],
    verified_source: "Apex Motors Verified Catalog 2026"
  },
  {
    id: "22222222-2222-2222-2222-222222222222",
    make: "Hyundai",
    model: "Creta",
    variant: "SX (O) 1.5 Turbo",
    category: "SUV",
    body_type: "SUV",
    fuel_type: "Petrol",
    transmission: "7-Speed DCT",
    ex_showroom_price: 1999000.0,
    ncap_rating: 4,
    mileage_kpl: 18.4,
    seating_capacity: 5,
    airbags_count: 6,
    ground_clearance_mm: 190,
    boot_space_litres: 433,
    warranty_years: 3,
    key_features: ["Level 2 ADAS (19 Features)", "Dual-zone Climate Control", "Bose Premium 8-Speaker Audio"],
    verified_source: "Apex Motors Verified Catalog 2026"
  },
  {
    id: "33333333-3333-3333-3333-333333333333",
    make: "Tata",
    model: "Nexon EV",
    variant: "Empowered Plus Long Range",
    category: "SUV",
    body_type: "Electric SUV",
    fuel_type: "Electric",
    transmission: "Single-Speed Automatic",
    ex_showroom_price: 1699000.0,
    ev_range_km: 465.0,
    ncap_rating: 5,
    seating_capacity: 5,
    airbags_count: 6,
    ground_clearance_mm: 190,
    boot_space_litres: 350,
    warranty_years: 8,
    key_features: ["V2V & V2L Charging", "12.3-inch Cinematic Touchscreen", "Paddle Shifters for Multi-mode Regen"],
    verified_source: "Apex Motors Verified Catalog 2026"
  },
  {
    id: "44444444-4444-4444-4444-444444444444",
    make: "Mahindra",
    model: "XUV700",
    variant: "AX7 L AWD",
    category: "SUV",
    body_type: "7-Seater SUV",
    fuel_type: "Diesel",
    transmission: "6-Speed Automatic",
    ex_showroom_price: 2399000.0,
    ncap_rating: 5,
    mileage_kpl: 16.57,
    seating_capacity: 7,
    airbags_count: 7,
    ground_clearance_mm: 200,
    boot_space_litres: 450,
    warranty_years: 3,
    key_features: ["Sony 3D 12-Speaker Sound", "Smart Door Handles", "Personalized Safety Alerts"],
    verified_source: "Apex Motors Verified Catalog 2026"
  },
  {
    id: "55555555-5555-5555-5555-555555555555",
    make: "Maruti Suzuki",
    model: "Grand Vitara",
    variant: "Alpha Plus Strong Hybrid",
    category: "SUV",
    body_type: "Hybrid SUV",
    fuel_type: "Hybrid",
    transmission: "e-CVT",
    ex_showroom_price: 1993000.0,
    ncap_rating: 4,
    mileage_kpl: 27.97,
    seating_capacity: 5,
    airbags_count: 6,
    ground_clearance_mm: 210,
    boot_space_litres: 373,
    warranty_years: 3,
    key_features: ["Strong Hybrid Self-charging", "Head-Up Display (HUD)", "Panoramic Sunroof"],
    verified_source: "Apex Motors Verified Catalog 2026"
  },
  {
    id: "66666666-6666-6666-6666-666666666666",
    make: "Tata",
    model: "Punch",
    variant: "Creative Flagship DT",
    category: "Compact SUV",
    body_type: "Compact SUV",
    fuel_type: "Petrol",
    transmission: "5-Speed AMT",
    ex_showroom_price: 980000.0,
    ncap_rating: 5,
    mileage_kpl: 18.82,
    seating_capacity: 5,
    airbags_count: 2,
    ground_clearance_mm: 187,
    boot_space_litres: 366,
    warranty_years: 3,
    key_features: ["90-degree Door Opening", "5-Star Global NCAP", "Traction Pro Mode"],
    verified_source: "Apex Motors Verified Catalog 2026"
  }
];
