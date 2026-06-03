// Narrative Client Module: Compendium & Entity Viewers
// Line limit compliance: Under 250 lines
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
