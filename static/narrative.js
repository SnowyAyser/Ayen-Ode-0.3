// State
let currentWorldId = null;
let conversationHistory = [];
let currentEntities = [];
let investigationPoints = 5;
let maxInvestigationPoints = 5;
let activeInvestigations = {};
let investigationPollInterval = null;
let pendingInvestigation = null;
let panelCloseTimeout = null;
let selectedEntityId = null;
let detailHistory = [];
const entityCache = {};
const compendiumSectionState = {};

let timerTickInterval = null;

function updateInvestigationPointsDisplay() {
  const el = document.getElementById("investigationPoints");
  if (el) {
    el.textContent = `${investigationPoints}/${maxInvestigationPoints}`;
  }
}

async function updateCurrencyFromServer() {
  if (!currentWorldId) return;
  try {
    const data = await apiCall(`/api/worlds/${currentWorldId}/currencies`);
    if (data && data.balance !== undefined) {
      investigationPoints = data.balance;
      if (data.max_balance !== undefined) {
        maxInvestigationPoints = data.max_balance;
      }
      updateInvestigationPointsDisplay();
    }
  } catch (e) {
    console.error("Error updating currency:", e);
  }
}

// Settings
const SETTINGS_KEY = 'ayen_ode_settings';
function getSettings() {
  try { return JSON.parse(localStorage.getItem(SETTINGS_KEY)) || {}; } catch { return {}; }
}
function updateSettings(patch) {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify({ ...getSettings(), ...patch }));
}

// Send-confirmation state
let pendingConfirm = false;

// Cached in-game time label (survives DOM replacements in skip picker)
let currentTimeLabel = '';

function _cancelPendingConfirm() {
  if (!pendingConfirm) return;
  pendingConfirm = false;
  const el = document.getElementById('actionInput');
  if (el) {
    el.classList.remove('border-amber-600');
    el.readOnly = false;
  }
  _restoreHintText();
}
function _restoreHintText() {
  const hint = document.getElementById('inputHintText');
  if (hint) hint.textContent = 'Enter to send · Shift+Enter for new line';
}

// Pagination state
let historyRenderOffset = 0;
let historyScrollListenerAttached = false;
const HISTORY_PAGE = 100;

// Storage helpers
function _historyKey(worldId) { return `ayen_ode_history_${worldId}`; }
function saveHistoryToStorage() {
  if (currentWorldId) localStorage.setItem(_historyKey(currentWorldId), JSON.stringify(conversationHistory));
}
function loadHistoryFromStorage() {
  try { return JSON.parse(localStorage.getItem(_historyKey(currentWorldId)) || '[]'); } catch { return []; }
}

function linkifyDOMTextNodes(node) {
  if (node.nodeType === Node.TEXT_NODE) {
    const text = node.nodeValue;
    if (!text) return;

    // Build unified candidates list
    const completed = (currentEntities || []).map(e => ({ name: e.name, type: 'completed', entity: e }));
    
    const active = Object.values(activeInvestigations || {})
      .filter(inv => inv.status === 'queued' || inv.status === 'processing')
      .map(inv => ({ name: inv.itemName, type: 'active', inv }));
      
    const available = Array.from(document.querySelectorAll('.investigate-btn'))
      .filter(el => el.getAttribute('data-investigating') !== 'true')
      .map(el => ({
        name: el.getAttribute('data-inv-item'),
        type: 'available',
        entityType: el.getAttribute('data-inv-type') || 'object',
        cost: parseInt(el.getAttribute('data-inv-cost') || '1')
      }))
      .filter(c => c.name);

    const candidateMap = new Map();
    available.forEach(c => candidateMap.set(c.name.toLowerCase(), c));
    active.forEach(c => candidateMap.set(c.name.toLowerCase(), c));
    completed.forEach(c => candidateMap.set(c.name.toLowerCase(), c));

    const candidates = Array.from(candidateMap.values())
      .filter(c => c.name && c.name.length >= 2)
      .sort((a, b) => b.name.length - a.name.length);

    if (!candidates.length) return;

    const matches = [];
    candidates.forEach(candidate => {
      const escaped = candidate.name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const base = escaped.endsWith('s') ? (escaped.endsWith('es') ? escaped.slice(0, -2) + '(es)?' : escaped.slice(0, -1) + 's?') : escaped;
      const regex = new RegExp(`\\b${base}(s|es)?\\b`, 'gi');
      let m;
      while ((m = regex.exec(text)) !== null) {
        matches.push({ start: m.index, end: m.index + m[0].length, candidate, matched: m[0] });
      }
    });
    if (!matches.length) return;

    matches.sort((a, b) => a.start - b.start);
    const noOverlap = [];
    let lastEnd = 0;
    for (const m of matches) {
      if (m.start >= lastEnd) { noOverlap.push(m); lastEnd = m.end; }
    }

    const fragment = document.createDocumentFragment();
    let pos = 0;
    for (const m of noOverlap) {
      if (m.start > pos) {
        fragment.appendChild(document.createTextNode(text.slice(pos, m.start)));
      }
      
      let btn;
      if (m.candidate.type === 'completed') {
        btn = document.createElement('button');
        btn.className = "text-slate-300 hover:text-emerald-400 underline decoration-dotted decoration-emerald-500 underline-offset-2 transition-colors text-[inherit] leading-[inherit] investigated-btn";
        const ename = m.candidate.entity.name.replace(/'/g, "\\'");
        btn.setAttribute('onclick', `openInvestigatedEntity('${ename}')`);
        btn.textContent = m.matched;
      } else if (m.candidate.type === 'active') {
        const inv = m.candidate.inv;
        btn = _htmlToElement(investigatingBtnHtml(inv.itemName, inv.entityType, inv.cost || 1, m.matched));
      } else {
        const c = m.candidate;
        btn = _htmlToElement(investigateBtnHtml(c.name, c.entityType, c.cost, m.matched));
      }
      
      fragment.appendChild(btn);
      pos = m.end;
    }
    if (pos < text.length) {
      fragment.appendChild(document.createTextNode(text.slice(pos)));
    }

    node.parentNode.replaceChild(fragment, node);
    return;
  }

  const skipTags = ['BUTTON', 'A', 'SCRIPT', 'STYLE', 'TEXTAREA', 'INPUT'];
  if (node.nodeType === Node.ELEMENT_NODE && skipTags.includes(node.tagName)) {
    return;
  }

  const children = Array.from(node.childNodes);
  for (const child of children) {
    linkifyDOMTextNodes(child);
  }
}

function _makeNarrativeBlock(content) {
  const parsed = parseInvestigateText(content);
  const html = parsed.text.split('\n').map(p => p.trim()).filter(p => p).map(p => `<p>${p}</p>`).join('');
  const div = document.createElement('div');
  div.className = 'narrative-block text-slate-200 leading-7 space-y-3';
  div.innerHTML = html;
  linkifyDOMTextNodes(div);
  return div;
}

function _makeUserBlock(content) {
  const div = document.createElement('div');
  div.className = 'border-l-2 border-blue-600/50 pl-4 py-2 bg-blue-950/10 rounded-r-lg';
  div.innerHTML = `<p class="text-blue-500 text-xs font-semibold uppercase tracking-widest mb-1">You</p><p class="text-slate-300 italic">${escapeHtml(content)}</p>`;
  return div;
}

function renderHistoryToPage(history) {
  const narrativeDiv = document.getElementById("narrativeContent");
  historyRenderOffset = Math.max(0, history.length - HISTORY_PAGE);
  for (let i = historyRenderOffset; i < history.length; i++) {
    const msg = history[i];
    if (msg.role === 'assistant') narrativeDiv.appendChild(_makeNarrativeBlock(msg.content));
    else if (msg.role === 'user') narrativeDiv.appendChild(_makeUserBlock(msg.content));
  }
  if (!historyScrollListenerAttached) {
    historyScrollListenerAttached = true;
    narrativeDiv.addEventListener('scroll', function () {
      if (narrativeDiv.scrollTop < 20 && historyRenderOffset > 0) {
        const newOffset = Math.max(0, historyRenderOffset - HISTORY_PAGE);
        const slice = conversationHistory.slice(newOffset, historyRenderOffset);
        const prevHeight = narrativeDiv.scrollHeight;
        const insertRef = narrativeDiv.firstChild;
        for (let i = 0; i < slice.length; i++) {
          const msg = slice[i];
          if (msg.role === 'assistant') narrativeDiv.insertBefore(_makeNarrativeBlock(msg.content), insertRef);
          else if (msg.role === 'user') narrativeDiv.insertBefore(_makeUserBlock(msg.content), insertRef);
        }
        narrativeDiv.scrollTop += narrativeDiv.scrollHeight - prevHeight;
        historyRenderOffset = newOffset;
      }
    }, { passive: true });
  }
}

// --- Entrance / intro state (driven by URL params + sessionStorage handoff from dashboard) ---
const _entryParams = new URLSearchParams(window.location.search);
const _isFreshEntry = _entryParams.get('fresh') === '1' || sessionStorage.getItem('worldEntering') === '1';
const _isReplayIntro = _entryParams.get('replay_intro') === '1' || sessionStorage.getItem('replayIntro') === '1';
sessionStorage.removeItem('worldEntering');
sessionStorage.removeItem('replayIntro');

let _introSkipRequested = false;

// World enter overlay is no longer used — kept as no-ops so existing call sites
// don't break. The black-to-narrative transition is handled by #navBlackout
// (CSS animation in narrative.html <head>).
function showWorldEnterOverlay() { /* noop */ }
function fadeWorldEnterOverlay() { /* noop */ }

function _splitIntoLines(text) {
  return text.split('\n').map(s => s.trim()).filter(Boolean);
}

function _showReplayBadge() {
  const b = document.createElement('div');
  b.id = 'introReplayBadge';
  b.textContent = 'Replay';
  document.body.appendChild(b);
  setTimeout(() => b.remove(), 4000);
}

function _showSkipButton(onSkip) {
  const btn = document.createElement('button');
  btn.id = 'introSkipBtn';
  btn.textContent = 'Skip ›';
  btn.onclick = () => { _introSkipRequested = true; btn.remove(); onSkip(); };
  document.body.appendChild(btn);
  return btn;
}

function _sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Render the opening scene with a typewriter on the first paragraph and a
// stagger-fade for the rest. Returns a promise that resolves once the
// animation finishes (or is skipped). The DOM ends up in the same final shape
// that the static path produces, so investigate-link wiring still works.
async function playOpeningSceneIntro(handoffText) {
  const parsed = parseInvestigateText(handoffText);
  const lines = _splitIntoLines(parsed.text);
  const narrativeDiv = document.getElementById('narrativeContent');
  narrativeDiv.innerHTML = `<div class="narrative-block text-slate-200 leading-7 space-y-3" id="introBlock"></div>`;
  const block = document.getElementById('introBlock');

  let skipBtn = null;
  const skipHandler = () => {
    if (skipBtn) { skipBtn.remove(); skipBtn = null; }
    block.innerHTML = lines.map(l => `<p>${l}</p>`).join('');
    linkifyDOMTextNodes(block);
  };
  skipBtn = _showSkipButton(skipHandler);

  if (lines.length === 0) return;

  // Paragraph 1 — typewriter for plain text, instant fade-in for HTML (buttons etc.)
  const first = document.createElement('p');
  first.className = 'intro-typewriter';
  block.appendChild(first);
  const firstLine = lines[0];
  const firstLineHasHtml = /<[a-z][\s\S]*>/i.test(firstLine);
  if (firstLineHasHtml) {
    // Can't animate char-by-char through HTML tags — just reveal instantly
    first.innerHTML = firstLine;
    first.classList.add('done');
    linkifyDOMTextNodes(first);
  } else {
    const charDelay = Math.min(35, Math.max(12, 2400 / Math.max(1, firstLine.length)));
    for (let i = 0; i < firstLine.length; i++) {
      if (_introSkipRequested) break;
      first.textContent += firstLine[i];
      await _sleep(charDelay);
    }
    if (!_introSkipRequested) {
      first.textContent = firstLine;
      first.classList.add('done');
      linkifyDOMTextNodes(first);
    }
  }

  // Remaining paragraphs — stagger fade
  for (let i = 1; i < lines.length; i++) {
    if (_introSkipRequested) break;
    const p = document.createElement('p');
    p.className = 'intro-line';
    p.innerHTML = lines[i];
    block.appendChild(p);
    linkifyDOMTextNodes(p);
    requestAnimationFrame(() => p.classList.add('show'));
    await _sleep(380);
  }

  if (skipBtn) skipBtn.remove();
}

// Bootstrap
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

    // The black-to-narrative fade is owned by #navBlackout's CSS animation.
    // We just wait a small beat so the typewriter doesn't start while the
    // screen is still 100% black, then begin the reveal.
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

    // Drop the entering state once the blackout has faded (CSS animation runs
    // for ~900ms after page load) so the page returns to its normal background.
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
    // Ensure the blackout overlay is removed so the error is visible to the user!
    document.documentElement.classList.remove('entering');
    const b = document.getElementById('navBlackout');
    if (b) b.remove();
  }
}

function getEntitySubgroup(entity, type) {
  const factionNames = currentEntities
    .filter(e => (e.entity_type || e.type) === 'faction')
    .map(f => f.name).filter(Boolean);
  const tags = entity.tags || [];
  if (type === 'character') {
    const lowerTags = tags.map(t => t.toLowerCase());
    const lowerSummary = (entity.summary || '').toLowerCase();
    for (const fname of factionNames) {
      const fl = fname.toLowerCase();
      if (lowerTags.some(t => t.includes(fl) || fl.includes(t)) || lowerSummary.includes(fl)) return fname;
    }
    const familyTag = tags.find(t => /family|house|clan|bloodline/i.test(t));
    if (familyTag) return familyTag;
  }
  if (type === 'object') {
    const kw = ['weapon', 'artifact', 'document', 'relic', 'armor', 'potion', 'tool'];
    const tag = tags.find(t => kw.some(k => t.toLowerCase().includes(k)));
    if (tag) return tag;
  }
  if (type === 'location') {
    const kw = ['city', 'town', 'village', 'dungeon', 'wilderness', 'forest', 'mountain', 'castle', 'temple', 'district', 'region'];
    const tag = tags.find(t => kw.some(k => t.toLowerCase().includes(k)));
    if (tag) return tag;
  }
  if (type === 'faction') {
    const kw = ['political', 'military', 'religious', 'criminal', 'merchant', 'guild', 'noble', 'cult', 'order', 'alliance', 'council', 'brotherhood', 'sisterhood'];
    const tag = tags.find(t => kw.some(k => t.toLowerCase().includes(k)));
    if (tag) return tag;
  }
  return null;
}

function _renderCompendiumCard(e, style) {
  const eid = e.entity_id || e.id;
  const isSelected = eid === selectedEntityId;
  return `
    <div id="card-${eid}" class="rounded-lg overflow-hidden${isSelected ? ' is-selected' : ''}">
      <button
        onclick="selectEntity('${eid}')"
        class="w-full flex items-center gap-2 px-2.5 py-2 hover:bg-slate-800/60 transition-colors text-left min-w-0"
      >
        <div class="w-1 h-1 rounded-full flex-none ${style.dot} opacity-40 entity-dot"></div>
        <span class="text-sm text-slate-200 truncate flex-1">${capFirst(e.name)}</span>
      </button>
    </div>
  `;
}

function _renderCompendiumSubSection(subId, label, ents, style, searchQuery) {
  const subOpen = searchQuery ? true : (compendiumSectionState[subId] === true);
  return `
    <div class="ml-2 mb-0.5">
      <button
        onclick="toggleCompendiumSection('${subId}')"
        class="w-full flex items-center justify-between px-2 py-1 rounded-md hover:bg-slate-800/30 transition-colors"
      >
        <div class="flex items-center gap-1.5">
          <span class="text-xs text-slate-500 italic">${capFirst(label)}</span>
          <span class="text-xs text-slate-700">${ents.length}</span>
        </div>
        <span id="${subId}-icon" class="text-slate-700 text-xs">${subOpen ? '▾' : '▸'}</span>
      </button>
      <div id="${subId}" class="${subOpen ? '' : 'hidden'} space-y-px mt-px">
        ${ents.map(e => _renderCompendiumCard(e, style)).join('')}
      </div>
    </div>
  `;
}

function loadWorldState() {
  try {
    const searchQuery = (document.getElementById("compendiumSearch")?.value || '').toLowerCase().trim();

    const seenIds = new Set();
    const seenNameType = new Set();
    currentEntities = currentEntities.filter(e => {
      const id = e.entity_id || e.id;
      const nameType = `${(e.name || '').toLowerCase()}|${e.entity_type || e.type || ''}`;
      if ((id && seenIds.has(id)) || seenNameType.has(nameType)) return false;
      if (id) seenIds.add(id);
      seenNameType.add(nameType);
      return true;
    });

    if (!currentEntities || currentEntities.length === 0) {
      document.getElementById("entityListView").innerHTML =
        '<p class="text-slate-600 text-xs px-2 py-3">No entities yet. They will appear as the story unfolds.</p>';
      return;
    }

    const typeStyle = {
      character: { label: 'Characters', color: 'text-blue-400',    dot: 'bg-blue-500' },
      location:  { label: 'Locations',  color: 'text-emerald-400', dot: 'bg-emerald-500' },
      faction:   { label: 'Factions',   color: 'text-purple-400',  dot: 'bg-purple-500' },
      object:    { label: 'Objects',    color: 'text-orange-400',  dot: 'bg-orange-500' },
      event:     { label: 'Events',     color: 'text-red-400',     dot: 'bg-red-500' },
    };

    const grouped = {};
    currentEntities.forEach(e => {
      const name = (e.name || '').toLowerCase();
      const summary = (e.summary || '').toLowerCase();
      if (searchQuery && !name.includes(searchQuery) && !summary.includes(searchQuery)) return;
      const etype = e.entity_type || e.type || 'unknown';
      if (!grouped[etype]) grouped[etype] = [];
      grouped[etype].push(e);
    });

    if (Object.keys(grouped).length === 0) {
      document.getElementById("entityListView").innerHTML =
        '<p class="text-slate-600 text-xs px-2 py-3">No results.</p>';
      return;
    }

    let html = '';
    Object.entries(grouped).forEach(([type, ents]) => {
      const style = typeStyle[type] || { label: type.charAt(0).toUpperCase() + type.slice(1) + 's', color: 'text-slate-400', dot: 'bg-slate-500' };
      const sectionId = `type-section-${type}`;
      const isOpen = searchQuery ? true : (compendiumSectionState[sectionId] === true);

      const subGroups = {};
      const ungrouped = [];
      ents.forEach(e => {
        const sg = getEntitySubgroup(e, type);
        if (sg) { if (!subGroups[sg]) subGroups[sg] = []; subGroups[sg].push(e); }
        else ungrouped.push(e);
      });
      const hasSubGroups = Object.keys(subGroups).length > 0;

      let innerHtml = '';
      if (hasSubGroups) {
        Object.entries(subGroups).forEach(([sgName, sgEnts]) => {
          const subId = `sub-${type}-${sgName.replace(/[^a-z0-9]/gi, '-').toLowerCase()}`;
          innerHtml += _renderCompendiumSubSection(subId, sgName, sgEnts, style, searchQuery);
        });
        if (ungrouped.length > 0) {
          innerHtml += _renderCompendiumSubSection(`sub-${type}-independent`, 'Independent', ungrouped, style, searchQuery);
        }
      } else {
        innerHtml = ents.map(e => _renderCompendiumCard(e, style)).join('');
      }

      html += `
        <div class="mb-0.5">
          <button
            onclick="toggleCompendiumSection('${sectionId}')"
            class="w-full flex items-center justify-between px-2 py-1.5 rounded-md hover:bg-slate-800/40 transition-colors"
          >
            <div class="flex items-center gap-2">
              <div class="w-1.5 h-1.5 rounded-full flex-none ${style.dot} opacity-60"></div>
              <span class="text-xs font-semibold ${style.color} uppercase tracking-widest">${style.label}</span>
              <span class="text-xs text-slate-700">${ents.length}</span>
            </div>
            <span id="${sectionId}-icon" class="text-slate-700 text-xs">${isOpen ? '▾' : '▸'}</span>
          </button>
          <div id="${sectionId}" class="${isOpen ? '' : 'hidden'} space-y-px mt-px">
            ${innerHtml}
          </div>
        </div>
      `;
    });

    document.getElementById("entityListView").innerHTML = html;
    const narrativeDiv = document.getElementById("narrativeContent");
    if (narrativeDiv) {
      linkifyDOMTextNodes(narrativeDiv);
    }
  } catch (error) {
    console.error("Error loading world state:", error);
  }
}

function getNarrativeStatDescription(value) {
  if (value < 20) return 'Weak';
  if (value < 40) return 'Fragile';
  if (value < 60) return 'Moderate';
  if (value < 80) return 'Strong';
  return 'Exceptional';
}

function toggleCompendiumSection(sectionId) {
  const section = document.getElementById(sectionId);
  const icon = document.getElementById(`${sectionId}-icon`);
  if (!section) return;
  const isHidden = section.classList.contains('hidden');
  section.classList.toggle('hidden');
  if (icon) icon.textContent = isHidden ? '▾' : '▸';
  compendiumSectionState[sectionId] = isHidden;
}

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function capFirst(s) { return s ? s.charAt(0).toUpperCase() + s.slice(1) : s; }

// Input area helpers
function _draftKey() { return `ayen_ode_draft_${currentWorldId}`; }

function autoResizeTextarea(el) {
  el.style.height = '0px';
  const full = el.scrollHeight;
  el.style.height = Math.min(full, 164) + 'px';
  el.style.overflowY = full > 164 ? 'auto' : 'hidden';
}

function updateCharCount(el) {
  const counter = document.getElementById('charCount');
  if (!counter) return;
  const len = el.value.length;
  if (len === 0) { counter.classList.add('hidden'); return; }
  counter.classList.remove('hidden');
  counter.textContent = len;
}

function saveDraft() {
  const el = document.getElementById('actionInput');
  if (currentWorldId && el) localStorage.setItem(_draftKey(), el.value);
}

function restoreDraft() {
  const el = document.getElementById('actionInput');
  if (!el || !currentWorldId) return;
  const draft = localStorage.getItem(_draftKey()) || '';
  if (draft) { el.value = draft; autoResizeTextarea(el); updateCharCount(el); }
}

function formatSeconds(s) {
  if (!s || s <= 0) return '';
  const days = Math.floor(s / 86400);
  const hours = Math.floor((s % 86400) / 3600);
  if (days > 0) return `Day ${days + 1}` + (hours > 0 ? `, Hour ${hours}` : '');
  if (hours > 0) return `Hour ${hours}`;
  const mins = Math.floor(s / 60);
  return mins > 0 ? `${mins} min elapsed` : `${s}s elapsed`;
}

function updateTimeDisplay(gameTime) {
  const label = (gameTime && gameTime.label) ? gameTime.label : formatSeconds(gameTime && gameTime.seconds);
  if (!label) return;
  currentTimeLabel = label;
  const gameLbl = document.getElementById('gameTimeLabel');
  if (gameLbl) gameLbl.textContent = label;
  const skipBtn = document.getElementById('skipTimeBtn');
  if (skipBtn) skipBtn.classList.remove('hidden');
}

function quickAction(text) {
  const el = document.getElementById('actionInput');
  if (!el) return;
  el.value = text;
  autoResizeTextarea(el);
  updateCharCount(el);
  saveDraft();
  el.focus();
  el.setSelectionRange(text.length, text.length);
}

// Narrative action form
document.getElementById("actionForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const actionText = document.getElementById("actionInput").value.trim();
  if (!actionText) return;

  // Confirmation mode: first submission arms the confirm state; second submission fires
  if (getSettings().confirmBeforeSend && !pendingConfirm) {
    pendingConfirm = true;
    const inputEl = document.getElementById('actionInput');
    inputEl.classList.add('border-amber-600');
    inputEl.readOnly = true;
    const hint = document.getElementById('inputHintText');
    if (hint) hint.textContent = 'Press Enter to send  ·  Esc to cancel';
    return;
  }
  pendingConfirm = false;
  const inputEl0 = document.getElementById('actionInput');
  inputEl0.classList.remove('border-amber-600');
  inputEl0.readOnly = false;
  _restoreHintText();

  const inputEl = document.getElementById("actionInput");
  inputEl.value = "";
  autoResizeTextarea(inputEl);
  updateCharCount(inputEl);
  if (currentWorldId) localStorage.removeItem(_draftKey());

  const submitBtn = document.getElementById("submitBtn");
  submitBtn.disabled = true;
  const btnLoader = document.createElement('div');
  btnLoader.className = 'flex items-center justify-center gap-1.5';
  const cloverWrap = document.createElement('div');
  CloverLoader.createLoader(cloverWrap, 16, 38);
  btnLoader.appendChild(cloverWrap);
  btnLoader.appendChild(Object.assign(document.createElement('span'), { textContent: '…' }));
  submitBtn.replaceChildren(btnLoader);

  try {
    const narrativeDiv = document.getElementById("narrativeContent");
    narrativeDiv.appendChild(_makeUserBlock(actionText));
    narrativeDiv.scrollTop = narrativeDiv.scrollHeight;

    const response = await fetch("/api/narrative", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${getToken()}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        world_id: currentWorldId,
        action: actionText,
        history: conversationHistory,
      }),
    });

    if (!response.ok) throw new Error("Failed to process action");

    const data = await response.json();
    const narrativeResponse = data.narrative;
    conversationHistory = data.history || conversationHistory;
    saveHistoryToStorage();

    if (data.investigation_points !== undefined) {
      investigationPoints = data.investigation_points;
      if (data.max_investigation_points !== undefined) maxInvestigationPoints = data.max_investigation_points;
      updateInvestigationPointsDisplay();
    }
    if (data.game_time) updateTimeDisplay(data.game_time);

    narrativeDiv.appendChild(_makeNarrativeBlock(narrativeResponse));
    refreshNarrativeLinks();

    narrativeDiv.scrollTop = narrativeDiv.scrollHeight;

    try {
      const worldResp = await fetch(`/api/world?world_id=${currentWorldId}`, {
        headers: { "Authorization": `Bearer ${getToken()}` }
      });
      if (worldResp.ok) {
        const worldData = await worldResp.json();
        currentEntities = worldData.entities || [];
      }
    } catch (_) {}

    await updateCurrencyFromServer();
    loadWorldState();
    loadQuests();
  } catch (error) {
    console.error("Error processing action:", error);
    document.getElementById("narrativeContent").innerHTML +=
      `<div class="text-red-400 text-sm p-3 bg-red-950/20 border border-red-900/30 rounded-lg">Error: ${error.message}</div>`;
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = 'Act';
    document.getElementById("actionInput").focus();
  }
});

setTimeout(() => { const el = document.getElementById("actionInput"); el.focus(); autoResizeTextarea(el); }, 500);
document.getElementById("compendiumSearch").addEventListener("input", loadWorldState);

// Settings popover
(function () {
  const btn = document.getElementById('settingsBtn');
  const popover = document.getElementById('settingsPopover');
  const toggle = document.getElementById('confirmToggle');
  console.log("[SettingsPopover] Elements found:", { btn, popover, toggle });
  if (!btn || !popover || !toggle) {
    console.warn("[SettingsPopover] Initialization failed: missing element!");
    return;
  }

  function syncToggle() {
    const on = !!getSettings().confirmBeforeSend;
    toggle.setAttribute('data-on', on ? '1' : '0');
    toggle.className = on
      ? 'relative inline-flex h-5 w-9 items-center rounded-full bg-amber-600 transition-colors focus:outline-none flex-none'
      : 'relative inline-flex h-5 w-9 items-center rounded-full bg-slate-600 transition-colors focus:outline-none flex-none';
    toggle.innerHTML = `<span class="inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform ${on ? 'translate-x-4' : 'translate-x-1'}"></span>`;
  }
  syncToggle();

  btn.addEventListener('click', (e) => {
    console.log("[SettingsPopover] Click registered!");
    e.stopPropagation();
    popover.classList.toggle('hidden');
    syncToggle();
  });

  toggle.addEventListener('click', () => {
    const current = !!getSettings().confirmBeforeSend;
    updateSettings({ confirmBeforeSend: !current });
    if (!current === false) _cancelPendingConfirm();
    syncToggle();
  });

  document.addEventListener('click', (e) => {
    if (!popover.classList.contains('hidden') && !popover.contains(e.target) && e.target !== btn) {
      popover.classList.add('hidden');
    }
  });
})();

function showSkipPicker() {
  document.getElementById('skipPickerPopover')?.classList.remove('hidden');
}

function cancelSkipPicker() {
  document.getElementById('skipPickerPopover')?.classList.add('hidden');
}

async function doSkipTime(seconds) {
  if (!currentWorldId) return;
  cancelSkipPicker();
  try {
    const resp = await fetch(`/api/worlds/${currentWorldId}/skip-time`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${getToken()}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ seconds }),
    });
    const data = await resp.json();
    if (!resp.ok) {
      const blocking = data.blocking || {};
      const jobNames = (blocking.investigation || []).map(j => j.name).join(', ');
      const msg = jobNames ? `Active: ${jobNames}` : (data.error || 'Cannot skip time');
      const lbl = document.getElementById('gameTimeLabel');
      if (lbl) {
        const saved = lbl.textContent;
        lbl.textContent = `⚠ ${msg}`;
        lbl.classList.add('text-amber-500', 'text-right');
        setTimeout(() => { lbl.textContent = saved; lbl.classList.remove('text-amber-500', 'text-right'); }, 3500);
      }
      return;
    }
    if (data.game_time) updateTimeDisplay(data.game_time);
  } catch (_) {}
}

// Close skip picker on outside click
document.addEventListener('click', (e) => {
  const pop = document.getElementById('skipPickerPopover');
  const btn = document.getElementById('skipTimeBtn');
  if (pop && !pop.classList.contains('hidden') && !pop.contains(e.target) && e.target !== btn) {
    pop.classList.add('hidden');
  }
});

// Textarea: auto-resize, char count, draft, history navigation
(function () {
  const el = document.getElementById('actionInput');
  if (!el) return;

  autoResizeTextarea(el);

  el.addEventListener('input', () => {
    autoResizeTextarea(el);
    updateCharCount(el);
    saveDraft();
  });

  el.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      document.getElementById('actionForm').requestSubmit();
    } else if (e.key === 'Escape' && pendingConfirm) {
      e.preventDefault();
      _cancelPendingConfirm();
    }
  });
})();