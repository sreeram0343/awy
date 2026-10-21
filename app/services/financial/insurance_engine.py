from typing import Dict, Any, Optional
from app.services.financial.config_loader import FinancialConfigLoader


class InsuranceEngine:
    @staticmethod
    def compute_insurance(
        category: str,
        fuel_type: str,
        ex_showroom_price: float,
        engine_capacity_cc: Optional[float] = None,
        motor_power_kw: Optional[float] = None,
        zero_dep: bool = True,
        engine_protect: bool = True,
        return_to_invoice: bool = False,
        roadside_assist: bool = True,
        cpa_cover: bool = True,
    ) -> Dict[str, Any]:
        """
        Compute insurance premium according to IRDAI mandated slabs and
        standard motor insurance underwriting rules.
        """
        cfg = FinancialConfigLoader.load_config()
        ins_cfg = cfg.get("insurance_rules", {})

        cat = category.strip().upper()
        fuel_raw = fuel_type.strip().upper()
        if fuel_raw in ["EV", "ELECTRIC", "BEV"]:
            fuel = "EV"
        elif fuel_raw in ["DIESEL"]:
            fuel = "Diesel"
        elif fuel_raw in ["CNG"]:
            fuel = "CNG"
        else:
            fuel = "Petrol"

        # 1. Compute Insured Declared Value (IDV) - standard 95% for brand new vehicles
        idv_factor = float(ins_cfg.get("new_vehicle_idv_factor", 0.95))
        idv = round(ex_showroom_price * idv_factor, 2)

        # 2. Base Own Damage (OD) Premium
        od_rate_map = ins_cfg.get("base_od_rate_percent", {})
        od_rate = float(od_rate_map.get(cat, 2.15))
        base_od = round(idv * (od_rate / 100.0), 2)

        # 3. Add-on covers (computed as percentage of base OD)
        addon_rates = ins_cfg.get("add_ons_rates_percent_of_od", {})
        addons_breakdown = {}
        total_addons = 0.0

        if zero_dep:
            z_rate = float(addon_rates.get("zero_depreciation", 15.0))
            z_cost = round(base_od * (z_rate / 100.0), 2)
            addons_breakdown["zero_depreciation"] = z_cost
            total_addons += z_cost

        if engine_protect and fuel != "EV":
            ep_rate = float(addon_rates.get("engine_protection", 6.0))
            ep_cost = round(base_od * (ep_rate / 100.0), 2)
            addons_breakdown["engine_protection"] = ep_cost
            total_addons += ep_cost

        if return_to_invoice:
            rti_rate = float(addon_rates.get("return_to_invoice", 10.0))
            rti_cost = round(base_od * (rti_rate / 100.0), 2)
            addons_breakdown["return_to_invoice"] = rti_cost
            total_addons += rti_cost

        if roadside_assist:
            rsa_rate = float(addon_rates.get("roadside_assistance", 3.0))
            rsa_cost = round(base_od * (rsa_rate / 100.0), 2)
            addons_breakdown["roadside_assistance"] = rsa_cost
            total_addons += rsa_cost

        total_addons = round(total_addons, 2)

        # 4. Mandatory Third-Party (TP) Premium as per IRDAI statutory slabs
        tp_slabs = ins_cfg.get("tp_slabs", {}).get(cat, {})
        tp_premium = 0.0

        if fuel == "EV":
            ev_tp_slabs = tp_slabs.get("EV", [])
            kw = motor_power_kw or 15.0
            for slab in ev_tp_slabs:
                max_kw = slab.get("max_kw")
                if max_kw is None or kw <= max_kw:
                    tp_premium = float(slab.get("premium", 5543.0))
                    break
        else:
            ice_tp_slabs = tp_slabs.get("ICE", [])
            cc = engine_capacity_cc or (1200.0 if cat == "4W" else 150.0)
            for slab in ice_tp_slabs:
                max_cc = slab.get("max_cc")
                if max_cc is None or cc <= max_cc:
                    tp_premium = float(slab.get("premium", 6286.0))
                    break

        # 5. Compulsory Personal Accident (CPA) cover for owner-driver
        cpa_premium = float(ins_cfg.get("pa_cover_driver_annual", 375.0)) if cpa_cover else 0.0

        # 6. Total Net Premium & GST
        net_premium = round(base_od + total_addons + tp_premium + cpa_premium, 2)
        gst_percent = float(ins_cfg.get("gst_on_insurance_percent", 18.0))
        gst_amount = round(net_premium * (gst_percent / 100.0), 2)
        total_insurance = round(net_premium + gst_amount, 2)

        mandate_years = ins_cfg.get("third_party_mandate_years", {}).get(cat, 3)

        return {
            "idv": idv,
            "base_od_premium": base_od,
            "tp_premium": tp_premium,
            "tp_tenure_years": mandate_years,
            "addons_total": total_addons,
            "addons_breakdown": addons_breakdown,
            "cpa_cover": cpa_premium,
            "net_premium": net_premium,
            "gst_rate_percent": gst_percent,
            "gst_amount": gst_amount,
            "total_insurance_premium": total_insurance,
            "rule_version": cfg.get("version"),
        }


insurance_engine = InsuranceEngine()
