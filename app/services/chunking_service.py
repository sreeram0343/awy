import hashlib
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from uuid import UUID


VALID_TOPICS = {"performance", "comfort", "reliability", "service_cost"}

TOPIC_PATTERNS = {
    "performance": [
        r"(?:engine|acceleration|pickup|throttle|torque|power|speed|gearbox|transmission|handling|braking|abs|braking distance|high speed stability|cornering)",
        r"(?:mileage|fuel efficiency|range|battery drain|kmpl|wh/km)",
    ],
    "comfort": [
        r"(?:suspension|ride quality|seat comfort|ergonomics|cushioning|nvh|noise|cabin insulation|vibration|legroom|headroom|air conditioning|ventilated seats|infotainment)",
    ],
    "reliability": [
        r"(?:reliability|breakdown|niggle|defect|fit and finish|rattle|paint quality|sensor failure|build quality|battery degradation|motor issue|electronics)",
    ],
    "service_cost": [
        r"(?:service cost|maintenance|spare parts|parts availability|dealership experience|annual maintenance|repair cost|scheduled service|warranty claim|labor charges)",
    ],
}


@dataclass
class ReviewChunk:
    chunk_hash: str
    vehicle_id: str
    variant_id: Optional[str]
    topic: str
    content: str
    source: str
    rating: Optional[float]
    source_version: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ReviewChunker:
    """
    Topic-based semantic chunker for automotive reviews.
    Chunks content semantically by automotive evaluation topics:
    - performance
    - comfort
    - reliability
    - service_cost
    """

    @staticmethod
    def compute_hash(vehicle_id: str, topic: str, content: str) -> str:
        """Compute deterministic SHA-256 hash for chunk idempotency."""
        normalized_content = " ".join(content.strip().lower().split())
        raw_key = f"{vehicle_id}:{topic}:{normalized_content}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    @classmethod
    def chunk_structured_review(
        cls,
        vehicle_id: str,
        variant_id: Optional[str],
        topic: str,
        content: str,
        source: str,
        rating: Optional[float] = None,
        source_version: str = "v1.0",
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> ReviewChunk:
        """
        Creates a ReviewChunk for structured review sections with known topic.
        """
        topic_clean = topic.strip().lower()
        if topic_clean not in VALID_TOPICS:
            topic_clean = cls.classify_topic(content)

        chunk_hash = cls.compute_hash(vehicle_id, topic_clean, content)
        meta = extra_metadata.copy() if extra_metadata else {}
        meta.update({
            "vehicle_id": vehicle_id,
            "variant_id": variant_id,
            "topic": topic_clean,
            "source": source,
            "rating": rating,
            "source_version": source_version,
            "chunk_hash": chunk_hash,
        })

        return ReviewChunk(
            chunk_hash=chunk_hash,
            vehicle_id=vehicle_id,
            variant_id=variant_id,
            topic=topic_clean,
            content=content.strip(),
            source=source,
            rating=rating,
            source_version=source_version,
            metadata=meta,
        )

    @classmethod
    def classify_topic(cls, text: str) -> str:
        """Classify unstructured text snippet into one of the 4 canonical topics."""
        text_lower = text.lower()
        scores = {t: 0 for t in VALID_TOPICS}

        for topic, patterns in TOPIC_PATTERNS.items():
            for pat in patterns:
                matches = re.findall(pat, text_lower)
                scores[topic] += len(matches)

        best_topic = max(scores, key=scores.get)
        return best_topic if scores[best_topic] > 0 else "comfort"

    @classmethod
    def parse_long_review(
        cls,
        raw_text: str,
        vehicle_id: str,
        variant_id: Optional[str],
        source: str,
        rating: Optional[float] = None,
        source_version: str = "v1.0",
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[ReviewChunk]:
        """
        Parse multi-section review text by topic headers (e.g. '### Performance', 'Comfort:', etc.)
        or paragraph-level semantic clustering.
        """
        chunks: List[ReviewChunk] = []
        sections = re.split(r"\n+(?=[#A-Z][A-Za-z\s\-/]+:|\b(?:Performance|Ride & Handling|Comfort & Ergonomics|Reliability|Maintenance & Service Cost)\b)", raw_text)

        for section in sections:
            clean_sec = section.strip()
            if not clean_sec or len(clean_sec) < 30:
                continue

            topic = cls.classify_topic(clean_sec)
            chunk = cls.chunk_structured_review(
                vehicle_id=vehicle_id,
                variant_id=variant_id,
                topic=topic,
                content=clean_sec,
                source=source,
                rating=rating,
                source_version=source_version,
                extra_metadata=extra_metadata,
            )
            chunks.append(chunk)

        return chunks
