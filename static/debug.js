// State
let worldId    = null;
let worldName  = '';
let entityMap  = {};
let allKnowledge = [];
let consequenceEvents = [];
let seenEventIds = new Set();
let liveFeed   = [];
let liveNewCount = 0;

let activeTab       = 'entities';
let entitySearchVal = '';
let entityTypeVal   = '';
let showingDetail   = false;

// API wrapper
async function debugApi(url) {
  const token = getToken();
  try {
    const res = await fetch(url, {
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
    });
    if (res.status === 401) { clearToken(); window.location.href = '/'; return null; }
    if (!res.ok) return null;
    return res.json();
  } catch { return null; }
}

// Badge / color helpers
const TYPE_CLS = {
  character: 'bg-purple-950 text-purple-300 border-purple-800/50',
  location:  'bg-teal-950 text-teal-300 border-teal-800/50',
  object:    'bg-orange-950 text-orange-300 border-orange-800/50',
  event:     'bg-amber-950 text-amber-300 border-amber-800/50',
};
const TYPE_DOT = {
  character: 'bg-purple-500',
  location:  'bg-teal-500',
  object:    'bg-orange-500',
  event:     'bg-amber-500',
};

function typeBadge(type) {
  const cls = TYPE_CLS[type] || 'bg-slate-800 text-slate-400 border-slate-700/50';
  return `<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium border ${cls}">${type || '?'}</span>`;
}

const DEGREE_CLS = {
  deeply_knows: 'bg-violet-950 text-violet-300 border-violet-800/50',
  witnessed:    'bg-blue-950 text-blue-300 border-blue-800/50',
  secondhand:   'bg-slate-800 text-slate-300 border-slate-700/50',
  heard_rumor:  'bg-slate-900 text-slate-400 border-slate-800',
  fabricated:   'bg-red-950 text-red-300 border-red-800/50',
  unaware:      'bg-slate-950 text-slate-600 border-slate-800',
};

function degreeBadge(degree) {
  const cls = DEGREE_CLS[degree] || 'bg-slate-800 text-slate-400 border-slate-700/50';
  return `<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium border ${cls}">${(degree || '?').replace(/_/g, ' ')}</span>`;
}

const EFFECT_CLS = {
  created:              'bg-emerald-950 text-emerald-300 border-emerald-800/50',
  destroyed:            'bg-red-950 text-red-300 border-red-800/50',
  moved:                'bg-teal-950 text-teal-300 border-teal-800/50',
  state_changed:        'bg-slate-800 text-slate-300 border-slate-700/50',
  triggered_event:      'bg-amber-950 text-amber-300 border-amber-800/50',
  relationship_changed: 'bg-purple-950 text-purple-300 border-purple-800/50',
  transformed:          'bg-orange-950 text-orange-300 border-orange-800/50',
};

function effectBadge(type) {
  const cls = EFFECT_CLS[type] || 'bg-slate-800 text-slate-400 border-slate-700/50';
  return `<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium border ${cls}">${(type || '?').replace(/_/g, ' ')}</span>`;
}

function eName(id) { return entityMap[id]?.name || (id ? id.slice(0, 12) + '…' : '?'); }
function eType(id) { return entityMap[id]?.entity_type || ''; }

function fmtTime(ts) {
  if (!ts) return '—';
  try { return new Date(ts).toLocaleTimeString([], { hour12: false }); } catch { return ts; }
}

function fmtDateTime(ts) {
  if (!ts) return '—';
  try {
    const d = new Date(ts);
    const mo = d.toLocaleString('default', { month: 'short' });
    const day = String(d.getDate()).padStart(2, '0');
    const t = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
    return `${mo} ${day} ${t}`;
  } catch { return ts; }
}

function empty(msg) {
  return `<div class="text-slate-600 text-sm italic py-10 text-center">${msg}</div>`;
}

function sectionHeader(color, title) {
  return `<div class="flex items-center gap-2 mb-4">
    <div class="w-0.5 h-4 ${color} rounded-full"></div>
    <h3 class="text-xs font-semibold text-slate-300 uppercase tracking-wider">${title}</h3>
  </div>`;
}

// Tab switching
const ALL_TABS = ['entities','containment','knowledge','consequence','live','intake'];

function switchTab(tab) {
  activeTab = tab;
  ALL_TABS.forEach(t => {
    const panel = document.getElementById(`panel-${t}`);
    const btn   = document.getElementById(`tab-btn-${t}`);
    if (t === tab) {
      panel.classList.remove('hidden');
      btn.classList.add('text-amber-200', 'bg-amber-900/25', 'border-b-2', 'border-amber-600');
      btn.classList.remove('text-slate-400');
    } else {
      panel.classList.add('hidden');
      btn.classList.remove('text-amber-200', 'bg-amber-900/25', 'border-b-2', 'border-amber-600');
      btn.classList.add('text-slate-400');
    }
  });
  if (tab === 'live') {
    liveNewCount = 0;
    const badge = document.getElementById('live-count');
    badge.textContent = '0';
    badge.classList.remove('bg-emerald-900', 'text-emerald-400');
    badge.classList.add('bg-slate-800', 'text-slate-500');
    renderLiveFeed();
  }
  if (tab === 'containment') renderContainmentTree();
  if (tab === 'knowledge')   renderKnowledgeTable();
  if (tab === 'consequence') renderConsequenceList();
  if (tab === 'entities' && !showingDetail) renderEntityGrid();
  if (tab === 'intake')      pollIntakePanel();
}

// Metrics
function updateMetrics() {
  const all = Object.values(entityMap);
  document.getElementById('m-entities').textContent    = all.length;
  document.getElementById('m-locations').textContent   = all.filter(e => e.entity_type === 'location').length;
  document.getElementById('m-knowledge').textContent   = allKnowledge.length;
  document.getElementById('m-consequences').textContent = consequenceEvents.length;
}

// Polling
async function fetchActiveWorld() {
  const data = await debugApi('/api/worlds/active');
  if (data?.world) {
    worldId   = data.world.world_id || data.world.id;
    worldName = data.world.name || 'Unnamed World';
    document.getElementById('world-name').textContent = worldName;
  }
}

async function poll() {
  if (!worldId) { await fetchActiveWorld(); if (!worldId) return; }

  const dot = document.getElementById('poll-dot');
  dot.classList.replace('bg-slate-700', 'bg-emerald-500');

  const [entData, knowData, cqData, cevtData, kevtData] = await Promise.all([
    debugApi(`/api/entities?world_id=${worldId}`),
    debugApi(`/api/worlds/${worldId}/knowledge/all`),
    debugApi(`/api/worlds/${worldId}/consequences/events?limit=500`),
    debugApi(`/api/worlds/${worldId}/containment/events?limit=500`),
    debugApi(`/api/worlds/${worldId}/knowledge/events?limit=500`),
  ]);

  if (entData?.entities) {
    entityMap = {};
    for (const e of entData.entities) entityMap[e.entity_id] = e;
  }
  if (knowData?.links)   allKnowledge      = knowData.links;
  if (cqData?.records)   consequenceEvents = cqData.records;

  ingestLiveFeed(cevtData?.events, kevtData?.events, cqData?.records);
  updateMetrics();

  if (activeTab === 'containment') renderContainmentTree();
  if (activeTab === 'knowledge')   renderKnowledgeTable();
  if (activeTab === 'consequence') renderConsequenceList();
  if (activeTab === 'entities' && !showingDetail) renderEntityGrid();
  if (activeTab === 'intake')      pollIntakePanel();

  setTimeout(() => dot.classList.replace('bg-emerald-500', 'bg-slate-700'), 250);
}

// Live feed ingestion
function ingestLiveFeed(cevts, kevts, cqevts) {
  const newItems = [];

  for (const e of (cevts || [])) {
    const key = `c:${e.event_id}`;
    if (seenEventIds.has(key)) continue;
    seenEventIds.add(key);
    const entName  = eName(e.entity_id);
    const fromName = e.from_container_id ? eName(e.from_container_id) : 'root';
    const toName   = e.to_container_id   ? eName(e.to_container_id)   : 'root';
    newItems.push({
      key, dot: 'bg-teal-400', ts: e.created_at,
      html: `<span class="text-teal-400">[move]</span> <span class="text-slate-200">${entName}</span> <span class="text-slate-600">${fromName} → ${toName}</span>`,
    });
  }

  for (const e of (kevts || [])) {
    const key = `k:${e.event_id}`;
    if (seenEventIds.has(key)) continue;
    seenEventIds.add(key);
    const knower  = eName(e.entity_id);
    const subject = eName(e.knows_about_id);
    const evType  = (e.event_type || 'learn').replace(/_/g, ' ');
    const dot     = e.event_type === 'forget' ? 'bg-slate-500' : 'bg-purple-400';
    newItems.push({
      key, dot, ts: e.created_at,
      html: `<span class="text-purple-400">[know]</span> <span class="text-slate-200">${knower}</span> <span class="text-slate-600">${evType}</span> <span class="text-slate-300">${subject}</span>${e.degree ? ` <span class="text-slate-600">@ ${e.degree.replace(/_/g,' ')}</span>` : ''}`,
    });
  }

  for (const e of (cqevts || [])) {
    const key = `q:${e.consequence_id || e.id}`;
    if (seenEventIds.has(key)) continue;
    seenEventIds.add(key);
    const cause  = eName(e.cause_id);
    const target = eName(e.target_id);
    const et     = e.effect_type || '';
    const dot    = et === 'created' ? 'bg-emerald-400' : et === 'destroyed' ? 'bg-red-400' : 'bg-amber-400';
    newItems.push({
      key, dot, ts: e.created_at,
      html: `<span class="text-amber-400">[cq]</span> <span class="text-slate-200">${cause}</span> <span class="text-slate-600">→ ${et.replace(/_/g,' ')} →</span> <span class="text-slate-300">${target}</span>${e.detail ? ` <span class="text-slate-600">${e.detail}</span>` : ''}`,
    });
  }

  if (newItems.length === 0) return;

  newItems.sort((a, b) => new Date(b.ts) - new Date(a.ts));
  liveFeed = [...newItems, ...liveFeed].slice(0, 200);

  if (activeTab === 'live') {
    renderLiveFeed();
  } else {
    liveNewCount += newItems.length;
    const badge = document.getElementById('live-count');
    badge.textContent = liveNewCount;
    badge.classList.remove('bg-slate-800', 'text-slate-500');
    badge.classList.add('bg-emerald-900', 'text-emerald-400');
  }
}

// Live feed renderer
function renderLiveFeed() {
  if (liveFeed.length === 0) {
    document.getElementById('live-feed').innerHTML = empty('Waiting for events…');
    return;
  }
  document.getElementById('live-feed').innerHTML = liveFeed.map(item => `
    <div class="flex items-start gap-3 py-0.5 px-2 rounded hover:bg-slate-900/50 transition-colors">
      <div class="w-1.5 h-1.5 rounded-full ${item.dot} mt-1 shrink-0"></div>
      <span class="text-slate-600 shrink-0 w-16 text-right">${fmtTime(item.ts)}</span>
      <span class="text-slate-300 leading-relaxed">${item.html}</span>
    </div>`).join('');
}

// Init
async function init() {
  checkAuth();
  switchTab('entities');
  await fetchActiveWorld();
  await poll();
  setInterval(poll, 2000);
}

document.addEventListener('DOMContentLoaded', init);
