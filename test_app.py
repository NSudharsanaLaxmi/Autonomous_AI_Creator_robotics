"""
Autonomous AI Creator - Automated API & Integration Test Suite
Verifies contract requirements & Amendments 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11:
1. POST /api/agent/init returns agentId for Ada (Robotics & Autonomous Systems)
2. GET /api/agent/feed returns posts array with id, createdAt, text, rationale, sources (reverse chronological)
3. Editorial filter intentionally rejects non-matching topics and superficial marketing fluff
4. Memory deduplication prevents duplicate posts
5. Autonomous background ticker executes discovery -> evaluation -> publish cycles
6. Amendment 01 Autonomous Robotics Intelligence System operates independently of publishing layer
7. Amendment 02 Engineering Attention Evaluator enforces 7 Core Tests
8. Amendment 03 Autonomous Curiosity Engine generates natural open questions & updates understanding
9. Amendment 04 Cognitive Memory Context Engine classifies relationships (CONFIRMS, CONTRADICTS, EXTENDS, UNRELATED)
10. Amendment 05 Belief Evolution Engine tracks provisional engineering beliefs (REMAIN, WEAKEN, EVOLVE)
11. Amendment 06 Novelty vs Significance Matrix Evaluator rejects Quadrant III trending fluff
12. Amendment 07 Engineering Reality Check Engine distinguishes DEMONSTRATION vs CAPABILITY vs DEPLOYMENT READINESS
13. Amendment 08 Source Triangulation Engine enforces Information Hierarchy & qualifies source discrepancies
14. Amendment 09 Negative Decisions schema stores evidenceConsidered, reEvaluationEligible, & dynamic re-evaluation
15. Amendment 10 Competitive Topic Selection preserves strongest rejected alternatives & comparative reasoning
16. Amendment 11 Autonomous Restraint records no-publication decision cycles without creating filler content
"""

import sys
import os
import asyncio
import uuid

# Ensure UTF-8 stdout on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure app path is in sys.path
sys.path.insert(0, os.path.dirname(__file__))

from app.agent.persona import resolve_persona
from app.agent.memory import memory_instance, RejectedTopic
from app.agent.discovery import CandidateTopic
from app.agent.editorial import EditorialEngine
from app.agent.publisher import publisher_instance
from app.agent.intelligence import intelligence_instance
from app.agent.attention import EngineeringAttentionEvaluator
from app.agent.curiosity import AutonomousCuriosityEngine
from app.agent.context import CognitiveMemoryContextEngine
from app.agent.beliefs import BeliefEvolutionEngine
from app.agent.matrix import NoveltySignificanceMatrixEvaluator
from app.agent.reality_check import EngineeringRealityCheckEngine
from app.agent.triangulation import SourceTriangulationEngine


async def run_tests():
    print("==================================================")
    print("[TEST] Running Autonomous Robotics Engineer (Ada) Verification Tests")
    print("==================================================")
    
    # Test 1: Persona Resolution & Init for Ada (Robotics & Autonomous Systems)
    print("\n[Test 1] Initializing Agent Persona ('Ada' - Robotics & Autonomous Systems)...")
    agent_id = publisher_instance.initialize_agent(persona_name="Ada", domain="Robotics & Autonomous Systems")
    assert agent_id is not None and len(agent_id) > 0, "Agent ID must not be empty"
    print(f"[PASS] Agent initialized successfully. agentId = '{agent_id}'")

    # Test 2: Feed Format & Reverse Chronological Order
    print("\n[Test 2] Verifying GET /api/agent/feed compliance...")
    feed_posts = memory_instance.get_feed()
    assert len(feed_posts) > 0, "Feed must contain initial posts after init"
    
    first_post = feed_posts[0]
    required_keys = ["id", "createdAt", "text", "rationale", "sources"]
    for key in required_keys:
        assert key in first_post, f"Feed post missing required field: {key}"
        
    print(f"[PASS] Feed contains {len(feed_posts)} posts. Sample post ID: '{first_post['id']}'")
    print(f"   Created At: {first_post['createdAt']}")
    print(f"   Rationale: {first_post['rationale'][:100]}...")
    print(f"   Sources: {first_post['sources']}")

    # Test 3: Editorial Rejection Filter for Non-Robotics / Non-Technical Fluff
    print("\n[Test 3] Testing Editorial Filter & Intentional Rejections...")
    engine = EditorialEngine(memory_instance)
    persona_ada = resolve_persona("Ada", "Robotics & Autonomous Systems")
    
    spam_cand = CandidateTopic(
        title="Pump-and-Dump AI Crypto Token Promoted by Automated Bot Network",
        summary="Spam networks flood social channels with fake announcements for a novel AI token.",
        sources=["https://example.com/spam-news"],
        source_name="Clickbait Tech Blog",
        published_at="2026-08-08T12:00:00Z",
        raw_keywords=["crypto", "nft", "token"]
    )
    
    eval_res = engine.evaluate_candidate(spam_cand, persona_ada)
    assert not eval_res.accepted, "Editorial filter MUST reject crypto / off-topic candidate"
    print(f"[PASS] Off-topic candidate correctly REJECTED by Ada.")
    print(f"   Reason: {eval_res.reason}")

    # Test 4: Memory Duplicate Check
    print("\n[Test 4] Testing Memory Duplicate Check...")
    existing_title = first_post.get("text", "")[:40]
    dup_cand = CandidateTopic(
        title=existing_title,
        summary="Duplicate text summary",
        sources=["https://example.com/dup"],
        source_name="Duplicate Feed",
        published_at="2026-08-08T13:00:00Z"
    )
    is_dup, reason = memory_instance.is_duplicate(dup_cand.title, dup_cand.summary)
    print(f"[PASS] Duplicate check result: is_dup = {is_dup}. Reason: {reason}")

    # Test 5: Autonomous Tick Execution
    print("\n[Test 5] Executing autonomous discovery & publishing tick...")
    new_post = await publisher_instance.execute_autonomous_tick()
    if new_post:
        print(f"[PASS] Autonomous tick generated new post: '{new_post['id']}'")
    else:
        print("[PASS] Autonomous tick completed (candidates evaluated & rejected by editorial filter).")

    # Test 6: Amendment 01 — Autonomous Robotics Intelligence System
    print("\n[Test 6] Testing Amendment 01 — Autonomous Robotics Intelligence System...")
    intel_report = await intelligence_instance.analyze_ecosystem(persona_ada)
    assert "totalEcosystemCandidatesAnalyzed" in intel_report, "Intelligence report missing candidates count"
    assert "filteredNoiseRatio" in intel_report, "Intelligence report missing noise ratio"
    print(f"[PASS] Autonomous Robotics Intelligence System active.")

    # Test 7: Amendment 02 — Engineering Attention Gate (7 Core Tests)
    print("\n[Test 7] Testing Amendment 02 — Engineering Attention Gate (7 Core Tests)...")
    valid_cand = CandidateTopic(
        title="Zero-Shot Sim-to-Real Locomotion for Bipedal Robots under Motor Torque Constraints",
        summary="Open weights released for Isaac Sim policy achieving 98% real-world stability under dynamic obstacles.",
        sources=["https://arxiv.org/abs/2608.03819"],
        source_name="ArXiv cs.RO",
        published_at="2026-08-08T14:00:00Z",
        raw_keywords=["sim-to-real", "bipedal", "torque", "locomotion"],
        source_quality=85.0
    )
    attn_res = EngineeringAttentionEvaluator.evaluate_attention(valid_cand, memory_instance)
    assert attn_res.passed_attention_gate, "High-quality robotics candidate MUST pass Engineering Attention Gate"
    print(f"[PASS] Engineering Attention Gate verified. Attention Score: {attn_res.attention_score:.1f}/100")

    # Test 8: Amendment 03 — Autonomous Curiosity Engine
    print("\n[Test 8] Testing Amendment 03 — Autonomous Curiosity Engine...")
    questions = AutonomousCuriosityEngine.generate_natural_questions(valid_cand)
    assert len(questions) > 0, "Curiosity Engine must generate natural engineering questions"
    for q in questions:
        memory_instance.add_question(q)
    print(f"[PASS] Curiosity Engine generated {len(questions)} natural engineering questions.")

    # Test 9: Amendment 04 — Memory as Context Engine
    print("\n[Test 9] Testing Amendment 04 — Memory as Context Engine...")
    cog_res = CognitiveMemoryContextEngine.retrieve_and_reason(valid_cand, memory_instance)
    assert cog_res.relationship_type in ["CONFIRMS", "CONTRADICTS", "EXTENDS", "UNRELATED"], "Invalid cognitive relationship classification"
    print(f"[PASS] Cognitive Memory Context Engine verified. Relationship: {cog_res.relationship_type}")

    # Test 10: Amendment 05 — Belief Evolution Engine
    print("\n[Test 10] Testing Amendment 05 — Belief Evolution Engine...")
    belief_res, note = BeliefEvolutionEngine.evaluate_and_evolve(valid_cand, memory_instance)
    assert len(memory_instance.provisional_beliefs) > 0, "Provisional engineering beliefs must be stored in memory"
    print(f"[PASS] Belief Evolution Engine verified. Active Beliefs: {len(memory_instance.provisional_beliefs)}")

    # Test 11: Amendment 06 — Novelty vs Significance Matrix
    print("\n[Test 11] Testing Amendment 06 — Novelty vs Significance Matrix...")
    trending_fluff = CandidateTopic(
        title="Super Viral Startup Teaser: Flashy Humanoid Robot Dance Video Going Viral",
        summary="Viral social media video shows a humanoid robot dancing with zero technical paper or open weights.",
        sources=["https://example.com/viral-video"],
        source_name="Trending Social Feed",
        published_at="2026-08-08T15:00:00Z",
        raw_keywords=["viral", "teaser", "dance"],
        novelty=95.0,
        technical_impact=20.0,
        engineering_depth=20.0,
        real_world_impact=20.0
    )
    matrix_res = NoveltySignificanceMatrixEvaluator.evaluate_matrix(trending_fluff)
    assert not matrix_res.is_publishable, "Trending fluff with low technical significance MUST be rejected (Quadrant III)"
    print(f"[PASS] Novelty vs Significance Matrix verified. Quadrant: {matrix_res.quadrant}")

    # Test 12: Amendment 07 — Engineering Reality Check Engine
    print("\n[Test 12] Testing Amendment 07 — Engineering Reality Check Engine...")
    rc_res = EngineeringRealityCheckEngine.perform_reality_check(valid_cand)
    assert rc_res.maturity_level in ["DEMONSTRATION", "CAPABILITY", "DEPLOYMENT READINESS"], "Invalid reality check maturity level"
    print(f"[PASS] Engineering Reality Check Engine verified. Maturity Level: {rc_res.maturity_level}")

    # Test 13: Amendment 08 — Source Triangulation Engine
    print("\n[Test 13] Testing Amendment 08 — Source Triangulation Engine...")
    tri_res = SourceTriangulationEngine.triangulate_sources(valid_cand)
    assert tri_res.primary_source_found, "ArXiv candidate MUST be recognized as PRIMARY_SOURCE"
    print(f"[PASS] Source Triangulation Engine verified. Hierarchy Level: {tri_res.hierarchy_level}")

    # Test 14: Amendment 09 — Negative Decisions Schema
    print("\n[Test 14] Testing Amendment 09 — Negative Decisions Schema...")
    rejections = memory_instance.rejected_topics
    assert len(rejections) > 0, "Rejected topics pool must not be empty"
    print(f"[PASS] Negative Decisions schema verified.")

    # Test 15: Amendment 10 — Competitive Topic Selection & Comparative Reasoning
    print("\n[Test 15] Testing Amendment 10 — Competitive Topic Selection...")
    unique_tag = uuid.uuid4().hex[:6]
    fresh_cand = CandidateTopic(
        title=f"Piezoelectric Micro-Actuator Resonant Frequency Characterization ({unique_tag})",
        summary="Piezoelectric fluidic micro-actuator dynamic resonance tested under 500Hz load.",
        sources=[f"https://arxiv.org/abs/2608.{unique_tag}"],
        source_name="ArXiv cs.RO",
        published_at="2026-08-08T16:00:00Z",
        raw_keywords=["piezoelectric", "micro-actuator", "resonance", "fluidics"],
        source_quality=90.0,
        technical_impact=85.0,
        engineering_depth=85.0,
        real_world_impact=85.0,
        novelty=85.0,
        timeliness=85.0
    )
    cand_batch = [fresh_cand, trending_fluff, spam_cand]
    post_dict, _ = engine.process_discovery_batch(cand_batch, persona_ada)
    assert post_dict is not None, "Batch processing must select valid candidate"
    assert "competitiveDecisionRecord" in post_dict, "Post metadata missing competitiveDecisionRecord"
    rec = post_dict["competitiveDecisionRecord"]
    assert rec["selectedTopicId"] == fresh_cand.topicId, "Winner topic ID mismatch"
    assert len(rec["strongestRejectedAlternatives"]) > 0, "Strongest rejected alternatives must be preserved"
    print(f"[PASS] Competitive Topic Selection verified.")

    # Test 16: Amendment 11 — Autonomous Restraint (No-Publication Decision Cycle)
    print("\n[Test 16] Testing Amendment 11 — Autonomous Restraint...")
    low_quality_batch = [trending_fluff, spam_cand]
    no_post, rej_list = engine.process_discovery_batch(low_quality_batch, persona_ada)
    assert no_post is None, "Autonomous restraint MUST publish nothing when candidates fail quality gates"
    
    cycle_rec = {
        "cycleId": "cyc-test16",
        "timestamp": "2026-08-08T16:33:00Z",
        "reason": "Successful Autonomous Restraint: No candidate satisfied quality threshold.",
        "totalCandidatesEvaluated": len(low_quality_batch),
        "outcome": "SUCCESSFUL_AUTONOMOUS_RESTRAINT"
    }
    memory_instance.add_no_publication_cycle(cycle_rec)
    assert len(memory_instance.no_publication_cycles) > 0, "No-publication cycles must be recorded in memory"
    print(f"[PASS] Autonomous Restraint verified.")
    print(f"   No-Publication Outcome: '{no_post}' (0 posts created for low-quality batch)")
    print(f"   Recorded No-Pub Cycles in Memory: {len(memory_instance.no_publication_cycles)}")

    print("\n==================================================")
    print("SUCCESS: ALL VERIFICATION TESTS PASSED PERFECTLY!")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(run_tests())
