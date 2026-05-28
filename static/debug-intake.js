// State
let intakeLogsList = [];
let activeDebtsList = [];
let historyDebtsList = [];
let expandedLogs = new Set(); // tracks log_ids that are expanded

// Fetch active debts and intake logs from API
async function pollIntakePanel() {
  if (!worldId) return;

  // Populate manual assertion dropdown lists from our live entityMap
  populateDropdowns();

  const [debtsRes, logsRes] = await Promise.all([
    debugApi(`/api/worlds/${worldId}/arch/debts`),
    debugApi(`/api/worlds/${worldId}/arch/intake-logs?limit=25`)
  ]);

  if (debtsRes?.success) {
    activeDebtsList = debtsRes.active || [];
    historyDebtsList = debtsRes.history || [];
    renderDebts();
  }

  if (logsRes?.success) {
    intakeLogsList = logsRes.logs || [];
    renderIntakeLogs();
  }
}

// Populate debtor & creditor selection dropdowns dynamically
function populateDropdowns() {
  const debtorSel = document.getElementById('debt-debtor');
  const creditorSel = document.getElementById('debt-creditor');
  if (!debtorSel || !creditorSel) return;

  const entities = Object.values(entityMap);
  if (entities.length === 0) return;

  // Only refresh if selection size matches current options (prevents wiping user focus)
  const currentCount = debtorSel.options.length;
  const characterCount = entities.filter(e => e.entity_type === 'character').length;
  if (currentCount > 1 && currentCount - 1 === characterCount) return;

  let debtorHtml = '<option value="">-- Select Debtor --</option>';
  let creditorHtml = '<option value="">-- Select Creditor --</option>';

  entities.sort((a, b) => a.name.localeCompare(b.name)).forEach(e => {
    // Debtor is typically a Character
    if (e.entity_type === 'character') {
      debtorHtml += `<option value="${e.entity_id}">${e.name} (${e.entity_type})</option>`;
    }
    // Creditor can be Character, Faction, or Location
    if (['character', 'faction', 'location'].includes(e.entity_type)) {
      creditorHtml += `<option value="${e.entity_id}">${e.name} (${e.entity_type})</option>`;
    }
  });

  debtorSel.innerHTML = debtorHtml;
  creditorSel.innerHTML = creditorHtml;
}

// Assert a new custom debt manually (override)
async function assertCustomDebt(event) {
  event.preventDefault();
  if (!worldId) return;

  const debtor_id = document.getElementById('debt-debtor').value;
  const creditor_id = document.getElementById('debt-creditor').value;
  const resource_type = document.getElementById('debt-resource').value;
  const quantity = document.getElementById('debt-quantity').value;
  const detail = document.getElementById('debt-detail').value;
  const evidence = document.getElementById('debt-evidence').value || 'Manual developer override assertion';

  try {
    const token = getToken();
    const res = await fetch(`/api/worlds/${worldId}/arch/debts`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ debtor_id, creditor_id, resource_type, quantity, detail, evidence })
    });
    const data = await res.json();
    if (data.success) {
      document.getElementById('debt-form').reset();
      pollIntakePanel();
    } else {
      alert(`Assertion failed: ${data.error}`);
    }
  } catch (err) {
    alert(`Assertion failed: ${err}`);
  }
}

// Resolve or Default an active debt obligation
async function resolveDebt(debtId, status) {
  if (!worldId) return;
  const reason = prompt(`Enter resolution summary for marking this debt as ${status}:`);
  if (reason === null) return; // cancelled

  try {
    const token = getToken();
    const res = await fetch(`/api/worlds/${worldId}/arch/debts/${debtId}/status`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ status, detail: reason })
    });
    const data = await res.json();
    if (data.success) {
      pollIntakePanel();
    } else {
      alert(`Resolution failed: ${data.error}`);
    }
  } catch (err) {
    alert(`Resolution failed: ${err}`);
  }
}

// Render active and historical debts list
function renderDebts() {
  const activeContainer = document.getElementById('active-debts-list');
  const historyContainer = document.getElementById('history-debts-list');
  if (!activeContainer || !historyContainer) return;

  if (activeDebtsList.length === 0) {
    activeContainer.innerHTML = empty('No active debt obligations.');
  } else {
    activeContainer.innerHTML = activeDebtsList.map(d => `
      <div class="bg-slate-900 border border-teal-950/60 hover:border-teal-900 rounded-lg p-4 shadow-sm transition-all">
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center gap-1.5">
            <span class="text-xs font-bold text-slate-100">${d.debtor_name}</span>
            <span class="text-[10px] uppercase text-slate-600 tracking-wide font-semibold">owes</span>
            <span class="text-xs font-bold text-slate-100">${d.creditor_name}</span>
          </div>
          <span class="text-[10px] px-2 py-0.5 rounded-full font-bold bg-teal-950 text-teal-400 border border-teal-900">
            ${d.quantity} ${d.resource_type}
          </span>
        </div>
        <div class="text-xs text-slate-400 leading-normal mb-2">
          <span class="text-slate-600 font-semibold">Context:</span> ${d.detail || 'None provided'}
        </div>
        ${d.evidence ? `
          <div class="bg-slate-950/50 border-l border-slate-800 p-2 text-[11px] italic text-slate-500 rounded-r mb-3 font-serif">
            "${d.evidence}"
          </div>
        ` : ''}
        <div class="flex items-center gap-2">
          <button onclick="resolveDebt('${d.debt_id}', 'satisfied')" class="flex-1 bg-emerald-950/60 hover:bg-emerald-950 text-emerald-400 border border-emerald-900 hover:border-emerald-700 rounded py-1 text-[11px] font-semibold transition-colors">
            Satisfy Debt
          </button>
          <button onclick="resolveDebt('${d.debt_id}', 'defaulted')" class="flex-1 bg-red-950/60 hover:bg-red-950 text-red-400 border border-red-900 hover:border-red-700 rounded py-1 text-[11px] font-semibold transition-colors">
            Default Debt
          </button>
        </div>
      </div>
    `).join('');
  }

  if (historyDebtsList.length === 0) {
    historyContainer.innerHTML = empty('No resolved historical debts.');
  } else {
    historyContainer.innerHTML = historyDebtsList.map(d => `
      <div class="bg-slate-950 border border-slate-900 rounded-lg p-3">
        <div class="flex items-center justify-between mb-1 opacity-70">
          <div class="flex items-center gap-1">
            <span class="text-xs font-medium text-slate-300">${d.debtor_name}</span>
            <span class="text-[9px] uppercase text-slate-700 font-bold">owed</span>
            <span class="text-xs font-medium text-slate-300">${d.creditor_name}</span>
          </div>
          <span class="text-[9px] px-1.5 py-0.5 rounded bg-slate-900 text-slate-500">
            ${d.quantity} ${d.resource_type}
          </span>
        </div>
        <div class="text-[11px] text-slate-500">
          <span class="text-[10px] uppercase text-slate-600 font-bold tracking-wide">${d.status}</span>: ${d.detail}
        </div>
      </div>
    `).join('');
  }
}

// Toggle expansion of an individual log card
function toggleLog(logId) {
  if (expandedLogs.has(logId)) {
    expandedLogs.delete(logId);
  } else {
    expandedLogs.add(logId);
  }
  renderIntakeLogs();
}

// Render post-narration state extractor logs
function renderIntakeLogs() {
  const container = document.getElementById('intake-logs-list');
  if (!container) return;

  if (intakeLogsList.length === 0) {
    container.innerHTML = empty('No post-narration logs recorded yet.');
    return;
  }

  container.innerHTML = intakeLogsList.map(log => {
    const isExpanded = expandedLogs.has(log.log_id);
    const timeStr = fmtTime(log.created_at);
    
    // Tools overview badges
    const totalCount = log.tools_attempted.length;
    const successCount = log.tools_executed.filter(t => t.status === 'success').length;
    const errorCount = log.tools_executed.filter(t => t.status === 'error').length;
    
    let badgeHtml = '';
    if (totalCount > 0) {
      badgeHtml += `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-400 border border-slate-700">${totalCount} tools</span>`;
    }
    if (successCount > 0) {
      badgeHtml += `<span class="ml-1.5 px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-900">✅ ${successCount} ok</span>`;
    }
    if (errorCount > 0) {
      badgeHtml += `<span class="ml-1.5 px-2 py-0.5 rounded text-[10px] font-bold bg-red-950 text-red-400 border border-red-900">⚠️ ${errorCount} err</span>`;
    }

    return `
      <div class="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden transition-all duration-200">
        
        <!-- Log Header (Click to toggle) -->
        <div onclick="toggleLog('${log.log_id}')" class="flex items-center justify-between p-4 cursor-pointer hover:bg-slate-800/40 select-none">
          <div class="flex items-center gap-3">
            <span class="text-slate-500 font-mono text-xs w-16">${timeStr}</span>
            <span class="text-amber-400/90 font-semibold text-xs tracking-wide">${log.game_time_label}</span>
          </div>
          <div class="flex items-center gap-2">
            ${badgeHtml}
            <svg class="w-4 h-4 text-slate-500 transform transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>

        <!-- Log Body -->
        ${isExpanded ? `
          <div class="border-t border-slate-800/80 p-4 space-y-4 bg-slate-950/20">
            
            <!-- Analyzed Narration -->
            <div>
              <div class="text-[10px] text-slate-500 uppercase tracking-widest font-bold mb-1">Analyzed Narration</div>
              <div class="bg-slate-950/60 rounded p-3 text-xs text-slate-300 leading-relaxed border border-slate-900 max-h-40 overflow-y-auto select-text font-serif">
                ${log.narrative_text}
              </div>
            </div>

            <!-- Haiku Analysis Thought Process -->
            <div>
              <div class="text-[10px] text-slate-500 uppercase tracking-widest font-bold mb-1">Chain-of-Thought Analysis</div>
              <div class="border-l-2 border-amber-600 bg-slate-950/40 p-3 italic text-slate-400 text-xs rounded-r">
                ${log.thought_process}
              </div>
            </div>

            <!-- Tool Execution Reports -->
            <div>
              <div class="text-[10px] text-slate-500 uppercase tracking-widest font-bold mb-2">Extraction Actions & DB Operations</div>
              <div class="space-y-2">
                ${log.tools_executed.length === 0 ? `
                  <div class="text-xs text-slate-600 italic">No DB actions extracted from this narration turn.</div>
                ` : log.tools_executed.map(t => {
                  const isSuccess = t.status === 'success';
                  const indicatorColor = isSuccess ? 'bg-emerald-500' : 'bg-red-500';
                  
                  return `
                    <div class="bg-slate-950/80 rounded p-2.5 border border-slate-900 flex items-start gap-3">
                      <div class="w-1.5 h-1.5 rounded-full ${indicatorColor} mt-1.5 shrink-0"></div>
                      <div class="flex-1 min-w-0">
                        <div class="flex items-center justify-between mb-1">
                          <span class="font-bold text-slate-200 text-xs">${t.name}</span>
                          <span class="text-[10px] px-1.5 py-0.5 rounded font-mono ${isSuccess ? 'bg-emerald-950 text-emerald-400' : 'bg-red-950 text-red-400'}">
                            ${t.status}
                          </span>
                        </div>
                        <div class="text-[11px] text-slate-500 mb-1 leading-normal">
                          <span class="text-slate-600 font-semibold font-mono">args:</span> ${JSON.stringify(t.input)}
                        </div>
                        ${isSuccess ? `
                          <div class="text-[11px] text-slate-400 font-mono">
                            <span class="text-slate-600 font-semibold">db_result:</span> ${JSON.stringify(t.result)}
                          </div>
                        ` : `
                          <div class="text-[11px] text-red-400/90 font-mono">
                            <span class="text-red-900 font-semibold">error:</span> ${t.error}
                          </div>
                        `}
                      </div>
                    </div>
                  `;
                }).join('')}
              </div>
            </div>

          </div>
        ` : ''}

      </div>
    `;
  }).join('');
}
