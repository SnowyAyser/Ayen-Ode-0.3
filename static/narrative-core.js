// State globals shared across narrative client modules
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
let pendingConfirm = false;
let currentTimeLabel = '';

const SETTINGS_KEY = 'ayen_ode_settings';
let historyRenderOffset = 0;
let historyScrollListenerAttached = false;
const HISTORY_PAGE = 100;

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

function getSettings() {
  try { return JSON.parse(localStorage.getItem(SETTINGS_KEY)) || {}; } catch { return {}; }
}

function updateSettings(patch) {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify({ ...getSettings(), ...patch }));
}

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

function _historyKey(worldId) { return `ayen_ode_history_${worldId}`; }

function saveHistoryToStorage() {
  if (currentWorldId) localStorage.setItem(_historyKey(currentWorldId), JSON.stringify(conversationHistory));
}

function loadHistoryFromStorage() {
  try { return JSON.parse(localStorage.getItem(_historyKey(currentWorldId)) || '[]'); } catch { return []; }
}

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

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function capFirst(s) { return s ? s.charAt(0).toUpperCase() + s.slice(1) : s; }
