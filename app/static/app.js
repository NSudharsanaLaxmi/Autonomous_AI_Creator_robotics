// FORGE Autonomous Robotics Engineer — Telemetry Dashboard JavaScript

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const offlineBanner = document.getElementById("offlineBanner");
  const engineStatusBadge = document.getElementById("engineStatusBadge");
  const telemetryLastCycle = document.getElementById("telemetryLastCycle");
  const telemetryNextCycle = document.getElementById("telemetryNextCycle");

  const statPostsCount = document.getElementById("statPostsCount");
  const statRejectionsCount = document.getElementById("statRejectionsCount");
  const statCuriosityCount = document.getElementById("statCuriosityCount");
  const statBeliefsCount = document.getElementById("statBeliefsCount");

  const feedBadgeCount = document.getElementById("feedBadgeCount");
  const activeAgentIdCode = document.getElementById("activeAgentIdCode");

  const feedPostsContainer = document.getElementById("feedPostsContainer");
  const decisionsContainer = document.getElementById("decisionsContainer");
  const rejectionsMemoryContainer = document.getElementById("rejectionsMemoryContainer");
  const curiosityQuestionsList = document.getElementById("curiosityQuestionsList");
  const provisionalBeliefsList = document.getElementById("provisionalBeliefsList");
  
  const jsonViewer = document.getElementById("jsonViewer");
  const copyJsonBtn = document.getElementById("copyJsonBtn");

  // Tab switching logic
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabPanels = document.querySelectorAll(".tab-panel");

  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetTab = btn.getAttribute("data-tab");
      
      tabBtns.forEach(b => b.classList.remove("active"));
      tabPanels.forEach(p => p.classList.remove("active"));
      
      btn.classList.add("active");
      const targetPanel = document.getElementById(targetTab);
      if (targetPanel) {
        targetPanel.classList.add("active");
      }
    });
  });

  // Format UTC ISO timestamps cleanly
  function formatUtcTime(isoStr) {
    if (!isoStr) return "--:-- UTC";
    try {
      const d = new Date(isoStr);
      return d.toUTCString().replace("GMT", "UTC").replace(/^.*?, /, "").replace(/:\d\d UTC$/, " UTC");
    } catch(e) {
      return isoStr;
    }
  }

  // Load telemetry data from backend
  async function loadDashboardData() {
    try {
      // 1. Fetch live status telemetry
      const statusRes = await fetch("/api/agent/status");
      if (!statusRes.ok) {
        showOfflineState(true);
        return;
      }
      showOfflineState(false);
      const statusData = await statusRes.json();

      // Update Header & Telemetry Pills
      if (activeAgentIdCode) activeAgentIdCode.textContent = statusData.agentId || "ada-bot-001";
      if (statPostsCount) statPostsCount.textContent = statusData.postCount || 0;
      if (statRejectionsCount) statRejectionsCount.textContent = statusData.rejectionCount || 0;
      if (statCuriosityCount) statCuriosityCount.textContent = statusData.unresolvedQuestionsCount || 0;
      if (statBeliefsCount) statBeliefsCount.textContent = statusData.provisionalBeliefsCount || 0;

      if (telemetryLastCycle) telemetryLastCycle.textContent = formatUtcTime(statusData.lastCycleAt);
      if (telemetryNextCycle) telemetryNextCycle.textContent = formatUtcTime(statusData.nextCycleAt);

      if (engineStatusBadge) {
        const loopActive = statusData.isLoopRunning;
        engineStatusBadge.innerHTML = `<span class="pulse-dot"></span> AUTONOMOUS ENGINE ● ${loopActive ? "ACTIVE" : "WAITING"}`;
        engineStatusBadge.className = `badge live-badge ${loopActive ? "" : "paused"}`;
      }

      // Update Memory Lists
      renderCuriosityQuestions(statusData.unresolvedQuestions || []);
      renderProvisionalBeliefs(statusData.provisionalBeliefs || []);
      renderRejections(statusData.recentRejections || []);

      // 2. Fetch evaluator feed
      const feedRes = await fetch("/api/agent/feed");
      if (feedRes.ok) {
        const feedData = await feedRes.json();
        const posts = feedData.posts || [];
        
        if (feedBadgeCount) feedBadgeCount.textContent = posts.length;
        renderFeed(posts);
        renderDecisionTrace(posts);
        
        if (jsonViewer) jsonViewer.textContent = JSON.stringify(feedData, null, 2);
      }
    } catch (err) {
      console.error("[ERROR] Failed loading dashboard telemetry:", err);
      showOfflineState(true);
    }
  }

  function showOfflineState(isOffline) {
    if (!offlineBanner) return;
    if (isOffline) {
      offlineBanner.classList.remove("hidden");
    } else {
      offlineBanner.classList.add("hidden");
    }
  }

  function renderFeed(posts) {
    if (!feedPostsContainer) return;
    if (!posts || posts.length === 0) {
      feedPostsContainer.innerHTML = `
        <div class="glass-panel" style="padding: 30px; text-align: center; color: var(--text-muted);">
          <i class="fa-solid fa-microchip" style="font-size: 2rem; margin-bottom: 12px; color: var(--accent-cyan);"></i>
          <p>FORGE is observing the robotics ecosystem. No publication has met its editorial threshold yet.</p>
        </div>
      `;
      return;
    }

    feedPostsContainer.innerHTML = posts.map(post => {
      const dateStr = formatUtcTime(post.createdAt);
      const sourcesHtml = (post.sources || []).map(src => {
        let label = src;
        try {
          const u = new URL(src);
          label = u.hostname.replace("www.", "") + u.pathname;
        } catch(e) {}
        return `<a href="${src}" target="_blank" class="source-badge"><i class="fa-solid fa-arrow-up-right-from-square"></i> ${label}</a>`;
      }).join(" ");

      return `
        <article class="post-card glass-panel">
          <div class="post-header">
            <span class="post-id-badge">${post.id}</span>
            <span class="post-time"><i class="fa-regular fa-clock"></i> ${dateStr}</span>
          </div>

          <div class="post-body">${escapeHtml(post.text)}</div>

          <div class="post-rationale-box">
            <div class="rationale-title"><i class="fa-solid fa-scale-balanced"></i> Autonomous Publishing Rationale</div>
            <div class="rationale-text">${escapeHtml(post.rationale)}</div>
          </div>

          <div class="post-sources">
            <span style="font-size: 0.78rem; font-weight: 600; color: var(--text-dim);"><i class="fa-solid fa-link"></i> Sources:</span>
            ${sourcesHtml}
          </div>
        </article>
      `;
    }).join("");
  }

  function renderDecisionTrace(posts) {
    if (!decisionsContainer) return;
    if (!posts || posts.length === 0) {
      decisionsContainer.innerHTML = `
        <div class="glass-panel" style="padding: 24px; text-align: center; color: var(--text-muted);">
          No decision history recorded yet. FORGE will record comparative candidates when an autonomous cycle publishes.
        </div>
      `;
      return;
    }

    decisionsContainer.innerHTML = posts.map(post => {
      const trace = post.structuredDecisionTrace || {};
      const comp = post.competitiveDecisionRecord || {};

      const alternativesHtml = (comp.strongestRejectedAlternatives || []).map(alt => `
        <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 4px;">
          • <strong>${escapeHtml(alt.title)}</strong> (Score: ${alt.score}/100) — <span style="color:#fca5a5;">${escapeHtml(alt.rejectionReason)}</span>
        </div>
      `).join("");

      return `
        <div class="decision-card glass-panel">
          <div class="decision-header">
            <span class="decision-title"><i class="fa-solid fa-square-check" style="color:var(--accent-green);"></i> Selected: ${escapeHtml(comp.selectedTopicTitle || post.id)}</span>
            <span class="decision-score-pill">Score: ${comp.selectedScore || 85.0}/100</span>
          </div>
          
          <p style="font-size:0.83rem; color:var(--text-muted);">${escapeHtml(comp.comparativeReasoning || post.rationale)}</p>

          ${alternativesHtml ? `
            <div class="decision-alternatives-box">
              <h5><i class="fa-solid fa-shield-cat"></i> Evaluated Alternatives Rejected in Current Cycle:</h5>
              ${alternativesHtml}
            </div>
          ` : ""}
        </div>
      `;
    }).join("");
  }

  function renderCuriosityQuestions(questions) {
    if (!curiosityQuestionsList) return;
    if (!questions || questions.length === 0) {
      curiosityQuestionsList.innerHTML = `<li style="font-style:italic;">No unresolved questions in memory pool yet.</li>`;
      return;
    }
    curiosityQuestionsList.innerHTML = questions.map(q => `
      <li><i class="fa-solid fa-circle-question" style="color:var(--primary); margin-right:6px;"></i> ${escapeHtml(typeof q === "string" ? q : q.question)}</li>
    `).join("");
  }

  function renderProvisionalBeliefs(beliefs) {
    if (!provisionalBeliefsList) return;
    if (!beliefs || beliefs.length === 0) {
      provisionalBeliefsList.innerHTML = `<li style="font-style:italic;">No provisional beliefs recorded yet.</li>`;
      return;
    }
    provisionalBeliefsList.innerHTML = beliefs.map(b => `
      <li><i class="fa-solid fa-lightbulb" style="color:var(--accent-green); margin-right:6px;"></i> ${escapeHtml(typeof b === "string" ? b : b.statement)}</li>
    `).join("");
  }

  function renderRejections(rejections) {
    if (!rejectionsMemoryContainer) return;
    if (!rejections || rejections.length === 0) {
      rejectionsMemoryContainer.innerHTML = `<div style="color:var(--text-dim); font-style:italic; padding:10px;">No candidate topics rejected yet.</div>`;
      return;
    }

    rejectionsMemoryContainer.innerHTML = rejections.map(rej => `
      <div class="rejection-card glass-panel">
        <div class="rejection-header">
          <span class="rejection-title"><i class="fa-solid fa-triangle-exclamation"></i> ${escapeHtml(rej.title)}</span>
          <span class="rejection-score">Score: ${rej.score ? rej.score.toFixed(1) : "15.0"}/100</span>
        </div>
        <p class="rejection-reason">${escapeHtml(rej.reason)}</p>
        <div style="font-size: 0.75rem; color: var(--text-dim); display: flex; justify-content: space-between; margin-top: 6px;">
          <span>Source: ${escapeHtml(rej.source_name || "Feed Source")}</span>
          <span>${formatUtcTime(rej.rejectedAt)}</span>
        </div>
      </div>
    `).join("");
  }

  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Copy JSON Button
  if (copyJsonBtn && jsonViewer) {
    copyJsonBtn.addEventListener("click", () => {
      navigator.clipboard.writeText(jsonViewer.textContent);
      copyJsonBtn.innerHTML = `<i class="fa-solid fa-check"></i> Copied!`;
      setTimeout(() => {
        copyJsonBtn.innerHTML = `<i class="fa-regular fa-copy"></i> Copy JSON`;
      }, 2000);
    });
  }

  // Initial load
  loadDashboardData();

  // Auto-refresh every 6 seconds to reflect continuous background ticks (read-only polling)
  setInterval(loadDashboardData, 6000);
});
