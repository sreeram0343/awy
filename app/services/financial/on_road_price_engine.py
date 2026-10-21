from typing import Dict, Any, Optional
from app.services.financial.config_loader import FinancialConfigLoader
from app.services.financial.rto_engine import rto_engine
from app.services.financial.insurance_engine import insurance_engine
from app.services.financial.gst_engine import gst_engine


class OnRoadPriceEngine:
    @staticmethod
    def calculate_on_road_price(
        state_code: str,
        category: str,
        fuel_type: str,
        ex_showroom_price: float,
        engine_capacity_cc: Optional[float] = None,
        motor_power_kw: Optional[float] = None,
        length_mm: Optional[float] = None,
        ground_clearance_mm: Optional[float] = None,
        optional_accessories: float = 0.0,
        extended_warranty: float = 0.0,
        zero_dep_insurance: bool = True,
        include_fastag: bool = True,
    ) -> Dict[str, Any]:
        """
        Compute complete, itemized, deterministic on-road price breakdown
        for both 4W and 2W vehicles across Indian states.
        """
        cfg = FinancialConfigLoader.load_config()
        incidentals = cfg.get("standard_incidental_fees", {})

        # 1. RTO Tax & Registration Fees
        rto_res = rto_engine.compute_rto(
            state_code=state_code,
            category=category,
            fuel_type=fuel_type,
            ex_showroom_price=ex_showroom_price,
        )
        rto_tax = rto_res["rto_tax_amount"]

        # 2. Insurance Premium (Comprehensive 1-yr OD + Multi-yr TP + Add-ons)
        ins_res = insurance_engine.compute_insurance(
            category=category,
            fuel_type=fuel_type,
            ex_showroom_price=ex_showroom_price,
            engine_capacity_cc=engine_capacity_cc,
            motor_power_kw=motor_power_kw,
            zero_dep=zero_dep_insurance,
        )
        insurance_premium = ins_res["total_insurance_premium"]

        # 3. GST & Cess embedded in Ex-Showroom (for audit trail)
        gst_res = gst_engine.compute_gst_and_cess(
            category=category,
            fuel_type=fuel_type,
            ex_showroom_price=ex_showroom_price,
            engine_capacity_cc=engine_capacity_cc,
            length_mm=length_mm,
            ground_clearance_mm=ground_clearance_mm,
        )

        # 4. Mandatory & Incidental Dealer / Registration Fees
        fastag_fee = float(incidentals.get("fastag", 500.0)) if (category.upper() == "4W" and include_fastag) else 0.0
        hsrp_fee = float(incidentals.get("hsrp_plate", 800.0))
        handling_fee = float(incidentals.get("handling_logistics", 1500.0)) if category.upper() == "4W" else 500.0

        total_incidentals = round(fastag_fee + hsrp_fee + handling_fee, 2)
        total_optional = round(max(0.0, optional_accessories) + max(0.0, extended_warranty), 2)

        # 5. Final On-Road Price Formula
        on_road_price = round(
            ex_showroom_price
            + rto_tax
            + insurance_premium
            + total_incidentals
            + total_optional,
            2
        )

        return {
            "state_code": rto_res["state_code"],
            "state_name": rto_res["state_name"],
            "category": category.upper(),
            "fuel_type": fuel_type,
            "ex_showroom_price": ex_showroom_price,
            "rto_charges": {
                "rto_tax_amount": rto_tax,
                "rate_percent": rto_res["rate_percent"],
                "fixed_fee": rto_res["fixed_fee"],
            },
            "insurance_charges": {
                "total_insurance_premium": insurance_premium,
                "idv": ins_res["idv"],
                "base_od_premium": ins_res["base_od_premium"],
                "tp_premium": ins_res["tp_premium"],
                "addons_total": ins_res["addons_total"],
                "gst_amount": ins_res["gst_amount"],
            },
            "incidental_charges": {
                "total": total_incidentals,
                "fastag": fastag_fee,
                "hsrp_plate": hsrp_fee,
                "handling_logistics": handling_fee,
            },
            "optional_charges": {
                "total": total_optional,
                "accessories": optional_accessories,
                "extended_warranty": extended_warranty,
            },
            "embedded_factory_taxes": {
                "base_factory_price": gst_res["base_factory_price"],
                "gst_amount": gst_res["gst_amount"],
                "cess_amount": gst_res["cess_amount"],
                "cess_rate_percent": gst_res["cess_rate_percent"],
            },
            "total_on_road_price": on_road_price,
            "rule_version": cfg.get("version"),
            "effective_date": cfg.get("effective_date"),
        }


on_road_price_engine = OnRoadPriceEngine()
