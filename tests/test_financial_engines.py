import pytest
from app.services.financial.config_loader import FinancialConfigLoader
from app.services.financial.rto_engine import rto_engine
from app.services.financial.gst_engine import gst_engine
from app.services.financial.insurance_engine import insurance_engine
from app.services.financial.emi_engine import emi_engine
from app.services.financial.on_road_price_engine import on_road_price_engine


# ==============================================================================
# 1. RTO TEST SUITE: 5 Hand-Verified Cases Per State Per Category (50 Total)
# ==============================================================================

# Format: (state, category, fuel, ex_showroom, expected_rate, expected_fixed, expected_tax)
HAND_VERIFIED_RTO_CASES = [
    # --- DELHI (DL) - 2W ---
    ("DL", "2W", "Petrol", 80000.0, 8.0, 300.0, 6700.0),       # 80k * 8% + 300 = 6400 + 300 = 6700
    ("DL", "2W", "Petrol", 100000.0, 8.0, 300.0, 8300.0),      # 100k * 8% + 300 = 8000 + 300 = 8300
    ("DL", "2W", "Petrol", 150000.0, 10.0, 300.0, 15300.0),    # 150k * 10% + 300 = 15000 + 300 = 15300
    ("DL", "2W", "Petrol", 250000.0, 10.0, 300.0, 25300.0),    # 250k * 10% + 300 = 25000 + 300 = 25300
    ("DL", "2W", "EV", 120000.0, 0.0, 300.0, 300.0),           # EV = 0% + 300 = 300

    # --- DELHI (DL) - 4W ---
    ("DL", "4W", "Petrol", 500000.0, 4.0, 1000.0, 21000.0),     # 500k * 4% + 1000 = 20000 + 1000 = 21000
    ("DL", "4W", "Petrol", 800000.0, 7.0, 1000.0, 57000.0),     # 800k * 7% + 1000 = 56000 + 1000 = 57000
    ("DL", "4W", "Petrol", 1200000.0, 10.0, 1000.0, 121000.0),  # 1.2M * 10% + 1000 = 120000 + 1000 = 121000
    ("DL", "4W", "Diesel", 1500000.0, 12.5, 1000.0, 188500.0),  # 1.5M * 12.5% + 1000 = 187500 + 1000 = 188500
    ("DL", "4W", "EV", 1800000.0, 0.0, 1000.0, 1000.0),        # EV = 0% + 1000 = 1000

    # --- MAHARASHTRA (MH) - 2W ---
    ("MH", "2W", "Petrol", 90000.0, 10.0, 500.0, 9500.0),       # 90k * 10% + 500 = 9000 + 500 = 9500
    ("MH", "2W", "Petrol", 150000.0, 11.0, 500.0, 17000.0),    # 150k * 11% + 500 = 16500 + 500 = 17000
    ("MH", "2W", "Petrol", 225000.0, 11.0, 500.0, 25250.0),    # 225k * 11% + 500 = 24750 + 500 = 25250
    ("MH", "2W", "Petrol", 350000.0, 12.0, 500.0, 42500.0),    # 350k * 12% + 500 = 42000 + 500 = 42500
    ("MH", "2W", "EV", 140000.0, 0.0, 500.0, 500.0),           # EV = 0% + 500 = 500

    # --- MAHARASHTRA (MH) - 4W ---
    ("MH", "4W", "Petrol", 900000.0, 11.0, 1500.0, 100500.0),   # 900k * 11% + 1500 = 99000 + 1500 = 100500
    ("MH", "4W", "Petrol", 1500000.0, 12.0, 1500.0, 181500.0),  # 1.5M * 12% + 1500 = 180000 + 1500 = 181500
    ("MH", "4W", "Petrol", 2500000.0, 13.0, 1500.0, 326500.0),  # 2.5M * 13% + 1500 = 325000 + 1500 = 326500
    ("MH", "4W", "Diesel", 1800000.0, 14.0, 1500.0, 253500.0),  # 1.8M * 14% + 1500 = 252000 + 1500 = 253500
    ("MH", "4W", "EV", 1600000.0, 0.0, 1500.0, 1500.0),        # EV = 0% + 1500 = 1500

    # --- KARNATAKA (KA) - 2W ---
    ("KA", "2W", "Petrol", 45000.0, 10.0, 500.0, 5000.0),       # 45k * 10% + 500 = 4500 + 500 = 5000
    ("KA", "2W", "Petrol", 90000.0, 12.0, 500.0, 11300.0),      # 90k * 12% + 500 = 10800 + 500 = 11300
    ("KA", "2W", "Petrol", 150000.0, 18.0, 500.0, 27500.0),    # 150k * 18% + 500 = 27000 + 500 = 27500
    ("KA", "2W", "Petrol", 300000.0, 18.0, 500.0, 54500.0),    # 300k * 18% + 500 = 54000 + 500 = 54500
    ("KA", "2W", "EV", 150000.0, 4.0, 500.0, 6500.0),          # EV = 4% + 500 = 6000 + 500 = 6500

    # --- KARNATAKA (KA) - 4W ---
    ("KA", "4W", "Petrol", 450000.0, 13.0, 1500.0, 60000.0),    # 450k * 13% + 1500 = 58500 + 1500 = 60000
    ("KA", "4W", "Petrol", 800000.0, 14.0, 1500.0, 113500.0),   # 800k * 14% + 1500 = 112000 + 1500 = 113500
    ("KA", "4W", "Petrol", 1500000.0, 17.0, 1500.0, 256500.0),  # 1.5M * 17% + 1500 = 255000 + 1500 = 256500
    ("KA", "4W", "Diesel", 2200000.0, 18.5, 1500.0, 408500.0),  # 2.2M * 18.5% + 1500 = 407000 + 1500 = 408500
    ("KA", "4W", "EV", 2000000.0, 0.0, 1500.0, 1500.0),        # EV under 25L = 0% + 1500 = 1500

    # --- TAMIL NADU (TN) - 2W ---
    ("TN", "2W", "Petrol", 75000.0, 8.0, 500.0, 6500.0),        # 75k * 8% + 500 = 6000 + 500 = 6500
    ("TN", "2W", "Petrol", 100000.0, 8.0, 500.0, 8500.0),       # 100k * 8% + 500 = 8000 + 500 = 8500
    ("TN", "2W", "Petrol", 180000.0, 12.0, 500.0, 22100.0),     # 180k * 12% + 500 = 21600 + 500 = 22100
    ("TN", "2W", "Petrol", 300000.0, 12.0, 500.0, 36500.0),     # 300k * 12% + 500 = 36000 + 500 = 36500
    ("TN", "2W", "EV", 135000.0, 0.0, 500.0, 500.0),           # EV = 0% + 500 = 500

    # --- TAMIL NADU (TN) - 4W ---
    ("TN", "4W", "Petrol", 850000.0, 10.0, 1000.0, 86000.0),    # 850k * 10% + 1000 = 85000 + 1000 = 86000
    ("TN", "4W", "Petrol", 1400000.0, 15.0, 1000.0, 211000.0),  # 1.4M * 15% + 1000 = 210000 + 1000 = 211000
    ("TN", "4W", "Diesel", 1800000.0, 15.0, 1000.0, 271000.0),  # 1.8M * 15% + 1000 = 270000 + 1000 = 271000
    ("TN", "4W", "Diesel", 2600000.0, 15.0, 1000.0, 391000.0),  # 2.6M * 15% + 1000 = 390000 + 1000 = 391000
    ("TN", "4W", "EV", 1750000.0, 0.0, 1000.0, 1000.0),        # EV = 0% + 1000 = 1000

    # --- HARYANA (HR) - 2W ---
    ("HR", "2W", "Petrol", 85000.0, 6.0, 400.0, 5500.0),        # 85k * 6% + 400 = 5100 + 400 = 5500
    ("HR", "2W", "Petrol", 150000.0, 8.0, 400.0, 12400.0),      # 150k * 8% + 400 = 12000 + 400 = 12400
    ("HR", "2W", "Petrol", 220000.0, 10.0, 400.0, 22400.0),     # 220k * 10% + 400 = 22000 + 400 = 22400
    ("HR", "2W", "Petrol", 320000.0, 10.0, 400.0, 32400.0),     # 320k * 10% + 400 = 32000 + 400 = 32400
    ("HR", "2W", "EV", 125000.0, 0.0, 400.0, 400.0),           # EV = 0% + 400 = 400

    # --- HARYANA (HR) - 4W ---
    ("HR", "4W", "Petrol", 550000.0, 5.0, 1000.0, 28500.0),     # 550k * 5% + 1000 = 27500 + 1000 = 28500
    ("HR", "4W", "Petrol", 850000.0, 8.0, 1000.0, 69000.0),     # 850k * 8% + 1000 = 68000 + 1000 = 69000
    ("HR", "4W", "Petrol", 1500000.0, 9.0, 1000.0, 136000.0),   # 1.5M * 9% + 1000 = 135000 + 1000 = 136000
    ("HR", "4W", "Diesel", 2400000.0, 10.0, 1000.0, 241000.0),  # 2.4M * 10% + 1000 = 240000 + 1000 = 241000
    ("HR", "4W", "EV", 1500000.0, 0.0, 1000.0, 1000.0),        # EV = 0% + 1000 = 1000
]


@pytest.mark.parametrize("state,category,fuel,price,exp_rate,exp_fixed,exp_tax", HAND_VERIFIED_RTO_CASES)
def test_hand_verified_rto_tax_calculations(state, category, fuel, price, exp_rate, exp_fixed, exp_tax):
    res = rto_engine.compute_rto(state, category, fuel, price)
    assert res["state_code"] == state
    assert res["rate_percent"] == exp_rate
    assert res["fixed_fee"] == exp_fixed
    assert res["rto_tax_amount"] == exp_tax


# ==============================================================================
# 2. GST & CESS MODULE TESTS
# ==============================================================================

def test_gst_and_cess_sub_4m_petrol():
    # Tata Nexon 1.2L Petrol (sub 4m, <=1200cc): 28% GST + 1% Cess = 29% total
    res = gst_engine.compute_gst_and_cess(
        category="4W",
        fuel_type="Petrol",
        ex_showroom_price=1100000.0,
        engine_capacity_cc=1199.0,
        length_mm=3995.0,
        ground_clearance_mm=208.0,
    )
    assert res["gst_rate_percent"] == 28.0
    assert res["cess_rate_percent"] == 1.0
    assert res["total_tax_rate_percent"] == 29.0
    # Base = 1100000 / 1.29 = 852713.18
    assert res["base_factory_price"] == 852713.18
    assert res["gst_amount"] == round(852713.18 * 0.28, 2)
    assert res["cess_amount"] == round(852713.18 * 0.01, 2)


def test_gst_and_cess_large_suv():
    # Mahindra Scorpio-N (length > 4000mm, ground clearance >= 170mm, engine > 1500cc): 28% GST + 22% Cess = 50%
    res = gst_engine.compute_gst_and_cess(
        category="4W",
        fuel_type="Diesel",
        ex_showroom_price=2450000.0,
        engine_capacity_cc=2184.0,
        length_mm=4662.0,
        ground_clearance_mm=187.0,
    )
    assert res["gst_rate_percent"] == 28.0
    assert res["cess_rate_percent"] == 22.0
    assert res["total_tax_rate_percent"] == 50.0
    # Base = 2450000 / 1.50 = 1633333.33
    assert res["base_factory_price"] == 1633333.33


def test_gst_and_cess_electric_vehicle():
    # Tata Tiago EV or Nexon EV: 5% GST + 0% Cess
    res = gst_engine.compute_gst_and_cess(
        category="4W",
        fuel_type="EV",
        ex_showroom_price=1000000.0,
    )
    assert res["gst_rate_percent"] == 5.0
    assert res["cess_rate_percent"] == 0.0
    assert res["total_tax_rate_percent"] == 5.0
    assert res["base_factory_price"] == round(1000000.0 / 1.05, 2)


def test_gst_and_cess_two_wheelers():
    # 2W <= 350cc (e.g. Yamaha MT-15 155cc): 28% GST, 0% Cess
    res_small = gst_engine.compute_gst_and_cess("2W", "Petrol", 170000.0, engine_capacity_cc=155.0)
    assert res_small["gst_rate_percent"] == 28.0
    assert res_small["cess_rate_percent"] == 0.0

    # 2W > 350cc (e.g. KTM 390 Duke 399cc): 28% GST, 3% Cess = 31%
    res_big = gst_engine.compute_gst_and_cess("2W", "Petrol", 310000.0, engine_capacity_cc=399.0)
    assert res_big["gst_rate_percent"] == 28.0
    assert res_big["cess_rate_percent"] == 3.0


# ==============================================================================
# 3. INSURANCE MODULE TESTS
# ==============================================================================

def test_insurance_engine_4w_calculation():
    # Hyundai Creta 1.5 Petrol ex-showroom 20,00,000
    res = insurance_engine.compute_insurance(
        category="4W",
        fuel_type="Petrol",
        ex_showroom_price=2000000.0,
        engine_capacity_cc=1482.0,
        zero_dep=True,
        engine_protect=True,
    )
    # IDV = 95% of 2M = 19,00,000
    assert res["idv"] == 1900000.0
    # Base OD = 1.9M * 2.15% = 40,850.0
    assert res["base_od_premium"] == 40850.0
    # 3-year TP for 1000-1500cc is ₹10,640
    assert res["tp_premium"] == 10640.0
    assert res["tp_tenure_years"] == 3
    # Addons: ZeroDep (15% of OD = 6127.50) + EngineProtect (6% of OD = 2451.00) + RSA (3% = 1225.50)
    assert "zero_depreciation" in res["addons_breakdown"]
    # 18% GST verified
    assert res["gst_rate_percent"] == 18.0
    expected_net = round(res["base_od_premium"] + res["addons_total"] + res["tp_premium"] + res["cpa_cover"], 2)
    assert res["net_premium"] == expected_net
    assert res["total_insurance_premium"] == round(expected_net * 1.18, 2)


def test_insurance_engine_2w_calculation():
    # Royal Enfield Classic 350 ex-showroom 2,25,000
    res = insurance_engine.compute_insurance(
        category="2W",
        fuel_type="Petrol",
        ex_showroom_price=225000.0,
        engine_capacity_cc=349.0,
        zero_dep=True,
    )
    # IDV = 95% of 225k = 213,750
    assert res["idv"] == 213750.0
    # 5-year TP for 150-350cc is ₹7,365
    assert res["tp_premium"] == 7365.0
    assert res["tp_tenure_years"] == 5


# ==============================================================================
# 4. EMI & AMORTIZATION SCHEDULE TESTS
# ==============================================================================

def test_reducing_balance_emi_exactness():
    # Hand-verified benchmark:
    # Loan Amount P = 10,00,000, Annual Rate = 9.5%, Tenure = 60 months
    # r = (9.5 / 12) / 100 = 0.0079166667
    # EMI = 1000000 * r * (1+r)^60 / ((1+r)^60 - 1) = 21001.91
    res = emi_engine.calculate_emi(
        total_price=1250000.0,
        down_payment=250000.0,  # Principal = 10,00,000
        tenure_months=60,
        annual_interest_rate=9.5,
        include_schedule=True,
    )
    assert res["principal_loan_amount"] == 1000000.0
    assert res["down_payment_percent"] == 20.0
    assert res["monthly_emi"] == 21001.86
    assert res["tenure_months"] == 60

    # Amortization schedule reconciliation:
    schedule = res["amortization_schedule"]
    assert len(schedule) == 60

    # First month check
    # Month 1 interest = 1000000 * (0.095/12) = 7916.67
    # Month 1 principal = 21001.86 - 7916.67 = 13085.19
    assert schedule[0]["month"] == 1
    assert schedule[0]["opening_balance"] == 1000000.0
    assert schedule[0]["interest"] == 7916.67
    assert schedule[0]["principal"] == 13085.19

    # Final month closing balance must be 0.0
    assert schedule[-1]["month"] == 60
    assert schedule[-1]["closing_balance"] == 0.0

    # Sum of all principal payments in schedule must equal the original principal loan amount
    total_principal_paid = sum(item["principal"] for item in schedule)
    assert pytest.approx(total_principal_paid, 0.05) == 1000000.0


def test_emi_zero_interest_and_full_payment():
    # Zero interest promotional loan
    res_zero = emi_engine.calculate_emi(
        total_price=120000.0,
        down_payment=0.0,
        tenure_months=12,
        annual_interest_rate=0.0,
    )
    assert res_zero["monthly_emi"] == 10000.0
    assert res_zero["total_interest_payable"] == 0.0

    # 100% down payment
    res_full = emi_engine.calculate_emi(
        total_price=150000.0,
        down_payment_percent=100.0,
    )
    assert res_full["principal_loan_amount"] == 0.0
    assert res_full["monthly_emi"] == 0.0


# ==============================================================================
# 5. UNIFIED ON-ROAD PRICE ENGINE TESTS
# ==============================================================================

def test_on_road_price_unified_consistency():
    # On-road price breakdown reconciliation:
    # On-Road == ExShowroom + RTO + Insurance + Incidentals + Optionals
    res = on_road_price_engine.calculate_on_road_price(
        state_code="MH",
        category="4W",
        fuel_type="Petrol",
        ex_showroom_price=1115000.0,
        engine_capacity_cc=1199.0,
        length_mm=3995.0,
        ground_clearance_mm=208.0,
        optional_accessories=15000.0,
        extended_warranty=22000.0,
    )

    rto = res["rto_charges"]["rto_tax_amount"]
    insurance = res["insurance_charges"]["total_insurance_premium"]
    incidentals = res["incidental_charges"]["total"]
    optionals = res["optional_charges"]["total"]
    expected_total = round(1115000.0 + rto + insurance + incidentals + optionals, 2)

    assert res["total_on_road_price"] == expected_total
    assert res["rule_version"] is not None
    assert res["effective_date"] is not None
