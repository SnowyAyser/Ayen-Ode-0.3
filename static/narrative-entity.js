// Entity detail panel, compendium selection, entity link detection

function linkifyEntityRefs(text, selfEntityId) {
  if (!text || !currentEntities.length) return escapeHtml(text);
  const candidates = currentEntities
    .filter(e => (e.entity_id || e.id) !== selfEntityId && e.name && e.name.length >= 2)
    .sort((a, b) => b.name.length - a.name.length);
  if (!candidates.length) return escapeHtml(text);

  const matches = [];
  candidates.forEach(entity => {
    const escaped = entity.name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`\\b${escaped}\\b`, 'gi');
    let m;
    while ((m = regex.exec(text)) !== null) {
      matches.push({ start: m.index, end: m.index + m[0].length, entity, matched: m[0] });
    }
  });
  if (!matches.length) return escapeHtml(text);

  matches.sort((a, b) => a.start - b.start);
  const noOverlap = [];
  let lastEnd = 0;
  for (const m of matches) {
    if (m.start >= lastEnd) { noOverlap.push(m); lastEnd = m.end; }
  }

  let result = '';
  let pos = 0;
  for (const m of noOverlap) {
    result += escapeHtml(text.slice(pos, m.start));
    const ename = m.entity.name.replace(/'/g, "\\'");
    result += `<button onclick="openInvestigatedEntity('${ename}')" class="text-amber-400/80 hover:text-amber-300 underline decoration-dotted underline-offset-2 transition-colors">${escapeHtml(m.matched)}</button>`;
    pos = m.end;
  }
  result += escapeHtml(text.slice(pos));
  return result;
}

async function selectEntity(entityId, pushHistory = true) {
  if (selectedEntityId) {
    const prev = document.getElementById(`card-${selectedEntityId}`);
    if (prev) prev.classList.remove('is-selected');
  }
  if (selectedEntityId === entityId) {
    selectedEntityId = null;
    closeEntityDetail();
    return;
  }
  if (pushHistory && selectedEntityId !== null) detailHistory.push(selectedEntityId);
  selectedEntityId = entityId;
  const card = document.getElementById(`card-${entityId}`);
  if (card) {
    card.classList.add('is-selected');
    card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
  updateBackButton();
  await loadEntityDetail(entityId);
}

async function goBackDetail() {
  if (!detailHistory.length) return;
  const prev = detailHistory.pop();
  await selectEntity(prev, false);
}

function updateBackButton() {
  const btn = document.getElementById('detailBackBtn');
  if (btn) btn.classList.toggle('hidden', detailHistory.length === 0);
}

function _renderEntityDetail(e, stats, entityId, contentDiv) {
  document.getElementById('detailEntityType').textContent = `${e.type || ''} · ${e.status || 'active'}`;

  let html = '';

  if (e.summary) {
    html += `<p class="text-slate-400 leading-relaxed">${linkifyEntityRefs(e.summary, entityId)}</p>`;
  }

  if (Object.keys(stats).length > 0) {
    html += `<div class="space-y-1.5 border-t border-slate-800 pt-2 mt-1">`;
    Object.entries(stats).forEach(([stat, value]) => {
      const barColor = value >= 70 ? 'bg-emerald-500' : value >= 40 ? 'bg-blue-500' : 'bg-red-600';
      html += `
        <div>
          <div class="flex justify-between mb-0.5">
            <span class="capitalize text-slate-400">${stat}</span>
            <span class="text-slate-600">${getNarrativeStatDescription(value)}</span>
          </div>
          <div class="bg-slate-800 rounded-full h-1 overflow-hidden">
            <div class="${barColor} h-full rounded-full" style="width:${value}%"></div>
          </div>
        </div>
      `;
    });
    html += `</div>`;
  }

  if (e.timeline_notes && e.timeline_notes.length > 0) {
    html += `<div class="space-y-1 border-t border-slate-800 pt-2 mt-1">`;
    e.timeline_notes.forEach(n => {
      html += `<div class="flex gap-1.5"><span class="text-slate-600 flex-none">•</span><span class="text-slate-400">${linkifyEntityRefs(n, entityId)}</span></div>`;
    });
    html += `</div>`;
  }

  if (e.open_questions && e.open_questions.length > 0) {
    html += `<div class="space-y-1 border-t border-slate-800 pt-2 mt-1">`;
    e.open_questions.forEach(q => {
      html += `<div class="flex gap-1.5"><span class="text-amber-700 flex-none">?</span><span class="text-slate-500 italic">${linkifyEntityRefs(q, entityId)}</span></div>`;
    });
    html += `</div>`;
  }

  if (e.tags && e.tags.length > 0) {
    html += `<div class="flex flex-wrap gap-1 border-t border-slate-800 pt-2 mt-1">`;
    e.tags.forEach(t => {
      html += `<span class="bg-slate-800 border border-slate-700/50 px-1.5 py-0.5 rounded text-slate-500">${t}</span>`;
    });
    html += `</div>`;
  }

  entityCache[entityId] = html || '<span class="text-slate-600">No details available.</span>';
  contentDiv.innerHTML = entityCache[entityId];
}

async function loadEntityDetail(entityId) {
  const entity = currentEntities.find(e => (e.entity_id || e.id) === entityId);
  if (!entity) return;

  const pane = document.getElementById('entityDetailPane');
  const contentDiv = document.getElementById('detailEntityContent');
  document.getElementById('detailEntityName').textContent = entity.name || 'Unknown';
  document.getElementById('detailEntityType').textContent = (entity.entity_type || entity.type || '') + (entity.status ? ' · ' + entity.status : '');
  contentDiv.innerHTML = '<span class="text-slate-600">Loading…</span>';
  pane.style.height = '270px';

  if (entityCache[entityId]) {
    contentDiv.innerHTML = entityCache[entityId];
    return;
  }

  try {
    const [entityResp, statsResp] = await Promise.allSettled([
      apiCall(`/api/entities/${entityId}?world_id=${currentWorldId}`),
      apiCall(`/api/entities/${entityId}/stats?world_id=${currentWorldId}`),
    ]);

    const entityData = entityResp.status === 'fulfilled' ? entityResp.value : null;
    const statsData = statsResp.status === 'fulfilled' ? statsResp.value : null;

    if (!entityData || !entityData.entity) {
      contentDiv.textContent = 'Could not load entity.';
      return;
    }

    _renderEntityDetail(entityData.entity, statsData?.stats || {}, entityId, contentDiv);

    const completedJobId = Object.keys(activeInvestigations).find(
      id => activeInvestigations[id].result?.entity?.entity_id === entityId
    );
    if (completedJobId) {
      activeInvestigations[completedJobId].reviewed = true;
      renderInvestigationQueue();
    }
  } catch (error) {
    console.error("Error loading entity detail:", error);
    if (contentDiv) contentDiv.textContent = 'Error loading details.';
  }
}

function closeEntityDetail() {
  document.getElementById('entityDetailPane').style.height = '0';
  detailHistory = [];
  updateBackButton();
  if (selectedEntityId) {
    const card = document.getElementById(`card-${selectedEntityId}`);
    if (card) card.classList.remove('is-selected');
    selectedEntityId = null;
  }
}

async function openInvestigatedEntity(itemName) {
  const entity = currentEntities.find(e => e.name.toLowerCase() === itemName.toLowerCase());
  if (!entity) return;
  const entityId = entity.entity_id || entity.id;
  const etype = entity.entity_type || entity.type || 'unknown';

  const typeSectionId = `type-section-${etype}`;
  const typeSection = document.getElementById(typeSectionId);
  if (typeSection && typeSection.classList.contains('hidden')) toggleCompendiumSection(typeSectionId);

  const sgName = getEntitySubgroup(entity, etype);
  if (sgName) {
    const subId = `sub-${etype}-${sgName.replace(/[^a-z0-9]/gi, '-').toLowerCase()}`;
    const subSection = document.getElementById(subId);
    if (subSection && subSection.classList.contains('hidden')) toggleCompendiumSection(subId);
  }

  await selectEntity(entityId);
}

function detectEntityReferences(text, currentEntityName) {
  const references = [];
  for (const entity of currentEntities) {
    if (entity.name === currentEntityName) continue;
    const regex = new RegExp(`\\b${entity.name}\\b`, 'gi');
    if (regex.test(text)) references.push(entity.entity_id);
  }
  return references;
}

async function createEntityLinks(entityId, linkedIds) {
  if (linkedIds.length === 0) return;
  for (const linkedId of linkedIds) {
    try {
      await fetch("/api/entities/link", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${getToken()}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          world_id: currentWorldId,
          entity_id_a: entityId,
          entity_id_b: linkedId,
          relation: "references",
        }),
      });
    } catch (e) {
      console.warn("Could not create link:", e);
    }
  }
}

async function addToCompendium(entityId) {
  const entity = currentEntities.find(e => e.entity_id === entityId);
  if (entity) {
    const referencedIds = detectEntityReferences(
      (entity.summary || '') + ' ' + (entity.timeline_notes || []).join(' '),
      entity.name
    );
    if (referencedIds.length > 0) await createEntityLinks(entityId, referencedIds);
    forceCloseInvestigationPanel();
    await selectEntity(entityId);
  }
}
