"""
Rule-based / regex entity extraction over parsed document text.

This intentionally avoids depending on a heavyweight NER model so the
system runs anywhere Tesseract + OpenCV already run. Patterns are tuned for
industrial maintenance/inspection/SOP documents. Each extracted entity
carries a confidence score derived from pattern specificity + context.
"""
import re
from dataclasses import dataclass, asdict
from typing import List

EQUIPMENT_ID_PATTERN = re.compile(r"\b([A-Z]{1,4}-\d{2,5}[A-Z]?)\b")
PRESSURE_PATTERN = re.compile(r"\b(\d{1,4}(?:\.\d+)?)\s?(bar|psi|kpa|mpa)\b", re.IGNORECASE)
TEMPERATURE_PATTERN = re.compile(r"\b(-?\d{1,4}(?:\.\d+)?)\s?°?\s?(c|f|celsius|fahrenheit)\b", re.IGNORECASE)
DATE_PATTERN = re.compile(
    r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2}|"
    r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4})\b",
    re.IGNORECASE,
)
ENGINEER_PATTERN = re.compile(
    r"\b(?:engineer|inspector|technician|supervisor|prepared by|reviewed by|approved by)[:\s]+([A-Z][a-zA-Z.\s]{2,40})",
    re.IGNORECASE,
)
DEPARTMENT_PATTERN = re.compile(
    r"\b(?:department|dept\.?)[:\s]+([A-Za-z &]{3,60})", re.IGNORECASE
)
PLANT_PATTERN = re.compile(
    r"\b(?:plant|facility|unit)[:\s]+([A-Za-z0-9 &-]{3,60})", re.IGNORECASE
)
LOCATION_PATTERN = re.compile(
    r"\b(?:location)[:\s]+([A-Za-z0-9 ,&-]{3,80})", re.IGNORECASE
)
REGULATION_PATTERN = re.compile(
    r"\b(OISD[-\s]?\d{3,4}|PESO[-\s]?[A-Z0-9]{2,10}|ISO[-\s]?\d{3,5}(?::\d{4})?|"
    r"Factory Act[,\s]*\d{4}?)\b",
    re.IGNORECASE,
)
FAILURE_KEYWORDS = re.compile(
    r"((?:leak(?:age)?|failure|breakdown|malfunction|corrosion|crack(?:ed)?|overheat(?:ing)?|"
    r"vibration|seizure|short[- ]circuit|blockage|worn|fatigue)[^.\n]{0,120})",
    re.IGNORECASE,
)
SAFETY_RULE_PATTERN = re.compile(
    r"((?:must|shall|should|is required to|mandatory)[^.\n]{5,150})",
    re.IGNORECASE,
)
INSPECTION_FINDING_PATTERN = re.compile(
    r"((?:finding|observed|noted that|deficiency)[:\s][^.\n]{5,150})",
    re.IGNORECASE,
)


@dataclass
class Entity:
    entity_type: str
    entity_value: str
    confidence_score: float
    context_snippet: str


def _snippet(text: str, match: re.Match, radius: int = 60) -> str:
    start = max(match.start() - radius, 0)
    end = min(match.end() + radius, len(text))
    return text[start:end].replace("\n", " ").strip()


def extract_entities(text: str) -> List[dict]:
    if not text:
        return []

    entities: List[Entity] = []

    def add_all(pattern, entity_type, confidence, group=1):
        for m in pattern.finditer(text):
            value = m.group(group) if m.groups() else m.group(0)
            entities.append(Entity(
                entity_type=entity_type,
                entity_value=value.strip(),
                confidence_score=confidence,
                context_snippet=_snippet(text, m),
            ))

    add_all(EQUIPMENT_ID_PATTERN, "EQUIPMENT_ID", 0.9, group=1)
    add_all(PRESSURE_PATTERN, "PRESSURE", 0.85, group=0)
    add_all(TEMPERATURE_PATTERN, "TEMPERATURE", 0.85, group=0)
    add_all(DATE_PATTERN, "MAINTENANCE_DATE", 0.75, group=0)
    add_all(ENGINEER_PATTERN, "ENGINEER", 0.7, group=1)
    add_all(DEPARTMENT_PATTERN, "DEPARTMENT", 0.65, group=1)
    add_all(PLANT_PATTERN, "PLANT", 0.65, group=1)
    add_all(LOCATION_PATTERN, "LOCATION", 0.6, group=1)
    add_all(REGULATION_PATTERN, "REGULATORY_REFERENCE", 0.85, group=0)
    add_all(FAILURE_KEYWORDS, "FAILURE_REASON", 0.6, group=0)
    add_all(SAFETY_RULE_PATTERN, "SAFETY_RULE", 0.55, group=0)
    add_all(INSPECTION_FINDING_PATTERN, "INSPECTION_FINDING", 0.6, group=0)

    # De-duplicate identical (type, value) pairs, keep highest confidence
    dedup = {}
    for e in entities:
        key = (e.entity_type, e.entity_value.lower())
        if key not in dedup or e.confidence_score > dedup[key].confidence_score:
            dedup[key] = e

    return [asdict(e) for e in dedup.values()]
