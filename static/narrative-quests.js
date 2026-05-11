// Quest panel: load, render, and interact with the layered goal tracker.

let questPanelOpen = true;

function toggleQuestPanel() {
  questPanelOpen = !questPanelOpen;
  const body = document.getElementById('questPanelBody');
  const icon = document.getElementById('questPanelToggle');
  if (body) body.style.display = questPanelOpen ? '' : 'none';
  if (icon) icon.classList.toggle('open', questPanelOpen);
}

async function loadQuests() {
  if (!currentWorldId) return;
  try {
    const data = await apiFetch(`/api/worlds/${currentWorldId}/quests`);
    renderQuestPanel(data.quests || []);
  } catch (e) {
    // Silent — quest panel is non-critical
  }
}

function renderQuestPanel(quests) {
  const body = document.getElementById('questPanelBody');
  if (!body) return;

  const active = quests.filter(q => q.status === 'active');
  const pending = quests.filter(q => q.status === 'pending_player');
  const tier1 = active.filter(q => q.tier === 1);
  const tier2 = active.filter(q => q.tier === 2);

  if (!tier1.length && !tier2.length && !pending.length) {
    body.innerHTML = '<div class="px-4 py-4 text-xs text-slate-600 text-center">No active goals yet.</div>';
    return;
  }

  let html = '';

  // Tier 1 — Overarching
  if (tier1.length) {
    html += `<div class="px-4 pt-3 pb-1">
      <div class="quest-tier-label mb-1.5">Overarching</div>`;
    for (const q of tier1) {
      html += renderQuestCard(q, false);
    }
    html += `</div>`;
  }

  // Tier 2 — Active
  if (tier2.length) {
    html += `<div class="px-4 pt-2 pb-1 border-t border-slate-800/60">
      <div class="quest-tier-label mb-1.5">Active</div>`;
    for (const q of tier2) {
      html += renderQuestCard(q, false);
    }
    html += `</div>`;
  }

  // Tier 3 — Pending player
  if (pending.length) {
    html += `<div class="px-4 pt-2 pb-2 border-t border-slate-800/60 bg-amber-950/10">
      <div class="quest-tier-label text-amber-700/70 mb-1.5">Threads — your call</div>`;
    for (const q of pending) {
      html += renderThreadCard(q);
    }
    html += `</div>`;
  }

  body.innerHTML = html;
}

function renderQuestCard(q, showTags) {
  const total = q.completion_tags.length;
  const matched = q.progress_tags.length;
  const pct = total > 0 ? Math.round((matched / total) * 100) : 0;

  let tagsHtml = '';
  if (showTags && matched > 0) {
    tagsHtml = `<div class="flex flex-wrap gap-1 mt-1.5">` +
      q.progress_tags.map(t => `<span class="quest-tag-done">${escapeHtml(t)} ✓</span>`).join('') +
      `</div>`;
  }

  const progressBar = total > 0 ? `
    <div class="quest-progress-bar mt-2">
      <div class="quest-progress-fill" style="width:${pct}%"></div>
    </div>` : '';

  return `<div class="mb-3">
    <p class="text-xs font-semibold text-slate-200 leading-snug">${escapeHtml(q.title)}</p>
    ${q.description ? `<p class="text-xs text-slate-500 leading-relaxed mt-0.5">${escapeHtml(q.description)}</p>` : ''}
    ${tagsHtml}
    ${progressBar}
    ${total > 0 ? `<p class="text-xs text-slate-600 mt-1">${matched} of ${total} milestones</p>` : ''}
  </div>`;
}

function renderThreadCard(q) {
  return `<div class="flex items-start gap-2 mb-2">
    <div class="flex-1 min-w-0">
      <p class="text-xs text-slate-400 leading-snug truncate">${escapeHtml(q.title)}</p>
      ${q.description ? `<p class="text-xs text-slate-600 leading-relaxed truncate">${escapeHtml(q.description)}</p>` : ''}
    </div>
    <div class="flex gap-1 flex-none mt-0.5">
      <button onclick="promoteQuest('${q.quest_id}')" class="quest-thread-btn quest-thread-btn-track">Track</button>
      <button onclick="dismissQuest('${q.quest_id}')" class="quest-thread-btn quest-thread-btn-dismiss">Ignore</button>
    </div>
  </div>`;
}

async function promoteQuest(questId) {
  if (!currentWorldId) return;
  try {
    await apiFetch(`/api/worlds/${currentWorldId}/quests/${questId}/promote`, { method: 'POST' });
    await loadQuests();
  } catch (e) {}
}

async function dismissQuest(questId) {
  if (!currentWorldId) return;
  try {
    await apiFetch(`/api/worlds/${currentWorldId}/quests/${questId}/dismiss`, { method: 'POST' });
    await loadQuests();
  } catch (e) {}
}

async function checkQuestProgress(questId) {
  if (!currentWorldId) return;
  try {
    const data = await apiFetch(
      `/api/worlds/${currentWorldId}/quests/${questId}/check`,
      { method: 'POST' }
    );
    // Reveal tags and show progress in the panel
    await loadQuests();
    // Show a brief banner with the result
    const pct = data.percentage || 0;
    const matched = data.matched || 0;
    const total = data.total || 0;
    const msg = `${data.title}: ${matched} of ${total} milestones complete (${pct}%). ${data.points_spent} point${data.points_spent !== 1 ? 's' : ''} spent.`;
    showQuestCheckBanner(msg);
  } catch (e) {}
}

function showQuestCheckBanner(msg) {
  let banner = document.getElementById('questCheckBanner');
  if (!banner) {
    banner = document.createElement('div');
    banner.id = 'questCheckBanner';
    banner.style.cssText = `
      position: fixed; bottom: 5.5rem; left: 50%; transform: translateX(-50%);
      z-index: 35; background: rgba(15,23,42,0.95); backdrop-filter: blur(8px);
      border: 1px solid rgba(124,101,247,0.4); color: #c4b5fd;
      padding: 0.5rem 1.1rem; border-radius: 999px;
      font-size: 0.72rem; letter-spacing: 0.03em;
      box-shadow: 0 4px 20px -4px rgba(0,0,0,0.6);
      white-space: nowrap; pointer-events: none;
    `;
    document.body.appendChild(banner);
  }
  banner.textContent = msg;
  banner.style.opacity = '1';
  clearTimeout(banner._timeout);
  banner._timeout = setTimeout(() => {
    banner.style.transition = 'opacity 0.6s';
    banner.style.opacity = '0';
  }, 4000);
}
