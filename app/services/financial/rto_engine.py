from typing import Dict, Any, Optional
from app.services.financial.config_loader import FinancialConfigLoader


class RTOEngine:
    @staticmethod
    def compute_rto(
        state_code: str,
        category: str,
        fuel_type: str,
        ex_showroom_price: float,
    ) -> Dict[str, Any]:
        """
        Compute state-wise RTO road tax and registration fees deterministically
        from versioned external financial config.
        """
        cfg = FinancialConfigLoader.load_config()
        rto_slabs = cfg.get("state_rto_slabs", {})

        st_code_clean = state_code.strip().upper()
        cat_clean = category.strip().upper()
        fuel_raw = fuel_type.strip().upper()
        if fuel_raw in ["EV", "ELECTRIC", "BEV"]:
            fuel_clean = "EV"
        elif fuel_raw in ["DIESEL"]:
            fuel_clean = "Diesel"
        elif fuel_raw in ["CNG"]:
            fuel_clean = "CNG"
        else:
            fuel_clean = "Petrol"

        state_data = rto_slabs.get(st_code_clean)
        if not state_data:
            # Fallback to Delhi slabs as default benchmark if unspecified state
            state_data = rto_slabs.get("DL", {})
            st_code_clean = "DL"

        state_name = state_data.get("state_name", st_code_clean)
        cat_slabs = state_data.get(cat_clean, state_data.get("4W", {}))

        # Select fuel specific slabs or default
        fuel_slabs = cat_slabs.get(fuel_clean, cat_slabs.get("default", []))

        selected_slab = None
        for slab in fuel_slabs:
            max_p = slab.get("max_price")
            if max_p is None or ex_showroom_price <= max_p:
                selected_slab = slab
                break

        if not selected_slab and fuel_slabs:
            selected_slab = fuel_slabs[-1]
        elif not selected_slab:
            selected_slab = {"rate_percent": 10.0, "fixed_fee": 1000.0}

        rate_pct = float(selected_slab.get("rate_percent", 0.0))
        fixed_fee = float(selected_slab.get("fixed_fee", 0.0))
        tax_amount = round((ex_showroom_price * (rate_pct / 100.0)) + fixed_fee, 2)

        return {
            "state_code": st_code_clean,
            "state_name": state_name,
            "rate_percent": rate_pct,
            "fixed_fee": fixed_fee,
            "rto_tax_amount": tax_amount,
            "rule_version": cfg.get("version"),
        }


rto_engine = RTOEngine()
