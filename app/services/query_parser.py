import re
from typing import Optional, Dict, Any, Tuple
from pydantic import BaseModel
from app.schemas.search import FilterConstraint


class ExtractedConstraints(BaseModel):
    category: Optional[str] = None  # "2W" or "4W"
    max_price: Optional[float] = None
    min_price: Optional[float] = None
    fuel_type: Optional[str] = None
    abs_type: Optional[str] = None
    min_ncap_rating: Optional[int] = None
    min_airbags: Optional[int] = None
    body_type: Optional[str] = None
    clean_query: str = ""


class QueryParser:
    """
    Deterministic rule-based query understanding and constraint extraction engine.
    Extracts hard numeric, categorical, and safety constraints from free-text
    queries before semantic vector ranking.
    """

    # Price pattern matching (e.g. "under 2L", "below 15 lakhs", "< ₹2.5L", "under 50 thousand")
    PRICE_UNDER_PATTERNS = [
        r"(?:under|below|less than|within|budget of|max(?:imum)? of|\<|upto|up to)\s*(?:₹|rs\.?|inr)?\s*([0-9]+(?:\.[0-9]+)?)\s*(lakhs?|lacs?|lac|l|crores?|cr|thousands?|thousand|k)?",
        r"(?:₹|rs\.?|inr)\s*([0-9]+(?:\.[0-9]+)?)\s*(lakhs?|lacs?|lac|l|crores?|cr|thousands?|thousand|k)?\s*(?:budget|or less|max)",
    ]

    PRICE_ABOVE_PATTERNS = [
        r"(?:above|over|more than|greater than|\>|minimum of|at least)\s*(?:₹|rs\.?|inr)?\s*([0-9]+(?:\.[0-9]+)?)\s*(lakhs?|lacs?|lac|l|crores?|cr|thousands?|thousand|k)?",
    ]

    # Category cues
    TWO_WHEELER_KEYWORDS = [
        r"\b(?:bikes?|motorcycles?|scooters?|two[ -]?wheelers?|2[ -]?wheelers?|2w)\b",
    ]
    FOUR_WHEELER_KEYWORDS = [
        r"\b(?:cars?|suvs?|sedans?|hatchbacks?|four[ -]?wheelers?|4[ -]?wheelers?|4w|mpvs?|cuvs?|chauffeur|chauffeur driven|family car)\b",
    ]

    # ABS cues
    ABS_PATTERNS = {
        "Cornering ABS": r"\b(?:cornering abs|cornering anti-lock)\b",
        "Dual-Channel": r"\b(?:dual[ -]?channel abs|dual abs|twin channel abs|2[ -]?channel abs)\b",
        "Single-Channel": r"\b(?:single[ -]?channel abs|single abs|1[ -]?channel abs)\b",
    }

    # NCAP cues
    NCAP_PATTERNS = [
        r"\b([3-5])[ -]?(?:star|stars)\s*(?:safety|ncap|global ncap|bharat ncap)?\b",
        r"\b(?:safety rating|ncap rating|ncap)\s*(?:of|at least)?\s*([3-5])\b",
    ]

    # Airbag cues
    AIRBAG_PATTERNS = [
        r"\b([0-9]+)\s*(?:airbags?)\b",
        r"\b(?:six)\s*(?:airbags?)\b",
    ]

    # Fuel type cues
    FUEL_PATTERNS = {
        "EV": r"\b(?:evs?|electric|battery electric|bev|home charging|charging|battery)\b",
        "Diesel": r"\b(?:diesel)\b",
        "Hybrid": r"\b(?:hybrids?|strong hybrid|e-cvt)\b",
        "CNG": r"\b(?:cng)\b",
        "Petrol": r"\b(?:petrol|gasoline)\b",
    }

    # Body type cues
    BODY_PATTERNS = {
        "SUV": r"\b(?:suvs?|compact suv|micro suv)\b",
        "Sedan": r"\b(?:sedans?)\b",
        "Hatchback": r"\b(?:hatchbacks?|hatches?)\b",
        "Cruiser": r"\b(?:cruisers?|retro cruiser)\b",
        "Scooter": r"\b(?:scooters?|scooty)\b",
        "Streetfighter": r"\b(?:streetfighters?|naked bike|naked streetfighter)\b",
        "Commuter": r"\b(?:commuters?|commuter bike)\b",
        "MPV": r"\b(?:mpvs?|people mover|7 seater)\b",
    }

    @classmethod
    def _parse_price_value(cls, num_str: str, unit_str: Optional[str]) -> float:
        val = float(num_str)
        if not unit_str:
            # If large number like 200000, keep as is; if 2, interpret as 2L in Indian context
            if val < 100:
                return val * 100000.0
            return val

        unit = unit_str.lower().strip()
        if unit in ("l", "lac", "lacs", "lakh", "lakhs"):
            return val * 100000.0
        elif unit in ("cr", "crore", "crores"):
            return val * 10000000.0
        elif unit in ("k", "thousand", "thousands"):
            return val * 1000.0
        return val

    @classmethod
    def parse_query(
        cls,
        query: str,
        explicit_category: Optional[str] = None,
        explicit_filters: Optional[FilterConstraint] = None,
    ) -> ExtractedConstraints:
        """
        Parse raw query and extract hard constraints.
        Explicit filters override or merge with parsed ones.
        """
        q_lower = query.lower()
        extracted = ExtractedConstraints(clean_query=query.strip())

        # 1. Category extraction
        if explicit_category:
            extracted.category = explicit_category.upper()
        else:
            for pat in cls.TWO_WHEELER_KEYWORDS:
                if re.search(pat, q_lower):
                    extracted.category = "2W"
                    break
            if not extracted.category:
                for pat in cls.FOUR_WHEELER_KEYWORDS:
                    if re.search(pat, q_lower):
                        extracted.category = "4W"
                        break

        # 2. Price ceilings (max_price)
        for pat in cls.PRICE_UNDER_PATTERNS:
            match = re.search(pat, q_lower)
            if match:
                groups = match.groups()
                num_str = groups[0]
                unit_str = groups[1] if len(groups) > 1 else None
                extracted.max_price = cls._parse_price_value(num_str, unit_str)
                break

        # Price floors (min_price)
        for pat in cls.PRICE_ABOVE_PATTERNS:
            match = re.search(pat, q_lower)
            if match:
                groups = match.groups()
                num_str = groups[0]
                unit_str = groups[1] if len(groups) > 1 else None
                extracted.min_price = cls._parse_price_value(num_str, unit_str)
                break

        # 3. ABS extraction
        for abs_label, pat in cls.ABS_PATTERNS.items():
            if re.search(pat, q_lower):
                extracted.abs_type = abs_label
                break

        # 4. NCAP rating extraction
        for pat in cls.NCAP_PATTERNS:
            match = re.search(pat, q_lower)
            if match:
                extracted.min_ncap_rating = int(match.group(1))
                break

        # Airbag extraction
        for pat in cls.AIRBAG_PATTERNS:
            match = re.search(pat, q_lower)
            if match:
                val = match.group(0)
                if "six" in val:
                    extracted.min_airbags = 6
                else:
                    extracted.min_airbags = int(match.group(1))
                break

        # 5. Fuel type extraction
        for fuel_label, pat in cls.FUEL_PATTERNS.items():
            if re.search(pat, q_lower):
                extracted.fuel_type = fuel_label
                break

        # 6. Body type extraction
        for body_label, pat in cls.BODY_PATTERNS.items():
            if re.search(pat, q_lower):
                extracted.body_type = body_label
                break

        # Apply explicit filters if provided
        if explicit_filters:
            if explicit_filters.max_price is not None:
                extracted.max_price = explicit_filters.max_price
            if explicit_filters.min_price is not None:
                extracted.min_price = explicit_filters.min_price
            if explicit_filters.fuel_type:
                extracted.fuel_type = explicit_filters.fuel_type
            if explicit_filters.abs_type:
                extracted.abs_type = explicit_filters.abs_type
            if explicit_filters.min_ncap_rating is not None:
                extracted.min_ncap_rating = explicit_filters.min_ncap_rating
            if explicit_filters.min_airbags is not None:
                extracted.min_airbags = explicit_filters.min_airbags
            if explicit_filters.body_type:
                extracted.body_type = explicit_filters.body_type

        return extracted
