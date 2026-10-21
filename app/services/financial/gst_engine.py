from typing import Dict, Any, Optional
from app.services.financial.config_loader import FinancialConfigLoader


class GSTEngine:
    @staticmethod
    def compute_gst_and_cess(
        category: str,
        fuel_type: str,
        ex_showroom_price: float,
        engine_capacity_cc: Optional[float] = None,
        length_mm: Optional[float] = None,
        ground_clearance_mm: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Compute GST rate, compensation cess rate, and breakdown of taxes included
        in the ex-showroom price according to MoF / GST Council rules.
        """
        cfg = FinancialConfigLoader.load_config()
        gst_cfg = cfg.get("gst_and_cess_slabs", {})

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

        if fuel == "EV":
            gst_rate = float(gst_cfg.get("ev_gst_rate", 5.0))
            cess_rate = 0.0
            cess_type = "ev"
        elif cat == "2W":
            gst_rate = float(gst_cfg.get("standard_gst_rate", 28.0))
            tw_cess = gst_cfg.get("2W_cess", {})
            if engine_capacity_cc and engine_capacity_cc > 350.0:
                cess_rate = float(tw_cess.get("above_350cc", 3.0))
                cess_type = "above_350cc"
            else:
                cess_rate = float(tw_cess.get("under_350cc", 0.0))
                cess_type = "under_350cc"
        else:
            # 4W
            gst_rate = float(gst_cfg.get("standard_gst_rate", 28.0))
            fw_cess = gst_cfg.get("4W_cess", {})
            cc = engine_capacity_cc or 1200.0
            length = length_mm or 3995.0
            gc = ground_clearance_mm or 180.0

            # Large SUV criteria: length > 4000mm, ground clearance >= 170mm, engine > 1500cc
            if length > 4000.0 and gc >= 170.0 and cc > 1500.0:
                cess_rate = float(fw_cess.get("suv_large", 22.0))
                cess_type = "suv_large"
            elif fuel == "Diesel":
                if length <= 4000.0 and cc <= 1500.0:
                    cess_rate = float(fw_cess.get("sub_4m_diesel_under_1500cc", 3.0))
                    cess_type = "sub_4m_diesel"
                else:
                    cess_rate = float(fw_cess.get("large_diesel", 20.0))
                    cess_type = "large_diesel"
            else:
                # Petrol / Hybrid / CNG
                if length <= 4000.0 and cc <= 1200.0:
                    cess_rate = float(fw_cess.get("sub_4m_petrol_under_1200cc", 1.0))
                    cess_type = "sub_4m_petrol"
                else:
                    cess_rate = float(fw_cess.get("large_petrol", 15.0))
                    cess_type = "large_petrol"

        total_tax_rate = gst_rate + cess_rate
        # Ex-showroom = Base Price * (1 + total_tax_rate / 100)
        base_price = round(ex_showroom_price / (1.0 + (total_tax_rate / 100.0)), 2)
        gst_amount = round(base_price * (gst_rate / 100.0), 2)
        cess_amount = round(base_price * (cess_rate / 100.0), 2)
        total_tax_amount = round(gst_amount + cess_amount, 2)

        return {
            "gst_rate_percent": gst_rate,
            "cess_rate_percent": cess_rate,
            "cess_type": cess_type,
            "total_tax_rate_percent": total_tax_rate,
            "base_factory_price": base_price,
            "gst_amount": gst_amount,
            "cess_amount": cess_amount,
            "total_tax_amount": total_tax_amount,
            "rule_version": cfg.get("version"),
        }


gst_engine = GSTEngine()
