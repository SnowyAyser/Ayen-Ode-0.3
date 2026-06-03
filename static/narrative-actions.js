// Bootstrap & core worlds loaders
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

let lastUserBlockNode = null;
let currentClarifyPayload = null;

async function executeNarrativeSubmit(actionText, isClarificationSubmit = false) {
  const submitBtn = document.getElementById("submitBtn");
  submitBtn.disabled = true;
  const btnLoader = document.createElement('div');
  btnLoader.className = 'flex items-center justify-center gap-1.5';
  const cloverWrap = document.createElement('div');
  CloverLoader.createLoader(cloverWrap, 16, 38);
  btnLoader.appendChild(cloverWrap);
  
  const statusSpan = Object.assign(document.createElement('span'), {
    id: 'actionStageStatus',
    textContent: '…',
    className: 'text-xs text-slate-400 font-mono ml-1 max-w-[200px] truncate'
  });
  btnLoader.appendChild(statusSpan);
  submitBtn.replaceChildren(btnLoader);

  let activeStageInterval = null;
  if (currentWorldId) {
    activeStageInterval = setInterval(async () => {
      try {
        const res = await fetch(`/api/worlds/${currentWorldId}/active-stage`, {
          headers: { "Authorization": `Bearer ${getToken()}` }
        });
        if (res.ok) {
          const d = await res.json();
          const statusEl = document.getElementById('actionStageStatus');
          if (statusEl && d.active_stage) {
            statusEl.textContent = d.active_stage;
          }
        }
      } catch (err) {
        console.warn("Failed to fetch active stage status", err);
      }
    }, 500);
  }

  const narrativeDiv = document.getElementById("narrativeContent");
  if (!isClarificationSubmit) {
    lastUserBlockNode = _makeUserBlock(actionText);
    narrativeDiv.appendChild(lastUserBlockNode);
    narrativeDiv.scrollTop = narrativeDiv.scrollHeight;
  }

  try {
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

    // Check if narrativeResponse is JSON
    let isJson = false;
    let jsonPayload = null;
    try {
      jsonPayload = JSON.parse(narrativeResponse);
      isJson = true;
    } catch (_) {}

    if (isJson && jsonPayload && jsonPayload["player.move"] === true) {
      const subj = (jsonPayload["towards.subject"] || "").trim().toLowerCase();
      if (subj === "self" || subj === "you") {
        jsonPayload["towards.subject"] = "self";
      }
      
      const dir = (jsonPayload["move.direction"] || "").toLowerCase();
      if (["north", "south", "east", "west", "forwards", "back"].includes(dir)) {
        if (!jsonPayload["towards.subject"]) {
          jsonPayload["towards.subject"] = "self";
        }
      }
    }

    if (isJson && jsonPayload && jsonPayload["player.identify"] === true) {
      const targetName = jsonPayload["identify.target"];
      if (!targetName) {
        if (activeStageInterval) clearInterval(activeStageInterval);
        submitBtn.disabled = false;
        submitBtn.textContent = 'Act';
        if (lastUserBlockNode) {
          lastUserBlockNode.remove();
          lastUserBlockNode = null;
        }
        const inputEl = document.getElementById("actionInput");
        inputEl.value = actionText;
        autoResizeTextarea(inputEl);
        updateCharCount(inputEl);
        inputEl.focus();
        const errBanner = document.getElementById("noMovementError");
        const errText = document.getElementById("noMovementErrorText");
        if (errBanner && errText) {
          errText.textContent = "Please specify a target to identify or inspect.";
          errBanner.classList.remove("hidden");
        }
        return;
      }
      
      const resolvedTarget = resolveSubjectName(targetName);
      const targetPos = getSubjectCoord(resolvedTarget);
      const dx = targetPos.x - playerPos.x;
      const dy = targetPos.y - playerPos.y;
      const distInches = Math.sqrt(dx * dx + dy * dy);
      
      if (distInches > 36) {
        if (activeStageInterval) clearInterval(activeStageInterval);
        submitBtn.disabled = false;
        submitBtn.textContent = 'Act';
        if (lastUserBlockNode) {
          lastUserBlockNode.remove();
          lastUserBlockNode = null;
        }
        const inputEl = document.getElementById("actionInput");
        inputEl.value = actionText;
        autoResizeTextarea(inputEl);
        updateCharCount(inputEl);
        inputEl.focus();
        const errBanner = document.getElementById("noMovementError");
        const errText = document.getElementById("noMovementErrorText");
        if (errBanner && errText) {
          const distFt = (distInches / 12).toFixed(1);
          const prettyTarget = resolvedTarget.split(" ").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
          errText.textContent = `You are too far away to identify or inspect the ${prettyTarget}. You must be within 3 feet (currently ${distFt} ft away).`;
          errBanner.classList.remove("hidden");
        }
        return;
      }
      
      if (activeStageInterval) clearInterval(activeStageInterval);
      submitBtn.disabled = false;
      submitBtn.textContent = 'Act';
      
      lastUserBlockNode = null;
      document.getElementById("noMovementError")?.classList.add("hidden");
      
      conversationHistory = data.history || conversationHistory;
      saveHistoryToStorage();
      
      narrativeDiv.appendChild(_makeNarrativeBlock(narrativeResponse, {
        theme_report: data.theme_report,
        quest_report: data.quest_report,
        mechanics_report: data.mechanics_report
      }));
      refreshNarrativeLinks();
      narrativeDiv.scrollTop = narrativeDiv.scrollHeight;
      
      loadWorldState();
      loadQuests();
      return;
    }

    const needsClarification = isJson && jsonPayload && jsonPayload["player.move"] === true && (
      !jsonPayload["towards.subject"] ||
      jsonPayload["move.distance_inches"] === null ||
      !jsonPayload["move.direction"]
    );

    if (!isJson || (jsonPayload && jsonPayload["player.move"] === false)) {
      // Text response or player.move: false indicates no movement action was detected
      if (activeStageInterval) clearInterval(activeStageInterval);
      submitBtn.disabled = false;
      submitBtn.textContent = 'Act';
      
      // Remove temporary player block from the chat
      if (lastUserBlockNode) {
        lastUserBlockNode.remove();
        lastUserBlockNode = null;
      }
      
      // Restore user text back into `#actionInput`
      const inputEl = document.getElementById("actionInput");
      inputEl.value = actionText;
      autoResizeTextarea(inputEl);
      updateCharCount(inputEl);
      inputEl.focus();
      
      // Show overhead error message
      const errBanner = document.getElementById("noMovementError");
      const errText = document.getElementById("noMovementErrorText");
      if (errBanner && errText) {
        let msg = "No movement detected. Please clarify your movement action to proceed.";
        if (!isJson) {
          msg = narrativeResponse || msg;
        } else if (jsonPayload && jsonPayload.clarification_prompt) {
          msg = jsonPayload.clarification_prompt;
        }
        errText.textContent = msg;
        errBanner.classList.remove("hidden");
      }
      return;
    } else if (needsClarification) {
      // JSON lacks required parameters (and player.move is true)
      if (activeStageInterval) clearInterval(activeStageInterval);
      submitBtn.disabled = false;
      submitBtn.textContent = 'Act';
      
      // Hide any active overhead error
      document.getElementById("noMovementError")?.classList.add("hidden");
      
      let missingFields = [];
      if (!jsonPayload["towards.subject"]) {
        missingFields.push("target subject (e.g. 'old man')");
      }
      if (jsonPayload["move.distance_inches"] === null) {
        missingFields.push("distance (e.g. 3 feet)");
      }
      if (!jsonPayload["move.direction"]) {
        missingFields.push("direction (e.g. 'towards' or 'away')");
      }
      
      const promptText = "Clarification needed: please provide the missing movement details: " + missingFields.join(", ") + ".";
      openClarifyModal(promptText, jsonPayload);
      return;
    }

    // Success: movement JSON is correct and complete
    lastUserBlockNode = null;
    document.getElementById("noMovementError")?.classList.add("hidden");

    if (isJson && jsonPayload && jsonPayload["player.move"] === true) {
      updatePlayerLocationFromPayload(jsonPayload);
    }

    conversationHistory = data.history || conversationHistory;
    saveHistoryToStorage();

    if (data.investigation_points !== undefined) {
      investigationPoints = data.investigation_points;
      if (data.max_investigation_points !== undefined) maxInvestigationPoints = data.max_investigation_points;
      updateInvestigationPointsDisplay();
    }
    if (data.game_time) updateTimeDisplay(data.game_time);

    narrativeDiv.appendChild(_makeNarrativeBlock(narrativeResponse, {
      theme_report: data.theme_report,
      quest_report: data.quest_report,
      mechanics_report: data.mechanics_report
    }));
    refreshNarrativeLinks();

    narrativeDiv.scrollTop = narrativeDiv.scrollHeight;

    try {
      const worldResp = await fetch(`/api/world?world_id=${currentWorldId}`, {
        headers: { "Authorization": `Bearer ${getToken()}` }
      });
      if (worldResp.ok) {
        const worldData = await worldResp.json();
        currentEntities = worldData.entities || [];
        for (const key in entityCache) delete entityCache[key];
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
    if (activeStageInterval) {
      clearInterval(activeStageInterval);
    }
    submitBtn.disabled = false;
    submitBtn.textContent = 'Act';
    document.getElementById("actionInput").focus();
  }
}

function openClarifyModal(promptText, jsonPayload) {
  currentClarifyPayload = jsonPayload;
  
  const modal = document.getElementById("movementClarifyModal");
  document.getElementById("clarifyPromptText").textContent = promptText;
  
  // Hide all fields by default
  document.getElementById("fieldFullAction").classList.add("hidden");
  document.getElementById("fieldSubject").classList.add("hidden");
  document.getElementById("fieldDistance").classList.add("hidden");
  document.getElementById("fieldDirection").classList.add("hidden");
  
  const detailsBox = document.getElementById("statusDetails");
  const detectedText = document.getElementById("statusDetected");
  
  // Populate the scene subjects datalist
  const datalist = document.getElementById("sceneSubjectsList");
  if (datalist) {
    const subjects = (typeof currentEntities !== "undefined" ? currentEntities.map(e => e.name) : []).filter(Boolean);
    if (!subjects.includes("old man")) subjects.push("old man");
    datalist.innerHTML = subjects.map(s => `<option value="${s}"></option>`).join("");
  }

  // Clear inputs
  document.getElementById("inputFullAction").value = "";
  document.getElementById("inputSubject").value = "";
  document.getElementById("inputDistanceValue").value = "";
  document.getElementById("inputDistanceUnit").value = "feet";
  document.getElementById("inputDirection").value = "";

  if (!jsonPayload) {
    // Suppressed: no movement detected case is now handled outside modal, but keep as fallback
    detectedText.textContent = "No";
    detectedText.className = "text-red-400 font-semibold";
    detailsBox.classList.add("hidden");
    document.getElementById("fieldFullAction").classList.remove("hidden");
    setTimeout(() => document.getElementById("inputFullAction").focus(), 100);
  } else {
    detectedText.textContent = "Yes";
    detectedText.className = "text-emerald-400 font-semibold";
    detailsBox.classList.remove("hidden");
    
    document.getElementById("statusSubject").textContent = jsonPayload["towards.subject"] || "—";
    document.getElementById("statusDistance").textContent = jsonPayload["move.distance_inches"] !== null ? `${jsonPayload["move.distance_inches"]} inches` : "—";
    document.getElementById("statusDirection").textContent = jsonPayload["move.direction"] || "—";
    
    let focusElement = null;
    
    // Check what is missing/unclear and show those input fields
    if (!jsonPayload["towards.subject"]) {
      document.getElementById("fieldSubject").classList.remove("hidden");
      if (!focusElement) focusElement = document.getElementById("inputSubject");
    }
    
    if (jsonPayload["move.distance_inches"] === null) {
      document.getElementById("fieldDistance").classList.remove("hidden");
      if (!focusElement) focusElement = document.getElementById("inputDistanceValue");
    }
    
    if (!jsonPayload["move.direction"]) {
      document.getElementById("fieldDirection").classList.remove("hidden");
      if (!focusElement) focusElement = document.getElementById("inputDirection");
    }
    
    if (focusElement) {
      setTimeout(() => focusElement.focus(), 100);
    }
  }
  
  modal.classList.remove("hidden");
}

function closeClarifyModal() {
  document.getElementById("movementClarifyModal").classList.add("hidden");
  // Cancel action: remove the last user block
  if (lastUserBlockNode) {
    lastUserBlockNode.remove();
    lastUserBlockNode = null;
  }
  document.getElementById("actionInput").focus();
}

async function submitClarifiedAction() {
  const modal = document.getElementById("movementClarifyModal");
  
  let reconstructedText = "";
  if (!currentClarifyPayload) {
    // Fallback rewrite case
    reconstructedText = document.getElementById("inputFullAction").value.trim();
    if (!reconstructedText) return;
  } else {
    // Parameter clarification case
    const subjectVal = document.getElementById("inputSubject").value.trim() || currentClarifyPayload["towards.subject"] || "";
    
    let distanceVal = "";
    if (!document.getElementById("fieldDistance").classList.contains("hidden")) {
      const distNum = document.getElementById("inputDistanceValue").value.trim();
      const distUnit = document.getElementById("inputDistanceUnit").value;
      if (distNum) {
        distanceVal = `${distNum} ${distUnit}`;
      }
    } else {
      distanceVal = currentClarifyPayload["move.distance_inches"] !== null ? `${currentClarifyPayload["move.distance_inches"]} inches` : "";
    }
    
    const directionVal = document.getElementById("inputDirection").value || currentClarifyPayload["move.direction"] || "towards";
    
    if (!subjectVal && !document.getElementById("fieldSubject").classList.contains("hidden")) {
      alert("Please clarify the target subject.");
      return;
    }
    if (!distanceVal && !document.getElementById("fieldDistance").classList.contains("hidden")) {
      alert("Please clarify the distance.");
      return;
    }
    
    reconstructedText = `I move ${distanceVal} ${directionVal} ${subjectVal}`.trim();
  }
  
  modal.classList.add("hidden");
  
  if (lastUserBlockNode) {
    lastUserBlockNode.querySelector(".italic").textContent = reconstructedText;
  } else {
    const narrativeDiv = document.getElementById("narrativeContent");
    lastUserBlockNode = _makeUserBlock(reconstructedText);
    narrativeDiv.appendChild(lastUserBlockNode);
    narrativeDiv.scrollTop = narrativeDiv.scrollHeight;
  }
  
  await executeNarrativeSubmit(reconstructedText, true);
}

document.getElementById("actionForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const actionText = document.getElementById("actionInput").value.trim();
  if (!actionText) return;

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

  await executeNarrativeSubmit(actionText, false);
});

setTimeout(() => { const el = document.getElementById("actionInput"); el.focus(); autoResizeTextarea(el); }, 500);
document.getElementById("compendiumSearch").addEventListener("input", loadWorldState);

// Tactical Map Implementation
let playerPos = { x: 0, y: 0 };
let manPos = { x: 60, y: 60 }; // 5 feet East, 5 feet North (60 inches)
let lastTargetSubject = "old man";
let hoveredSubject = null;
let mapViewportRadiusInches = 240; // Default visible viewport radius (20 feet)
let mapPan = { x: 0, y: 0 }; // Pan offsets in grid inches

const defaultEntities = [
  { name: "old man", type: "character" },
  { name: "paladin guard", type: "character" },
  { name: "wooden chest", type: "object" },
  { name: "stone archway", type: "location" }
];

function resolveSubjectName(name) {
  const normName = (name || "").trim().toLowerCase();
  if (!normName) return "";
  
  if (normName === "self" || normName === "you" || normName === "player") {
    return "self";
  }
  
  const entitiesToDraw = [...(typeof currentEntities !== "undefined" ? currentEntities : [])];
  const defaults = [
    { name: "old man", type: "character" },
    { name: "paladin guard", type: "character" },
    { name: "wooden chest", type: "object" },
    { name: "stone archway", type: "location" }
  ];
  
  defaults.forEach(d => {
    if (!entitiesToDraw.some(e => e.name.toLowerCase() === d.name.toLowerCase())) {
      entitiesToDraw.push(d);
    }
  });
  
  for (const e of entitiesToDraw) {
    if (e.name.toLowerCase() === normName) {
      return e.name.toLowerCase();
    }
  }
  
  for (const e of entitiesToDraw) {
    const sName = e.name.toLowerCase();
    if (sName.includes(normName) || normName.includes(sName)) {
      return sName;
    }
  }
  
  return normName;
}

function getSubjectCoord(name) {
  const resolved = resolveSubjectName(name);
  if (resolved === "self") return playerPos;
  if (resolved === "old man") return { x: 60, y: 60 };
  
  // Simple hash function to generate reproducible coordinates for dynamic entities
  let hash = 0;
  for (let i = 0; i < resolved.length; i++) {
    hash = resolved.charCodeAt(i) + ((hash << 5) - hash);
  }
  
  // Distribute angle between 0 and 2*PI deterministically
  const angle = Math.abs(hash % 360) * (Math.PI / 180);
  // Keep all dynamic subjects strictly inside the 20ft viewport: 3.5ft (42 inches) to 15ft (180 inches)
  const dist = 42 + (Math.abs(hash >> 8) % 138);
  
  return {
    x: Math.round(dist * Math.cos(angle)),
    y: Math.round(dist * Math.sin(angle))
  };
}

function initMapPositions() {
  const savedPlayer = localStorage.getItem("mapPlayerPos");
  const savedTarget = localStorage.getItem("mapLastTarget");
  if (savedPlayer) {
    try { playerPos = JSON.parse(savedPlayer); } catch(_) {}
  } else {
    playerPos = { x: 0, y: 0 };
  }
  mapPan = { x: 0, y: 0 };
  
  if (savedTarget) {
    lastTargetSubject = savedTarget;
  }
  drawMap();
}

function saveMapPositions() {
  localStorage.setItem("mapPlayerPos", JSON.stringify(playerPos));
  localStorage.setItem("mapLastTarget", lastTargetSubject);
}

function getMapViewParams() {
  const canvas = document.getElementById("mapCanvas");
  if (!canvas) return null;
  const rect = canvas.getBoundingClientRect();
  const width = rect.width;
  const height = rect.height;
  
  const entitiesToDraw = [...(typeof currentEntities !== "undefined" ? currentEntities : [])];
  defaultEntities.forEach(d => {
    if (!entitiesToDraw.some(e => e.name.toLowerCase() === d.name.toLowerCase())) {
      entitiesToDraw.push(d);
    }
  });

  let minX = playerPos.x;
  let maxX = playerPos.x;
  let minY = playerPos.y;
  let maxY = playerPos.y;

  entitiesToDraw.forEach(e => {
    const coords = getSubjectCoord(e.name);
    minX = Math.min(minX, coords.x);
    maxX = Math.max(maxX, coords.x);
    minY = Math.min(minY, coords.y);
    maxY = Math.max(maxY, coords.y);
  });
  
  const dx = maxX - minX;
  const dy = maxY - minY;
  
  const centerX = minX + dx / 2;
  const centerY = minY + dy / 2;
  
  const padding = 35;
  const minDimension = Math.min(width - padding * 2, height - padding * 2);
  let scale = minDimension / (mapViewportRadiusInches * 2);
  
  let viewCenterX = centerX + mapPan.x;
  let viewCenterY = centerY + mapPan.y;
  
  // Calculate canvas coordinate of player with current viewCenterX/viewCenterY and scale
  let px = width / 2 + (playerPos.x - viewCenterX) * scale;
  let py = height / 2 - (playerPos.y - viewCenterY) * scale;
  
  // Calculate furthest corner from player in canvas space
  const maxCornerDistPx = Math.max(
    Math.sqrt(px * px + py * py),
    Math.sqrt((width - px) ** 2 + py * py),
    Math.sqrt(px * px + (height - py) ** 2),
    Math.sqrt((width - px) ** 2 + (height - py) ** 2)
  );
  
  // Clamp scale so that player to furthest point never exceeds 20 feet (240 inches)
  const minScale = maxCornerDistPx / 240;
  if (scale < minScale) {
    scale = minScale;
    mapViewportRadiusInches = minDimension / (scale * 2);
    viewCenterX = centerX + mapPan.x;
    viewCenterY = centerY + mapPan.y;
  }
  
  function toCanvas(pos) {
    return {
      x: width / 2 + (pos.x - viewCenterX) * scale,
      y: height / 2 - (pos.y - viewCenterY) * scale
    };
  }
  
  return {
    canvas,
    rect,
    width,
    height,
    scale,
    toCanvas,
    centerX,
    centerY,
    viewCenterX,
    viewCenterY,
    minX,
    maxX,
    minY,
    maxY,
    entitiesToDraw
  };
}

function drawMap() {
  const params = getMapViewParams();
  if (!params) return;
  const { canvas, width, height, scale, toCanvas, viewCenterX, viewCenterY, entitiesToDraw } = params;
  const ctx = canvas.getContext("2d");
  
  canvas.width = width * window.devicePixelRatio;
  canvas.height = height * window.devicePixelRatio;
  ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
  
  // Clear canvas
  ctx.fillStyle = "#020617"; // slate-950
  ctx.fillRect(0, 0, width, height);
  
  // Draw grid background
  ctx.strokeStyle = "#1e293b"; // slate-800
  ctx.lineWidth = 0.5;
  const gridSpacing = 20;
  for (let x = 0; x < width; x += gridSpacing) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, height);
    ctx.stroke();
  }
  for (let y = 0; y < height; y += gridSpacing) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(width, y);
    ctx.stroke();
  }
  
  // Draw step crosshairs and coordinates every 10 feet (120 inches)
  ctx.fillStyle = "rgba(148, 163, 184, 0.4)";
  ctx.font = "7px monospace";
  ctx.textAlign = "center";
  const step = 120;
  
  const minVisibleX = viewCenterX - (width / 2) / scale;
  const maxVisibleX = viewCenterX + (width / 2) / scale;
  const minVisibleY = viewCenterY - (height / 2) / scale;
  const maxVisibleY = viewCenterY + (height / 2) / scale;
  
  const startX = Math.floor(minVisibleX / step) * step;
  const endX = Math.ceil(maxVisibleX / step) * step;
  const startY = Math.floor(minVisibleY / step) * step;
  const endY = Math.ceil(maxVisibleY / step) * step;
  
  for (let gx = startX; gx <= endX; gx += step) {
    for (let gy = startY; gy <= endY; gy += step) {
      const c = toCanvas({ x: gx, y: gy });
      // Skip if completely outside viewport bounds
      if (c.x < 0 || c.x > width || c.y < 0 || c.y > height) continue;
      
      ctx.strokeStyle = "rgba(148, 163, 184, 0.15)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(c.x - 3, c.y); ctx.lineTo(c.x + 3, c.y);
      ctx.moveTo(c.x, c.y - 3); ctx.lineTo(c.x, c.y + 3);
      ctx.stroke();
      
      const ftX = Math.round(gx / 12);
      const ftY = Math.round(gy / 12);
      ctx.fillText(`(${ftX},${ftY})`, c.x, c.y - 6);
    }
  }
  ctx.textAlign = "left"; // Reset align
  
  // Draw connecting dashed line to active target
  const targetPos = getSubjectCoord(lastTargetSubject);
  const targetCanvas = toCanvas(targetPos);
  const playerCanvas = toCanvas(playerPos);
  
  ctx.strokeStyle = "rgba(245, 158, 11, 0.15)";
  ctx.lineWidth = 1;
  ctx.setLineDash([4, 4]);
  ctx.beginPath();
  ctx.moveTo(playerCanvas.x, playerCanvas.y);
  ctx.lineTo(targetCanvas.x, targetCanvas.y);
  ctx.stroke();
  ctx.setLineDash([]);
  
  // Draw all subjects
  entitiesToDraw.forEach(e => {
    const coords = getSubjectCoord(e.name);
    const canvasPos = toCanvas(coords);
    const type = (e.entity_type || e.type || "").toLowerCase();
    
    const isFocused = e.name.toLowerCase() === lastTargetSubject.toLowerCase();
    const isHovered = hoveredSubject && e.name.toLowerCase() === hoveredSubject.toLowerCase();
    
    // Choose marker color by type
    let color = "#a855f7"; // purple-500 for locations
    if (e.name.toLowerCase() === "old man") {
      color = "#f59e0b"; // amber-500 for old man
    } else if (type === "character") {
      color = "#f43f5e"; // rose-500
    } else if (type === "object" || type === "item") {
      color = "#06b6d4"; // cyan-500
    }
    
    ctx.beginPath();
    if (isHovered) {
      // Draw outer highlight ring if hovered
      ctx.strokeStyle = "#ffffff";
      ctx.lineWidth = 1.5;
      ctx.arc(canvasPos.x, canvasPos.y, 7, 0, Math.PI * 2);
      ctx.stroke();
      ctx.beginPath();
    }
    
    ctx.shadowColor = color;
    ctx.shadowBlur = isHovered ? 12 : 6;
    ctx.fillStyle = color;
    ctx.arc(canvasPos.x, canvasPos.y, isHovered ? 5.5 : 4, 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0;
    
    // Format text and capitalize name
    const labelText = e.name.split(" ").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
    
    if (isFocused) {
      ctx.fillStyle = "#f59e0b"; // amber-500
      ctx.font = "bold 9px sans-serif";
    } else if (isHovered) {
      ctx.fillStyle = "#f8fafc"; // slate-50
      ctx.font = "bold 9px sans-serif";
    } else {
      ctx.fillStyle = "#94a3b8"; // slate-400
      ctx.font = "9px sans-serif";
    }
    
    ctx.fillText(labelText, canvasPos.x + 7, canvasPos.y + 3);
    
    if (isHovered) {
      const textWidth = ctx.measureText(labelText).width;
      ctx.strokeStyle = ctx.fillStyle;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(canvasPos.x + 7, canvasPos.y + 5);
      ctx.lineTo(canvasPos.x + 7 + textWidth, canvasPos.y + 5);
      ctx.stroke();
    }
  });
  
  // Draw Player (Blue dot with pulse glow)
  ctx.shadowColor = "#3b82f6";
  ctx.shadowBlur = 8;
  ctx.fillStyle = "#3b82f6";
  ctx.beginPath();
  ctx.arc(playerCanvas.x, playerCanvas.y, 5, 0, Math.PI * 2);
  ctx.fill();
  ctx.shadowBlur = 0;
  
  // Label Player
  ctx.fillStyle = "#3b82f6";
  ctx.font = "bold 9px sans-serif";
  ctx.fillText("You", playerCanvas.x - 22, playerCanvas.y + 3);
  
  // Update UI indicators
  const distInches = Math.sqrt((targetPos.x - playerPos.x) ** 2 + (targetPos.y - playerPos.y) ** 2);
  const distFt = (distInches / 12).toFixed(1);
  document.getElementById("mapDistanceLabel").textContent = `To ${lastTargetSubject}: ${distFt} ft`;
  
  document.getElementById("mapPlayerCoords").textContent = `${(playerPos.x / 12).toFixed(1)} ft, ${(playerPos.y / 12).toFixed(1)} ft`;
  
  // Display target coordinates in target label
  const targetLabel = document.querySelector("#mapPanel .absolute.bottom-2.right-2");
  if (targetLabel) {
    targetLabel.innerHTML = `${lastTargetSubject}: <span id="mapManCoords">${(targetPos.x / 12).toFixed(1)} ft, ${(targetPos.y / 12).toFixed(1)} ft</span>`;
  }
}

function updatePlayerLocationFromPayload(payload) {
  const dist = payload["move.distance_inches"];
  if (dist === null || dist === undefined) return;
  
  const dir = (payload["move.direction"] || "").toLowerCase();
  const subjectName = payload["towards.subject"] || "old man";
  const isSelf = subjectName.toLowerCase() === "self" || subjectName.toLowerCase() === "you";
  
  lastTargetSubject = subjectName;
  const targetPos = getSubjectCoord(subjectName);
  
  if (isSelf) {
    if (dir === "forwards" || dir === "north" || dir === "northg") {
      playerPos.y += dist;
    } else if (dir === "back" || dir === "south") {
      playerPos.y -= dist;
    } else if (dir === "east") {
      playerPos.x += dist;
    } else if (dir === "west") {
      playerPos.x -= dist;
    }
  } else {
    if (dir === "north" || dir === "northg") {
      playerPos.y += dist;
    } else if (dir === "south") {
      playerPos.y -= dist;
    } else if (dir === "east") {
      playerPos.x += dist;
    } else if (dir === "west") {
      playerPos.x -= dist;
    } else if (dir === "towards" || dir === "forwards") {
      const dx = targetPos.x - playerPos.x;
      const dy = targetPos.y - playerPos.y;
      const d = Math.sqrt(dx * dx + dy * dy);
      if (d > 0) {
        if (dist >= d) {
          playerPos.x = targetPos.x;
          playerPos.y = targetPos.y;
        } else {
          playerPos.x += dx * (dist / d);
          playerPos.y += dy * (dist / d);
        }
      }
    } else if (dir === "away" || dir === "back") {
      const dx = targetPos.x - playerPos.x;
      const dy = targetPos.y - playerPos.y;
      const d = Math.sqrt(dx * dx + dy * dy);
      if (d > 0) {
        playerPos.x -= dx * (dist / d);
        playerPos.y -= dy * (dist / d);
      } else {
        playerPos.y -= dist;
      }
    }
  }
  
  saveMapPositions();
  drawMap();
}

window.addEventListener("resize", drawMap);

// Setup interactive mouse event listeners for the Tactical Map
(function() {
  const canvas = document.getElementById("mapCanvas");
  if (!canvas) return;
  
  let isDragging = false;
  let startMouse = { x: 0, y: 0 };
  let startPan = { x: 0, y: 0 };
  let draggedDistance = 0;
  
  function getSubjectUnderMouse(clientX, clientY) {
    const rect = canvas.getBoundingClientRect();
    const clickX = clientX - rect.left;
    const clickY = clientY - rect.top;
    
    const params = getMapViewParams();
    if (!params) return null;
    
    const ctx = canvas.getContext("2d");
    ctx.save();
    ctx.font = "9px sans-serif";
    
    let found = null;
    
    for (const s of params.entitiesToDraw) {
      const coords = getSubjectCoord(s.name);
      const canvasPos = params.toCanvas(coords);
      
      // 1. Circle check (radius 15)
      const dist = Math.sqrt((clickX - canvasPos.x) ** 2 + (clickY - canvasPos.y) ** 2);
      if (dist <= 15) {
        found = s.name;
        break;
      }
      
      // 2. Text label check and capitalize name
      const labelText = s.name.split(" ").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
      const textWidth = ctx.measureText(labelText).width;
      const textLeft = canvasPos.x + 7;
      const textRight = textLeft + textWidth;
      const textTop = canvasPos.y - 10;
      const textBottom = canvasPos.y + 6;
      
      if (clickX >= textLeft && clickX <= textRight && clickY >= textTop && clickY <= textBottom) {
        found = s.name;
        break;
      }
    }
    
    ctx.restore();
    return found;
  }
  
  canvas.addEventListener("mousedown", (e) => {
    isDragging = true;
    startMouse = { x: e.clientX, y: e.clientY };
    startPan = { ...mapPan };
    draggedDistance = 0;
    canvas.style.cursor = "grabbing";
  });
  
  canvas.addEventListener("mousemove", (e) => {
    if (isDragging) {
      canvas.style.cursor = "grabbing";
      const dx = e.clientX - startMouse.x;
      const dy = e.clientY - startMouse.y;
      draggedDistance = Math.sqrt(dx * dx + dy * dy);
      
      const params = getMapViewParams();
      if (params && params.scale > 0) {
        const proposedPanX = startPan.x - dx / params.scale;
        const proposedPanY = startPan.y + dy / params.scale;
        
        const centerX = (params.minX + params.maxX) / 2;
        const centerY = (params.minY + params.maxY) / 2;
        
        const viewCenterX = centerX + proposedPanX;
        const viewCenterY = centerY + proposedPanY;
        
        const px = params.width / 2 + (playerPos.x - viewCenterX) * params.scale;
        const py = params.height / 2 - (playerPos.y - viewCenterY) * params.scale;
        
        // Allow drag panning only as long as 'You' (player marker) is inside canvas viewport with 10px padding margin
        if (px >= 10 && px <= params.width - 10 && py >= 10 && py <= params.height - 10) {
          mapPan.x = proposedPanX;
          mapPan.y = proposedPanY;
          drawMap();
        }
      }
    } else {
      const subject = getSubjectUnderMouse(e.clientX, e.clientY);
      if (subject !== hoveredSubject) {
        hoveredSubject = subject;
        drawMap();
      }
      canvas.style.cursor = hoveredSubject ? "pointer" : "default";
    }
  });
  
  const stopDrag = () => { 
    isDragging = false; 
    canvas.style.cursor = hoveredSubject ? "pointer" : "default";
  };
  canvas.addEventListener("mouseup", stopDrag);
  canvas.addEventListener("mouseleave", stopDrag);
  
  // Click on items to set distance target focus
  canvas.addEventListener("click", (e) => {
    if (draggedDistance > 5) return;
    
    if (hoveredSubject) {
      lastTargetSubject = hoveredSubject;
      saveMapPositions();
      drawMap();
    }
  });
  
  // Mouse wheel zoom events: zoom in allowed, zoom out clamped to 20 feet max radius
  canvas.addEventListener("wheel", (e) => {
    e.preventDefault();
    if (e.deltaY < 0) {
      mapViewportRadiusInches = Math.max(36, mapViewportRadiusInches * 0.9); // zoom in (min 3 feet)
    } else {
      mapViewportRadiusInches = Math.min(240, mapViewportRadiusInches * 1.1); // zoom out (max 20 feet radius)
    }
    drawMap();
  });
})();
