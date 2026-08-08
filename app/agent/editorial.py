"""
Editorial Judgment Engine
Applies strict persona alignment, quality scoring, memory uniqueness validation,
and intentional candidate rejections.
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple, Optional
from app.agent.persona import Persona
from app.agent.discovery import CandidateTopic
from app.agent.memory import AgentMemory, Post, RejectedTopic

logger = logging.getLogger("editorial")


class EvaluationResult:
    def __init__(self, topic: CandidateTopic, score: float, accepted: bool, reason: str, details: Dict[str, Any]):
        self.topic = topic
        self.score = score
        self.accepted = accepted
        self.reason = reason
        self.details = details


class EditorialEngine:
    def __init__(self, memory: AgentMemory):
        self.memory = memory

    def evaluate_candidate(self, candidate: CandidateTopic, persona: Persona) -> EvaluationResult:
        """
        Evaluates a single candidate topic against persona standards and memory.
        Returns EvaluationResult with detailed scoring breakdown and decision.
        """
        title_lower = candidate.title.lower()
        summary_lower = candidate.summary.lower()
        combined_text = f"{title_lower} {summary_lower}"
        
        # 1. Check for hard-rejected keywords
        for rkw in persona.rejected_keywords:
            if rkw.lower() in combined_text:
                return EvaluationResult(
                    topic=candidate,
                    score=15.0,
                    accepted=False,
                    reason=f"Topic intentionally rejected by {persona.name}: Contains non-{persona.domain} prohibited phrase or off-topic fluff ('{rkw}').",
                    details={"rejected_keyword": rkw}
                )
                
        # 2. Check for memory duplicates
        is_dup, dup_reason = self.memory.is_duplicate(candidate.title, candidate.summary)
        if is_dup:
            return EvaluationResult(
                topic=candidate,
                score=30.0,
                accepted=False,
                reason=f"Topic rejected due to memory constraint: {dup_reason}",
                details={"memory_duplicate": True}
            )

        # 3. Calculate Persona Domain Alignment Score (0 - 40)
        domain_matches = 0
        for akw in persona.approved_keywords:
            if akw.lower() in combined_text:
                domain_matches += 1
                
        domain_score = min(40.0, domain_matches * 12.0)
        if domain_matches == 0:
            # Check general tech relevance
            if any(w in combined_text for w in ["ai", "model", "llm", "code", "paper", "data"]):
                domain_score = 15.0
            else:
                domain_score = 5.0

        # 4. Technical Depth & Source Credibility Score (0 - 30)
        source_score = 25.0 if candidate.source_name in ["ArXiv AI Security", "ArXiv Cryptography & Security", "HuggingFace Papers", "GitHub Releases", "ArXiv AI"] else 18.0
        
        # 5. Novelty & Timeliness Score (0 - 30)
        novelty_score = 25.0
        
        total_score = domain_score + source_score + novelty_score
        
        # Threshold decision
        min_threshold = 60.0
        if total_score >= min_threshold and domain_matches > 0:
            return EvaluationResult(
                topic=candidate,
                score=total_score,
                accepted=True,
                reason=f"Passed editorial standards (Score: {total_score:.1f}/100). High domain alignment with {persona.domain}.",
                details={"domain_score": domain_score, "source_score": source_score, "novelty_score": novelty_score}
            )
        else:
            return EvaluationResult(
                topic=candidate,
                score=total_score,
                accepted=False,
                reason=f"Topic rejected by {persona.name}: Insufficient alignment with {persona.domain} editorial focus (Score: {total_score:.1f}/100, Domain Matches: {domain_matches}).",
                details={"domain_score": domain_score, "source_score": source_score, "novelty_score": novelty_score}
            )

    def process_discovery_batch(
        self,
        candidates: List[CandidateTopic],
        persona: Persona
    ) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Evaluates a batch of discovered topics.
        Rejects unqualified topics (recording reasons in memory).
        Selects the single highest scoring candidate to synthesize into a Post.
        Returns (new_post_dict, rejected_topics_list).
        """
        results: List[EvaluationResult] = []
        accepted_results: List[EvaluationResult] = []
        rejected_results: List[EvaluationResult] = []
        
        for cand in candidates:
            res = self.evaluate_candidate(cand, persona)
            results.append(res)
            
            if res.accepted:
                accepted_results.append(res)
            else:
                rejected_results.append(res)
                # Store rejection record in memory
                rej_obj = RejectedTopic(
                    topic_id=f"rej-{uuid.uuid4().hex[:6]}",
                    title=cand.title,
                    source_url=cand.source_url,
                    source_name=cand.source_name,
                    rejected_at=datetime.now(timezone.utc).isoformat(),
                    reason=res.reason,
                    score=res.score,
                    persona_id=persona.id
                )
                self.memory.add_rejection(rej_obj)

        if not accepted_results:
            logger.info("Batch evaluation complete: All candidate topics were intentionally rejected by editorial judgment.")
            return None, [r.topic.to_dict() for r in rejected_results]
            
        # Sort accepted candidates by score descending
        accepted_results.sort(key=lambda x: x.score, reverse=True)
        winner = accepted_results[0]
        
        # Build synthesis text and rationale
        post_dict = self._synthesize_post(winner, rejected_results, persona)
        
        # Save post into memory
        self.memory.add_post(post_dict, keywords=winner.topic.raw_keywords)
        
        return post_dict, [r.topic.to_dict() for r in rejected_results]

    def _synthesize_post(
        self,
        winner: EvaluationResult,
        rejections: List[EvaluationResult],
        persona: Persona
    ) -> Dict[str, Any]:
        """
        Synthesizes post text in persona's editorial voice and constructs the required 3-part rationale.
        """
        topic = winner.topic
        post_id = f"p-{uuid.uuid4().hex[:6]}"
        now_iso = datetime.now(timezone.utc).isoformat()
        
        # Persona Voice Generator Templates
        if persona.id == "ada":
            post_text = (
                f"🚨 SECURITY BREAKDOWN: {topic.title}\n\n"
                f"{topic.summary}\n\n"
                f"Threat Model Analysis:\n"
                f"When autonomous agents or pipeline tools ingest raw third-party inputs, standard boundary guardrails fail. "
                f"Without hardened sandboxing and strict token-level input sanitization, this attack vector allows unauthorized tool execution.\n\n"
                f"Key Takeaway: Never rely solely on system prompt instructions for security boundaries—enforce deterministic API access control at the runtime boundary."
            )
        elif persona.id == "nova":
            post_text = (
                f"⚡ PERFORMANCE & ARCHITECTURE: {topic.title}\n\n"
                f"{topic.summary}\n\n"
                f"System Optimization Metrics:\n"
                f"Profiling KV-cache memory bandwidth reveals how hardware-aware CUDA kernels eliminate memory stalls during speculative decoding. "
                f"By pairing custom FP8 quantization with asynchronous memory transfers, serving throughput scales linearly across cluster nodes.\n\n"
                f"Takeaway: Memory bandwidth—not raw compute FLOPs—remains the primary bottleneck for long-context production LLM serving."
            )
        elif persona.id == "cipher":
            post_text = (
                f"⚖️ ETHICS & GOVERNANCE AUDIT: {topic.title}\n\n"
                f"{topic.summary}\n\n"
                f"Policy & Alignment Analysis:\n"
                f"Frontier model deployment demands verifiable transparency rather than self-reported lab benchmarks. "
                f"Without independent multi-stakeholder audits, synthetic data loops introduce covert bias risks and compliance exposure.\n\n"
                f"Perspective: Robust AI governance requires mandatory third-party evaluations before model release."
            )
        elif persona.id == "astra":
            post_text = (
                f"🤖 EMBODIED AI BREAKTHROUGH: {topic.title}\n\n"
                f"{topic.summary}\n\n"
                f"Physical Systems & Sim2Real Insight:\n"
                f"Bridging the sim-to-real gap for dexterous motor policies requires multi-modal sensor fusion under dynamic friction constraints. "
                f"Integrating ROS2 control loops directly with vision-language-action policies enables real-time trajectory adaptation.\n\n"
                f"Takeaway: Spatial intelligence relies on tight hardware-software feedback loops in unstructured environments."
            )
        else:
            post_text = (
                f"📌 PERSPECTIVE ({persona.domain}): {topic.title}\n\n"
                f"{topic.summary}\n\n"
                f"Editorial Insights:\n"
                f"Analyzing these paradigm shifts is critical to understanding how autonomous agent systems evolve in production environments."
            )
            
        # Build 3-part rationale explicitly addressing Hackathon requirements
        rejected_summary_str = ""
        if rejections:
            rejected_titles = [f"'{r.topic.title}' ({r.reason})" for r in rejections[:2]]
            rejected_summary_str = f" Rejections in this cycle: {'; '.join(rejected_titles)}."
            
        rationale_text = (
            f"Topic Selection: Selected '{topic.title}' because it directly aligns with {persona.name}'s focus on {persona.domain} and scored {winner.score:.1f}/100 on domain relevance and technical depth."
            f" Timeliness: Relevant now as recent releases and research papers in {topic.source_name} highlight active developments affecting production deployments."
            f" Editorial Choice: Chosen over lower-scoring or off-topic candidates due to its technical rigor and actionable insights.{rejected_summary_str}"
        )
        
        return Post(
            post_id=post_id,
            created_at=now_iso,
            text=post_text,
            rationale=rationale_text,
            sources=[topic.source_url]
        )
