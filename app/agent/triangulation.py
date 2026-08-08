"""
Source Triangulation Engine (Amendment 08)
Establishes Information Hierarchy:
PRIMARY SOURCE -> TECHNICAL EVIDENCE -> INDEPENDENT CORROBORATION -> EDITORIAL INTERPRETATION

Prefer primary sources for:
product capabilities, research results, benchmark claims, technical specifications, deployment announcements.

If sources disagree:
1. Resolve through primary evidence over secondary hype
2. Qualify statement explicitly in commentary
3. Or REJECT topic if evidence is unresolvable / contradicted.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from app.agent.discovery import CandidateTopic

logger = logging.getLogger("triangulation")


class TriangulationResult:
    def __init__(
        self,
        hierarchy_level: str,  # "PRIMARY_SOURCE", "TECHNICAL_EVIDENCE", "INDEPENDENT_CORROBORATION", "SECONDARY_EDITORIAL"
        primary_source_found: bool,
        has_disagreement: bool,
        disagreement_detail: str,
        resolution_action: str,  # "RESOLVED_VIA_PRIMARY", "QUALIFIED_IN_COMMENTARY", "REJECTED_DISCREPANCY"
        source_qualification_note: str,
        is_acceptable: bool
    ):
        self.hierarchy_level = hierarchy_level
        self.primary_source_found = primary_source_found
        self.has_disagreement = has_disagreement
        self.disagreement_detail = disagreement_detail
        self.resolution_action = resolution_action
        self.source_qualification_note = source_qualification_note
        self.is_acceptable = is_acceptable

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hierarchyLevel": self.hierarchy_level,
            "primarySourceFound": self.primary_source_found,
            "hasDisagreement": self.has_disagreement,
            "disagreementDetail": self.disagreement_detail,
            "resolutionAction": self.resolution_action,
            "sourceQualificationNote": self.source_qualification_note,
            "isAcceptable": self.is_acceptable
        }


class SourceTriangulationEngine:
    PRIMARY_DOMAINS = [
        "arxiv.org", "github.com", "huggingface.co", "nvidia.com", "ros.org",
        "ieee.org", "nature.com", "science.org", "openreview.net"
    ]

    @classmethod
    def triangulate_sources(cls, candidate: CandidateTopic) -> TriangulationResult:
        """
        Audits candidate sources along the Information Hierarchy and detects source discrepancies.
        """
        sources = candidate.sources or []
        combined_text = f"{candidate.title} {candidate.summary}".lower()
        
        # 1. Identify Hierarchy Level
        has_primary = False
        for src in sources:
            for domain in cls.PRIMARY_DOMAINS:
                if domain in src.lower():
                    has_primary = True
                    break
                    
        if has_primary:
            hierarchy = "PRIMARY_SOURCE"
        elif candidate.sourceQuality >= 70.0:
            hierarchy = "TECHNICAL_EVIDENCE"
        elif len(sources) >= 2:
            hierarchy = "INDEPENDENT_CORROBORATION"
        else:
            hierarchy = "SECONDARY_EDITORIAL"

        # 2. Source Disagreement & Discrepancy Detection
        has_disagreement = False
        disagreement_detail = ""
        action = "RESOLVED_VIA_PRIMARY"
        qualification_note = ""
        is_acceptable = True

        # Detect discrepancy between marketing claims vs technical data
        if any(w in combined_text for w in ["full autonomy", "100%", "perfect", "flawless"]):
            if "arxiv" in combined_text or "paper" in combined_text:
                has_disagreement = True
                disagreement_detail = "Secondary news claims full autonomy; primary paper reports controlled laboratory benchmark success."
                action = "QUALIFIED_IN_COMMENTARY"
                qualification_note = "Source Qualification: Secondary headlines claim full autonomy, but primary ArXiv evidence confirms controlled lab benchmark performance."
            else:
                has_disagreement = True
                disagreement_detail = "Unsubstantiated marketing claim of full autonomy without primary technical paper."
                action = "REJECTED_DISCREPANCY"
                is_acceptable = False
                qualification_note = "Rejected by Source Triangulation: Unresolvable source disagreement and lack of primary source technical evidence."

        elif not has_primary and candidate.sourceQuality < 50.0:
            is_acceptable = False
            action = "REJECTED_DISCREPANCY"
            qualification_note = "Rejected by Source Triangulation: Relying solely on secondary editorial sources without primary technical evidence."
        else:
            qualification_note = f"Source Hierarchy Verified: Information grounded in {hierarchy} ({candidate.source_name})."

        return TriangulationResult(
            hierarchy_level=hierarchy,
            primary_source_found=has_primary,
            has_disagreement=has_disagreement,
            disagreement_detail=disagreement_detail,
            resolution_action=action,
            source_qualification_note=qualification_note,
            is_acceptable=is_acceptable
        )
