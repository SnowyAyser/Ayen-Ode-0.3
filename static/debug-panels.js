// Panel renderers: entity inspector, containment tree, knowledge table, consequence list

// Entity inspector
function onEntitySearch() {
  entitySearchVal = document.getElementById('entity-search').value;
  renderEntityGrid();
}

function onEntityTypeChange() {
  entityTypeVal = document.getElementById('entity-type-filter').value;
  renderEntityGrid();
}

function renderEntityGrid() {
  const search = entitySearchVal.toLowerCase();
  let entities = Object.values(entityMap).filter(e => {
    if (entityTypeVal && e.entity_type !== entityTypeVal) return false;
    if (search && !e.name.toLowerCase().includes(search)) return false;
    return true;
  });
  entities.sort((a, b) => a.name.localeCompare(b.name));

  const grid = document.getElementById('entity-grid');
  if (entities.length === 0) {
    grid.innerHTML = empty('No entities match.');
    return;
  }

  grid.innerHTML = `<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
    ${entities.map(entityCard).join('')}
  </div>`;
}

function entityCard(e) {
  const containerName = e.container_id ? eName(e.container_id) : '';
  return `<div onclick="openEntityDetail('${e.entity_id}')"
    class="bg-slate-900 border border-slate-800 rounded-lg p-3 cursor-pointer hover:border-slate-600 hover:bg-slate-800/50 transition-all group">
    <div class="mb-2">
      <span class="text-sm font-medium text-slate-100 group-hover:text-white leading-snug">${e.name}</span>
    </div>
    <div class="flex flex-wrap gap-1.5 items-center">
      ${typeBadge(e.entity_type)}
      ${containerName ? `<span class="text-[10px] text-slate-600 truncate">in ${containerName}</span>` : ''}
    </div>
  </div>`;
}

async function openEntityDetail(entityId) {
  showingDetail = true;
  document.getElementById('entity-grid').classList.add('hidden');
  const detail = document.getElementById('entity-detail');
  detail.classList.remove('hidden');
  detail.innerHTML = `<div class="text-slate-500 text-sm py-10 text-center">Loading…</div>`;

  const [chainData, contentsData, knowledgeData, historyData] = await Promise.all([
    debugApi(`/api/worlds/${worldId}/entities/${entityId}/container-chain`),
    debugApi(`/api/worlds/${worldId}/entities/${entityId}/contents`),
    debugApi(`/api/worlds/${worldId}/entities/${entityId}/knowledge`),
    debugApi(`/api/worlds/${worldId}/entities/${entityId}/history`),
  ]);

  renderEntityDetail(entityId, chainData, contentsData, knowledgeData, historyData);
}

function closeEntityDetail() {
  showingDetail = false;
  document.getElementById('entity-grid').classList.remove('hidden');
  document.getElementById('entity-detail').classList.add('hidden');
  renderEntityGrid();
}

function renderEntityDetail(entityId, chainData, contentsData, knowledgeData, historyData) {
  const entity   = entityMap[entityId] || {};
  const chain    = [...(chainData?.chain || [])].reverse();
  const contents = contentsData?.contents || [];
  const knowledge = knowledgeData?.knowledge || [];
  const history  = historyData?.history || [];

  let breadHtml = '';
  if (chain.length > 0) {
    breadHtml = chain.map((e, i) =>
      `${i > 0 ? '<span class="text-slate-700 mx-1.5">›</span>' : ''}` +
      `<span class="${i === chain.length - 1 ? 'text-white font-medium' : 'text-slate-400'}">${e.name}</span>`
    ).join('');
  } else {
    breadHtml = `<span class="text-slate-500 italic text-sm">root level</span>`;
  }

  const contentsHtml = contents.length === 0
    ? `<p class="text-slate-600 text-sm italic">Nothing inside.</p>`
    : `<div class="flex flex-wrap gap-2">${contents.map(c =>
        `<div class="flex items-center gap-1.5 bg-slate-800 border border-slate-700/50 rounded-md px-2.5 py-1.5">
          ${typeBadge(c.entity_type)}
          <span class="text-sm text-slate-200">${c.name}</span>
        </div>`).join('')}</div>`;

  const knowledgeHtml = knowledge.length === 0
    ? `<p class="text-slate-600 text-sm italic">No knowledge links.</p>`
    : `<div class="space-y-1">${knowledge.map(k => {
        const tgt = k.entity || {};
        return `<div class="flex items-center gap-2 py-1.5 border-b border-slate-800/40 last:border-0">
          ${degreeBadge(k.degree)}
          ${typeBadge(tgt.entity_type)}
          <span class="text-sm text-slate-200">${tgt.name || k.knows_about_id}</span>
        </div>`;
      }).join('')}</div>`;

  const historyHtml = history.length === 0
    ? `<p class="text-slate-600 text-sm italic">No consequence history.</p>`
    : `<div class="space-y-1.5">${history.map(h =>
        `<div class="flex flex-wrap items-start gap-3 py-1.5 border-b border-slate-800/40 last:border-0">
          <span class="text-[10px] text-slate-600 font-mono mt-0.5 shrink-0 w-28">${fmtDateTime(h.created_at)}</span>
          <div class="flex flex-wrap items-center gap-1.5">
            ${effectBadge(h.effect_type)}
            <span class="text-xs text-slate-500">cause: <span class="text-slate-300">${eName(h.cause_id)}</span></span>
            <span class="text-xs text-slate-500">target: <span class="text-slate-300">${eName(h.target_id)}</span></span>
            ${h.detail ? `<span class="text-xs text-slate-600 italic">${h.detail}</span>` : ''}
          </div>
        </div>`).join('')}</div>`;

  document.getElementById('entity-detail').innerHTML = `
    <div>
      <button onclick="closeEntityDetail()"
        class="flex items-center gap-2 text-sm text-slate-400 hover:text-slate-200 transition-colors mb-5">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
        </svg>
        Back to results
      </button>

      <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 mb-5">
        <div class="flex items-start gap-4 mb-3">
          <div>
            <h2 class="text-xl font-bold text-white mb-1.5">${entity.name || 'Unknown'}</h2>
            <div class="flex items-center gap-2">
              ${typeBadge(entity.entity_type)}
              <span class="text-[10px] text-slate-600 font-mono">${entityId}</span>
            </div>
          </div>
        </div>
        ${entity.summary ? `<p class="text-sm text-slate-400 mt-2 leading-relaxed">${entity.summary}</p>` : ''}
        <div class="mt-4 pt-4 border-t border-slate-800">
          <div class="text-[10px] uppercase tracking-widest text-slate-600 mb-2">Container Chain</div>
          <div class="flex items-center flex-wrap gap-0 text-sm">${breadHtml}</div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-5">
          ${sectionHeader('bg-teal-600', `Contains (${contents.length})`)}
          ${contentsHtml}
        </div>
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-5">
          ${sectionHeader('bg-purple-600', `Knowledge (${knowledge.length})`)}
          ${knowledgeHtml}
        </div>
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 lg:col-span-2">
          ${sectionHeader('bg-amber-600', `Consequence History (${history.length})`)}
          ${historyHtml}
        </div>
      </div>
    </div>`;
}

// Containment tree

let _treeChildren = {};

function _renderContainmentNode(id, depth) {
  const e = entityMap[id];
  if (!e) return '';
  const childIds = (_treeChildren[id] || []).sort((a, b) =>
    (entityMap[a]?.name || '').localeCompare(entityMap[b]?.name || ''));
  const indent  = depth * 20;
  const dotCls  = TYPE_DOT[e.entity_type] || 'bg-slate-500';
  const typeCls = TYPE_CLS[e.entity_type]  || 'bg-slate-800 text-slate-400 border-slate-700/50';
  let html = `<div class="flex items-center gap-2 py-0.5 hover:bg-slate-900/60 rounded px-1 transition-colors"
    style="padding-left:${8 + indent}px">`;
  if (depth > 0) html += `<div class="w-4 h-px bg-slate-800 shrink-0"></div>`;
  html += `<div class="w-1.5 h-1.5 rounded-full ${dotCls} shrink-0"></div>`;
  html += `<span class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium border ${typeCls} shrink-0">${e.entity_type}</span>`;
  html += `<span class="text-sm text-slate-200">${e.name}</span>`;
  if (childIds.length > 0) html += `<span class="text-[10px] text-slate-600 ml-auto pr-2 shrink-0">${childIds.length}</span>`;
  html += `</div>`;
  for (const cid of childIds) html += _renderContainmentNode(cid, depth + 1);
  return html;
}

function renderContainmentTree() {
  const entities = Object.values(entityMap);
  if (entities.length === 0) {
    document.getElementById('containment-tree').innerHTML = empty('No entities in the active world.');
    return;
  }

  _treeChildren = {};
  const roots = [];
  for (const e of entities) {
    if (!e.container_id) {
      roots.push(e.entity_id);
    } else {
      (_treeChildren[e.container_id] = _treeChildren[e.container_id] || []).push(e.entity_id);
    }
  }
  roots.sort((a, b) => (entityMap[a]?.name || '').localeCompare(entityMap[b]?.name || ''));

  const html = roots.map(r => _renderContainmentNode(r, 0)).join('');
  document.getElementById('containment-tree').innerHTML =
    `<div class="bg-slate-900 border border-slate-800 rounded-xl p-4">${html || empty('All entities are at root level.')}</div>`;
}

// Knowledge table
function renderKnowledgeTable() {
  const search = (document.getElementById('knowledge-search')?.value || '').toLowerCase();
  const degree = document.getElementById('knowledge-degree')?.value || '';

  const links = allKnowledge.filter(l => {
    if (degree && l.degree !== degree) return false;
    if (search) {
      const a = (l.knower_name || '').toLowerCase();
      const b = (l.target_name || '').toLowerCase();
      if (!a.includes(search) && !b.includes(search)) return false;
    }
    return true;
  });

  if (links.length === 0) {
    document.getElementById('knowledge-table').innerHTML = empty('No knowledge links match the filters.');
    return;
  }

  document.getElementById('knowledge-table').innerHTML = `
    <div class="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
      <div class="px-4 py-2.5 border-b border-slate-800 text-[10px] uppercase tracking-widest text-slate-500">
        ${links.length} link${links.length !== 1 ? 's' : ''}
      </div>
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-slate-800 text-left">
            <th class="px-4 py-2.5 text-[10px] uppercase tracking-widest text-slate-500 font-medium">Knower</th>
            <th class="px-4 py-2.5 text-[10px] uppercase tracking-widest text-slate-500 font-medium">Knows About</th>
            <th class="px-4 py-2.5 text-[10px] uppercase tracking-widest text-slate-500 font-medium">Degree</th>
            <th class="px-4 py-2.5 text-[10px] uppercase tracking-widest text-slate-500 font-medium hidden md:table-cell">Updated</th>
          </tr>
        </thead>
        <tbody>
          ${links.map(l => `
          <tr class="border-b border-slate-800/50 last:border-0 hover:bg-slate-800/30 transition-colors">
            <td class="px-4 py-2.5">
              <div class="flex items-center gap-2">
                ${typeBadge(l.knower_type)}
                <span class="text-slate-200">${l.knower_name}</span>
              </div>
            </td>
            <td class="px-4 py-2.5">
              <div class="flex items-center gap-2">
                ${typeBadge(l.target_type)}
                <span class="text-slate-200">${l.target_name}</span>
              </div>
            </td>
            <td class="px-4 py-2.5">${degreeBadge(l.degree)}</td>
            <td class="px-4 py-2.5 text-[11px] text-slate-600 font-mono hidden md:table-cell">${fmtDateTime(l.updated_at)}</td>
          </tr>`).join('')}
        </tbody>
      </table>
    </div>`;
}

// Consequence list
function renderConsequenceList() {
  if (consequenceEvents.length === 0) {
    document.getElementById('consequence-list').innerHTML = empty('No consequences recorded.');
    return;
  }

  document.getElementById('consequence-list').innerHTML = `
    <div class="space-y-1.5">
      ${consequenceEvents.map(e => {
        const causeType  = eType(e.cause_id);
        const targetType = eType(e.target_id);
        return `
        <div class="bg-slate-900 border border-slate-800 rounded-lg px-4 py-3 flex flex-wrap items-center gap-2.5 hover:border-slate-700/70 transition-colors">
          <span class="text-[10px] font-mono text-slate-600 shrink-0 w-24">${fmtDateTime(e.created_at)}</span>
          <div class="flex items-center gap-1.5 shrink-0">
            ${typeBadge(causeType)}
            <span class="text-sm text-slate-100">${eName(e.cause_id)}</span>
          </div>
          <svg class="w-3 h-3 text-slate-700 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/>
          </svg>
          ${effectBadge(e.effect_type)}
          <svg class="w-3 h-3 text-slate-700 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/>
          </svg>
          <div class="flex items-center gap-1.5 shrink-0">
            ${typeBadge(targetType)}
            <span class="text-sm text-slate-100">${eName(e.target_id)}</span>
          </div>
          ${e.detail ? `<span class="text-xs text-slate-600 italic ml-1 truncate max-w-xs">${e.detail}</span>` : ''}
        </div>`;
      }).join('')}
    </div>`;
}
