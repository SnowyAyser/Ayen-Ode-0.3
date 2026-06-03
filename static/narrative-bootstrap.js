// Narrative Client Module: Bootstrap & World Loader
// Line limit compliance: Under 150 lines
function bootstrapNarrativeWorld() {
  checkAuth();
  const params = new URLSearchParams(window.location.search);
  currentWorldId = params.get('world_id');

  if (!currentWorldId) {
    apiCall("/api/worlds/active")
      .then(data => {
        if (data && data.world) {
          currentWorldId = data.world.world_id;
          loadWorld();
        } else {
          document.getElementById("narrativeContent").innerHTML =
            '<div class="text-red-400 text-center py-12"><p>No active world. <a href="/dashboard.html" class="underline">Create one first</a></p></div>';
        }
      });
  } else {
    loadWorld();
  }
}

async function loadWorld() {
  try {
    const url = currentWorldId ? `/api/world?world_id=${currentWorldId}` : `/api/world`;
    const token = getToken();
    const response = await fetch(url, { headers: { "Authorization": `Bearer ${token}` } });
    if (!response.ok) throw new Error("Failed to load world");
    const data = await response.json();
    if (!data.success) throw new Error(data.error || "Could not load world");

    currentWorldId = data.world_id;
    restoreDraft();
    currentEntities = data.entities || [];
    for (const key in entityCache) delete entityCache[key];
    if (typeof restoreActiveInvestigations === 'function') {
      restoreActiveInvestigations(data.investigations || []);
    }
    const world = data.world;
    document.getElementById("worldName").textContent = world.name || "Unknown World";
    document.getElementById("worldPremise").textContent = world.premise || "";

    const handoff = data.handoff;
    let handoffText = '';
    if (typeof handoff === 'string') {
      handoffText = handoff;
    } else if (handoff && handoff.handoff_text) {
      handoffText = handoff.handoff_text;
    }

    conversationHistory = loadHistoryFromStorage();
    const narrativeDiv = document.getElementById("narrativeContent");

    if (_isReplayIntro && handoffText) {
      _showReplayBadge();
      await _sleep(450);
      await playOpeningSceneIntro(handoffText);
      if (conversationHistory.length > 0) {
        const divider = document.createElement('div');
        divider.className = 'flex items-center gap-3 my-8 opacity-0';
        divider.style.transition = 'opacity 600ms ease-out';
        divider.innerHTML = `
          <div class="flex-1 h-px bg-slate-800"></div>
          <span class="text-slate-600 text-xs uppercase tracking-widest">Continuing</span>
          <div class="flex-1 h-px bg-slate-800"></div>
        `;
        narrativeDiv.appendChild(divider);
        renderHistoryToPage(conversationHistory);
        requestAnimationFrame(() => { divider.style.opacity = '1'; });
        narrativeDiv.scrollTop = narrativeDiv.scrollHeight;
      }
    } else if (_isFreshEntry && conversationHistory.length === 0 && handoffText) {
      await _sleep(450);
      await playOpeningSceneIntro(handoffText);
    } else if (conversationHistory.length > 0) {
      narrativeDiv.innerHTML = '';
      renderHistoryToPage(conversationHistory);
      narrativeDiv.scrollTop = narrativeDiv.scrollHeight;
    } else if (handoffText) {
      const parsed = parseInvestigateText(handoffText);
      const htmlContent = parsed.text.split('\n').map(p => p.trim()).filter(p => p).map(p => `<p>${p}</p>`).join('');
      document.getElementById("narrativeContent").innerHTML = `
        <div class="narrative-block text-slate-200 leading-7 space-y-3">
          ${htmlContent}
        </div>
      `;
    } else {
      document.getElementById("narrativeContent").innerHTML =
        '<div class="text-slate-600 text-center py-12"><p>Ready to explore…</p></div>';
    }

    if (_isFreshEntry || _isReplayIntro) {
      setTimeout(() => {
        document.documentElement.classList.remove('entering');
        const b = document.getElementById('navBlackout');
        if (b) b.remove();
        sessionStorage.removeItem('worldEntering');
        sessionStorage.removeItem('replayIntro');
      }, 1100);
    }

    await updateCurrencyFromServer();
    loadWorldState();
    refreshNarrativeLinks();
    loadQuests();
    initMapPositions();

    try {
      const timeResp = await fetch(`/api/worlds/${currentWorldId}/time`, {
        headers: { 'Authorization': `Bearer ${getToken()}` }
      });
      if (timeResp.ok) updateTimeDisplay(await timeResp.json());
    } catch (_) {}
  } catch (error) {
    console.error("Error loading world:", error);
    document.getElementById("narrativeContent").innerHTML =
      `<div class="text-red-400 text-center py-12"><p>Error loading world: ${error.message}</p></div>`;
    document.documentElement.classList.remove('entering');
    const b = document.getElementById('navBlackout');
    if (b) b.remove();
  }
}
