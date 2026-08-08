// Autonomous AI Creator - Live Dashboard JavaScript

document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const personaName = document.getElementById("personaName");
  const personaDomain = document.getElementById("personaDomain");
  const personaTitle = document.getElementById("personaTitle");
  const personaTagline = document.getElementById("personaTagline");
  const personaAvatar = document.getElementById("personaAvatar");
  const interestsTags = document.getElementById("interestsTags");
  const rejectionCriteriaList = document.getElementById("rejectionCriteriaList");
  const switchPersonaSelect = document.getElementById("switchPersonaSelect");
  
  const statPostsCount = document.getElementById("statPostsCount");
  const statRejectionsCount = document.getElementById("statRejectionsCount");
  const statMemoryCount = document.getElementById("statMemoryCount");
  
  const feedBadgeCount = document.getElementById("feedBadgeCount");
  const rejectionsBadgeCount = document.getElementById("rejectionsBadgeCount");
  
  const feedPostsContainer = document.getElementById("feedPostsContainer");
  const rejectionsContainer = document.getElementById("rejectionsContainer");
  const jsonViewer = document.getElementById("jsonViewer");
  const copyJsonBtn = document.getElementById("copyJsonBtn");
  const manualTriggerBtn = document.getElementById("manualTriggerBtn");

  // Tab switching
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabPanels = document.querySelectorAll(".tab-panel");

  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetTab = btn.getAttribute("data-tab");
      
      tabBtns.forEach(b => b.classList.remove("active"));
      tabPanels.forEach(p => p.classList.remove("active"));
      
      btn.classList.add("active");
      document.getElementById(targetTab).classList.add("active");
    });
  });

  // Fetch status and feed
  async function loadDashboardData() {
    try {
      // 1. Fetch status
      const statusRes = await fetch("/api/agent/status");
      if (statusRes.ok) {
        const status = await statusRes.json();
        updatePersonaUI(status.persona);
        
        statPostsCount.textContent = status.postCount || 0;
        statRejectionsCount.textContent = status.rejectionCount || 0;
        statMemoryCount.textContent = status.conceptCount || 0;
        
        rejectionsBadgeCount.textContent = status.rejectionCount || 0;
        renderRejections(status.recentRejections || []);
      }

      // 2. Fetch evaluator feed
      const feedRes = await fetch("/api/agent/feed");
      if (feedRes.ok) {
        const feedData = await feedRes.json();
        const posts = feedData.posts || [];
        
        statPostsCount.textContent = posts.length;
        feedBadgeCount.textContent = posts.length;
        
        renderFeed(posts);
        jsonViewer.textContent = JSON.stringify(feedData, null, 2);
      }
    } catch (err) {
      console.error("Error loading dashboard data:", err);
    }
  }

  function updatePersonaUI(persona) {
    if (!persona) return;
    personaName.textContent = persona.name;
    personaDomain.textContent = persona.domain;
    personaTitle.textContent = persona.title;
    personaTagline.textContent = `"${persona.tagline}"`;
    
    if (persona.avatar_color) {
      personaAvatar.style.backgroundColor = persona.avatar_color;
      personaAvatar.style.boxShadow = `0 0 20px ${persona.avatar_color}66`;
    }
    
    // Interests
    interestsTags.innerHTML = (persona.interests || [])
      .map(tag => `<span class="tag-item">${tag}</span>`)
      .join("");
      
    // Rejection criteria
    rejectionCriteriaList.innerHTML = (persona.rejection_criteria || [])
      .map(item => `<li>${item}</li>`)
      .join("");

    // Set select value
    if (switchPersonaSelect.value !== persona.id) {
      switchPersonaSelect.value = persona.id;
    }
  }

  function renderFeed(posts) {
    if (!posts || posts.length === 0) {
      feedPostsContainer.innerHTML = `
        <div class="glass-panel" style="padding: 30px; text-align: center; color: var(--text-muted);">
          <i class="fa-solid fa-spinner fa-spin" style="font-size: 2rem; margin-bottom: 12px; color: var(--primary);"></i>
          <p>Autonomous agent discovery in progress... Posts will appear here automatically.</p>
        </div>
      `;
      return;
    }

    feedPostsContainer.innerHTML = posts.map(post => {
      const dateStr = new Date(post.createdAt).toLocaleString();
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

          <div class="post-body">${post.text}</div>

          <div class="post-rationale-box">
            <div class="rationale-title"><i class="fa-solid fa-lightbulb"></i> Autonomous Publishing Rationale</div>
            <div class="rationale-text">${post.rationale}</div>
          </div>

          <div class="post-sources">
            <span style="font-size: 0.78rem; font-weight: 600; color: var(--text-dim);"><i class="fa-solid fa-link"></i> Sources:</span>
            ${sourcesHtml}
          </div>
        </article>
      `;
    }).join("");
  }

  function renderRejections(rejections) {
    if (!rejections || rejections.length === 0) {
      rejectionsContainer.innerHTML = `
        <div class="glass-panel" style="padding: 20px; text-align: center; color: var(--text-muted);">
          No candidate topics rejected yet.
        </div>
      `;
      return;
    }

    rejectionsContainer.innerHTML = rejections.map(rej => `
      <div class="rejection-card glass-panel">
        <div class="rejection-header">
          <span class="rejection-title"><i class="fa-solid fa-triangle-exclamation"></i> ${rej.title}</span>
          <span class="rejection-score">Score: ${rej.score ? rej.score.toFixed(1) : "15.0"}/100</span>
        </div>
        <p class="rejection-reason">${rej.reason}</p>
        <div style="font-size: 0.75rem; color: var(--text-dim); display: flex; justify-content: space-between; margin-top: 4px;">
          <span>Source: ${rej.source_name || "Feed Source"}</span>
          <span>${new Date(rej.rejectedAt).toLocaleTimeString()}</span>
        </div>
      </div>
    `).join("");
  }

  // Switch persona listener
  switchPersonaSelect.addEventListener("change", async (e) => {
    const selected = e.target.value;
    const personaMap = {
      ada: { name: "Ada", domain: "AI Security" },
      nova: { name: "Nova", domain: "ML Systems" },
      cipher: { name: "Cipher", domain: "AI Ethics & Governance" },
      astra: { name: "Astra", domain: "Robotics & Embodied AI" }
    };
    const pData = personaMap[selected] || { name: selected, domain: "AI Tech" };

    try {
      const res = await fetch("/api/agent/init", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ persona: pData })
      });
      if (res.ok) {
        await loadDashboardData();
      }
    } catch (err) {
      console.error("Failed switching persona:", err);
    }
  });

  // Manual Trigger Button
  manualTriggerBtn.addEventListener("click", async () => {
    manualTriggerBtn.disabled = true;
    manualTriggerBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Discovering & Scoring...`;
    
    try {
      await fetch("/api/agent/trigger", { method: "POST" });
      await loadDashboardData();
    } catch (err) {
      console.error("Trigger failed:", err);
    } finally {
      manualTriggerBtn.disabled = false;
      manualTriggerBtn.innerHTML = `<i class="fa-solid fa-bolt"></i> Trigger Tick`;
    }
  });

  // Copy JSON Button
  copyJsonBtn.addEventListener("click", () => {
    navigator.clipboard.writeText(jsonViewer.textContent);
    copyJsonBtn.innerHTML = `<i class="fa-solid fa-check"></i> Copied!`;
    setTimeout(() => {
      copyJsonBtn.innerHTML = `<i class="fa-regular fa-copy"></i> Copy JSON`;
    }, 2000);
  });

  // Initial load
  loadDashboardData();

  // Auto-refresh every 6 seconds to reflect continuous background ticks
  setInterval(loadDashboardData, 6000);
});
