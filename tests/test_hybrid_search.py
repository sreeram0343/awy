import time
import pytest
from app.schemas.search import HybridSearchRequest, FilterConstraint
from app.services.hybrid_search_service import hybrid_search_service
from app.services.query_parser import QueryParser


BENCHMARK_QUERIES = [
    # 1. Hard-filter queries with strict constraints
    {
        "query": "bikes with dual-channel ABS under ₹2L",
        "expected_category": "2W",
        "expected_abs": ["Dual-Channel", "Cornering ABS"],
        "max_price_ceiling": 200000.0,
        "must_include_any": ["Hunter 350", "MT-15 V2", "Apache RTR 160 4V"],
        "forbidden_models": ["Scorpio-N", "Creta", "Activa 6G", "Nexon"],
    },
    {
        "query": "suvs with 5 star ncap under 15 lakh",
        "expected_category": "4W",
        "expected_min_ncap": 5,
        "max_price_ceiling": 1500000.0,
        "must_include_any": ["Nexon", "Punch"],
        "forbidden_models": ["Swift", "Activa 6G", "390 Duke"],
    },
    {
        "query": "electric scooter with high range under 1.6 lakh",
        "expected_category": "2W",
        "expected_fuel": "EV",
        "must_include_any": ["450X"],
        "forbidden_models": ["Classic 350", "City", "Scorpio-N"],
    },
    {
        "query": "strong hybrid cars under 35 lakhs",
        "expected_category": "4W",
        "expected_fuel": "Hybrid",
        "must_include_any": ["Innova Hycross"],
        "forbidden_models": ["Swift", "Hunter 350", "Classic 350"],
    },
    {
        "query": "diesel 4wd suv under 26 lakh",
        "expected_category": "4W",
        "expected_fuel": "Diesel",
        "must_include_any": ["Scorpio-N"],
        "forbidden_models": ["Swift", "Activa 6G", "Hunter 350"],
    },
    {
        "query": "petrol hatchback with automatic transmission under 10.5 lakh",
        "expected_category": "4W",
        "expected_fuel": "Petrol",
        "must_include_any": ["Swift", "i20"],
        "forbidden_models": ["Scorpio-N", "390 Duke"],
    },
    {
        "query": "motorcycle with cornering abs",
        "expected_category": "2W",
        "expected_abs": ["Cornering ABS"],
        "must_include_any": ["390 Duke"],
        "forbidden_models": ["Activa 6G", "City"],
    },
    {
        "query": "cruiser motorcycle under 2.5 lakh",
        "expected_category": "2W",
        "max_price_ceiling": 250000.0,
        "must_include_any": ["Classic 350", "Hunter 350"],
        "forbidden_models": ["Innova Hycross", "Scorpio-N"],
    },
    {
        "query": "electric car under 18 lakh with good safety",
        "expected_category": "4W",
        "expected_fuel": "EV",
        "must_include_any": ["Nexon", "Windsor EV", "Tiago EV"],
        "forbidden_models": ["Classic 350", "390 Duke"],
    },
    {
        "query": "7 seater suv under 25 lakh",
        "expected_category": "4W",
        "max_price_ceiling": 2500000.0,
        "must_include_any": ["Scorpio-N", "XUV700"],
        "forbidden_models": ["MT-15 V2", "Activa 6G", "Swift"],
    },

    # 2. Exact Technical Term Queries
    {
        "query": "Creta Turbo DCT 7 speed dual clutch",
        "must_include_any": ["Creta"],
        "forbidden_models": ["Classic 350", "Swift"],
    },
    {
        "query": "Royal Enfield Classic 350 counterbalanced J series engine",
        "must_include_any": ["Classic 350"],
        "forbidden_models": ["Creta", "Innova Hycross"],
    },
    {
        "query": "Yamaha Variable Valve Actuation VVA assist and slipper clutch",
        "must_include_any": ["MT-15 V2"],
        "forbidden_models": ["Activa 6G", "Nexon"],
    },
    {
        "query": "Ather Warp mode 0-40 fast acceleration",
        "must_include_any": ["450X"],
        "forbidden_models": ["Brezza", "Scorpio-N"],
    },
    {
        "query": "Honda Activa H-Smart keyless entry metal body",
        "must_include_any": ["Activa 6G"],
        "forbidden_models": ["390 Duke", "XUV700"],
    },
    {
        "query": "MG Windsor Aero Lounge seats 135 degree recline",
        "must_include_any": ["Windsor EV"],
        "forbidden_models": ["Raider 125", "Swift"],
    },
    {
        "query": "TVS Apache Glide Through Technology GTT",
        "must_include_any": ["Apache RTR 160 4V"],
        "forbidden_models": ["Creta", "City"],
    },
    {
        "query": "Honda City 1.5 i-VTEC sedan car high revving DOHC",
        "must_include_any": ["City"],
        "forbidden_models": ["MT-15 V2", "Hunter 350"],
    },
    {
        "query": "KTM 390 Duke motorcycle Quickshifter Plus bi-directional launch control",
        "must_include_any": ["390 Duke"],
        "forbidden_models": ["Activa 6G", "Tiago EV"],
    },
    {
        "query": "Toyota Innova ottoman captain seats TNGA",
        "must_include_any": ["Innova Hycross"],
        "forbidden_models": ["Punch", "Raider 125"],
    },

    # 3. Topic & Lifestyle Semantic Queries
    {
        "query": "lowest service maintenance cost daily commuter bike with high mileage",
        "expected_category": "2W",
        "must_include_any": ["Raider 125", "Apache RTR 160 4V", "Activa 6G", "Hunter 350"],
        "forbidden_models": ["Innova Hycross", "Scorpio-N"],
    },
    {
        "query": "plush rear lounge comfort for chauffeur driven travel",
        "expected_category": "4W",
        "must_include_any": ["Innova Hycross", "City", "Windsor EV", "Creta"],
        "forbidden_models": ["MT-15 V2", "390 Duke"],
    },
    {
        "query": "bulletproof reliability no mechanical problems over lakhs of kilometers",
        "must_include_any": ["Activa 6G", "City", "Innova Hycross", "Brezza"],
        "forbidden_models": [],
    },
    {
        "query": "rugged off-road mechanical locking differential hill climb",
        "expected_category": "4W",
        "must_include_any": ["Scorpio-N"],
        "forbidden_models": ["Activa 6G", "Swift", "Tiago EV"],
    },
    {
        "query": "peppy electric city car runabout under 10 lakh for narrow lanes",
        "expected_category": "4W",
        "expected_fuel": "EV",
        "max_price_ceiling": 1050000.0,
        "must_include_any": ["Tiago EV"],
        "forbidden_models": ["Scorpio-N", "Innova Hycross"],
    },
    {
        "query": "pocket friendly running cost home charging electric scooter",
        "expected_category": "2W",
        "expected_fuel": "EV",
        "must_include_any": ["450X"],
        "forbidden_models": ["Classic 350", "Scorpio-N"],
    },
    {
        "query": "safe subcompact suv with 200mm ground clearance for bad roads",
        "expected_category": "4W",
        "must_include_any": ["Nexon", "Brezza", "Punch"],
        "forbidden_models": ["MT-15 V2", "City"],
    },
    {
        "query": "nimble streetfighter motorcycle for aggressive cornering",
        "expected_category": "2W",
        "must_include_any": ["MT-15 V2", "390 Duke"],
        "forbidden_models": ["Activa 6G", "Innova Hycross"],
    },
    {
        "query": "legendary reliability automatic family scooter with metal body",
        "expected_category": "2W",
        "must_include_any": ["Activa 6G"],
        "forbidden_models": ["390 Duke", "Nexon"],
    },
    {
        "query": "premium mid-size suv with level 2 ADAS and dual screens",
        "expected_category": "4W",
        "must_include_any": ["XUV700", "Creta"],
        "forbidden_models": ["Activa 6G", "Hunter 350"],
    },

    # 4. Strict Negative Constraint Tests
    {
        "query": "cars under 2 lakh",
        "expected_category": "4W",
        "max_price_ceiling": 200000.0,
        "must_be_empty": True,
    },
    {
        "query": "motorcycles with 6 airbags",
        "expected_category": "2W",
        "must_be_empty": True,
    },
    {
        "query": "diesel scooter under 1 lakh",
        "expected_category": "2W",
        "expected_fuel": "Diesel",
        "must_be_empty": True,
    },
    {
        "query": "5 star ncap safety rating scooter",
        "expected_category": "2W",
        "expected_min_ncap": 5,
        "must_be_empty": True,
    },
    {
        "query": "4-wheeler under 50 thousand",
        "expected_category": "4W",
        "max_price_ceiling": 50000.0,
        "must_be_empty": True,
    },
]


@pytest.mark.asyncio
async def test_query_parser_rule_extraction():
    """Verify natural language filter extraction accuracy."""
    c1 = QueryParser.parse_query("bikes with dual-channel ABS under ₹2L")
    assert c1.category == "2W"
    assert c1.abs_type == "Dual-Channel"
    assert c1.max_price == 200000.0

    c2 = QueryParser.parse_query("suvs with 5 star ncap under 15 lakh")
    assert c2.category == "4W"
    assert c2.body_type == "SUV"
    assert c2.min_ncap_rating == 5
    assert c2.max_price == 1500000.0

    c3 = QueryParser.parse_query("electric car over 20 lakhs")
    assert c3.category == "4W"
    assert c3.fuel_type == "EV"
    assert c3.min_price == 2000000.0


@pytest.mark.asyncio
async def test_hybrid_search_benchmark_suite():
    """
    Acceptance Criteria:
    - 35 representative queries pass with >90% precision on hard-filter queries.
    - Latency budget: <150ms p95 for hybrid search end-to-end.
    """
    # Warm up model and index before measuring latency
    await hybrid_search_service.search(HybridSearchRequest(query="warmup test", top_k=1))

    total_queries = len(BENCHMARK_QUERIES)
    passed_precision = 0
    latencies_ms = []

    for test_case in BENCHMARK_QUERIES:
        q_text = test_case["query"]
        t0 = time.perf_counter()

        req = HybridSearchRequest(query=q_text, top_k=5)
        res = await hybrid_search_service.search(req)

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        latencies_ms.append(elapsed_ms)

        # Negative test handling (should return zero results)
        if test_case.get("must_be_empty"):
            assert res.total_matches == 0, f"Expected 0 matches for '{q_text}', got {res.total_matches}"
            passed_precision += 1
            continue

        results = res.results
        assert len(results) > 0, f"Query '{q_text}' returned no results"

        # Check hard constraints across returned results
        models_returned = [r.vehicle_model for r in results]
        case_passed = True

        # Category check
        if "expected_category" in test_case:
            for r in results:
                if r.metadata.get("category") != test_case["expected_category"]:
                    case_passed = False
                    break

        # Fuel check
        if "expected_fuel" in test_case:
            for r in results:
                if r.metadata.get("fuel_type") != test_case["expected_fuel"]:
                    case_passed = False
                    break

        # ABS check
        if "expected_abs" in test_case:
            for r in results:
                abs_val = r.metadata.get("abs_type")
                if abs_val not in test_case["expected_abs"]:
                    case_passed = False
                    break

        # NCAP check
        if "expected_min_ncap" in test_case:
            for r in results:
                ncap_val = r.metadata.get("ncap_rating")
                if not ncap_val or ncap_val < test_case["expected_min_ncap"]:
                    case_passed = False
                    break

        # Price ceiling check
        if "max_price_ceiling" in test_case:
            for r in results:
                min_p = r.metadata.get("min_price")
                if min_p and min_p > test_case["max_price_ceiling"]:
                    case_passed = False
                    break

        # Target model presence check
        if "must_include_any" in test_case and test_case["must_include_any"]:
            if not any(m in models_returned for m in test_case["must_include_any"]):
                case_passed = False

        # Forbidden models check
        if "forbidden_models" in test_case:
            for forb in test_case["forbidden_models"]:
                if forb in models_returned:
                    case_passed = False
                    break

        if case_passed:
            passed_precision += 1
        else:
            print(f"FAILED CASE for query: '{q_text}' -> Returned models: {models_returned}")

    precision = (passed_precision / total_queries) * 100.0

    # Calculate p95 latency
    latencies_sorted = sorted(latencies_ms)
    p95_index = int(0.95 * len(latencies_sorted))
    p95_latency = latencies_sorted[p95_index]
    avg_latency = sum(latencies_ms) / len(latencies_ms)

    print(f"\n==========================================")
    print(f"HYBRID SEARCH BENCHMARK RESULTS:")
    print(f"  Total Queries: {total_queries}")
    print(f"  Passed Queries: {passed_precision}")
    print(f"  Hard-Filter Precision: {precision:.1f}%")
    print(f"  Average Latency: {avg_latency:.2f}ms")
    print(f"  P95 Latency: {p95_latency:.2f}ms")
    print(f"==========================================")

    # Acceptance Criteria checks
    assert precision >= 90.0, f"Precision was {precision:.1f}%, expected >= 90.0%"
    assert p95_latency < 150.0, f"P95 latency was {p95_latency:.2f}ms, expected < 150ms"
