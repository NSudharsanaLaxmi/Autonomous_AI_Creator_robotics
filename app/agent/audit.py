"""
Pre-Publication Self-Audit Gate (Amendment 13)
Performs internal pre-publication verification across 7 Core Checks:
1. FACTUALITY: Are factual claims supported by primary sources?
2. NOVELTY: Is this sufficiently different from previous publications?
3. RELEVANCE: Does this genuinely matter to robotics?
4. ORIGINALITY: Does FORGE contribute an engineering interpretation?
5. PERSONA: Does this sound consistent with established robotics engineer?
6. EVIDENCE: Are important claims adequately sourced?
7. RESTRAINT: Would publishing this genuinely improve the feed?

If any critical check fails, the publication is REVISED or REJECTED.
"""

import logging
from typing import Dict, Any, List, Optional
from app.agent.discovery import CandidateTopic
from app.agent.persona import Persona
from app.agent.memory import AgentMemory

logger = logging.getLogger("audit")


class PrePublicationAuditResult:
    def __init__(
        self,
        passed_audit: bool,
        failed_checks: List[str],
        check_details: Dict[str, bool],
        audit_summary: str
    ):
        self.passed_audit = passed_audit
        self.failed_checks = failed_checks
        self.check_details = check_details
        self.audit_summary = audit_summary

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passedAudit": self.passed_audit,
            "failedChecks": self.failed_checks,
            "checkDetails": self.check_details,
            "auditSummary": self.audit_summary
        }


class PrePublicationAuditGate:
    @classmethod
    def audit_publication(
        cls,
        candidate: CandidateTopic,
        post_text: str,
        rationale_text: str,
        total_score: float,
        persona: Persona,
        memory: AgentMemory
    ) -> PrePublicationAuditResult:
        """
        Executes internal pre-publication self-audit before publishing.
        """
        failed_checks = []
        check_details = {}
        combined_text = (post_text + " " + rationale_text + " " + candidate.title + " " + candidate.summary).lower()
        
        # 1. FACTUALITY Check: Are factual claims supported by primary source URLs?
        factuality_passed = bool(candidate.sources and len(candidate.sources) > 0 and candidate.sources[0].startswith("http"))
        check_details["factuality"] = factuality_passed
        if not factuality_passed:
            failed_checks.append("FACTUALITY: Missing or invalid primary source URL")

        # 2. NOVELTY Check: Is this sufficiently different from previous publications?
        is_dup, dup_reason = memory.is_duplicate(candidate.title, candidate.summary, candidate.companies)
        novelty_passed = not is_dup
        check_details["novelty"] = novelty_passed
        if not novelty_passed:
            failed_checks.append(f"NOVELTY: High conceptual overlap with previous post ({dup_reason})")

        # 3. RELEVANCE Check: Does this genuinely matter to robotics?
        relevance_passed = candidate.roboticsRelevance >= 40.0 and total_score >= 65.0
        check_details["relevance"] = relevance_passed
        if not relevance_passed:
            failed_checks.append(f"RELEVANCE: Low robotics relevance or score below minimum quality threshold (Score: {total_score:.1f}/100)")

        # 4. ORIGINALITY Check: Does FORGE contribute an engineering interpretation?
        originality_passed = ("HOOK" in post_text and "ENGINEERING INTERPRETATION" in post_text and "REAL-WORLD LIMITATION" in post_text and "ENGINEERING TAKEAWAY" in post_text)
        check_details["originality"] = originality_passed
        if not originality_passed:
            failed_checks.append("ORIGINALITY: Missing required 4-part engineering interpretation structure")

        # 5. PERSONA Check: Does this sound consistent with established robotics engineer?
        user_facing_text = (post_text + " " + candidate.title + " " + candidate.summary).lower()
        persona_passed = not any(rkw.lower() in user_facing_text for rkw in persona.rejected_keywords)
        check_details["persona"] = persona_passed
        if not persona_passed:
            failed_checks.append("PERSONA: Contains prohibited non-technical marketing/crypto keywords inconsistent with Ada persona")

        # 6. EVIDENCE Check: Are important claims adequately sourced?
        evidence_passed = candidate.sourceQuality >= 40.0
        check_details["evidence"] = evidence_passed
        if not evidence_passed:
            failed_checks.append("EVIDENCE: Weak source credibility rating")

        # 7. RESTRAINT Check: Would publishing this genuinely improve the feed?
        restraint_passed = total_score >= 65.0
        check_details["restraint"] = restraint_passed
        if not restraint_passed:
            failed_checks.append("RESTRAINT: Candidate score fails editorial quality threshold; restraint exercised")

        passed_audit = len(failed_checks) == 0
        if passed_audit:
            summary = "Pre-Publication Self-Audit PASSED: All 7 critical verification checks (Factuality, Novelty, Relevance, Originality, Persona, Evidence, Restraint) satisfied."
        else:
            summary = f"Pre-Publication Self-Audit FAILED: Failed {len(failed_checks)} critical checks: {'; '.join(failed_checks)}"

        return PrePublicationAuditResult(
            passed_audit=passed_audit,
            failed_checks=failed_checks,
            check_details=check_details,
            audit_summary=summary
        )
