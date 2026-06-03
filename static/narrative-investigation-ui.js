// UI panel animations, confirmation dialogs, status overlays, circular timers and queue renderers
let _toastTimeout = null;

function showInvestigationStatus(itemName, entityType, cost) {
  const job = getActiveJob(itemName);
  if (job) {
    document.getElementById('statusItemName').textContent = itemName;
    document.getElementById('investigationStatusDialog').classList.remove('hidden');
  } else {
    showInvestigationToast(`Investigation for "${itemName}" failed — trying again…`);
    setTimeout(() => showInvestigationConfirmation(itemName, entityType, cost), 1200);
  }
}

function closeInvestigationStatusDialog() {
  document.getElementById('investigationStatusDialog').classList.add('hidden');
}

function showInvestigationToast(message) {
  const toast = document.getElementById('investigationToast');
  const msgEl = document.getElementById('investigationToastMsg');
  if (msgEl) msgEl.textContent = message;
  toast.classList.remove('hidden');
  clearTimeout(_toastTimeout);
  _toastTimeout = setTimeout(() => toast.classList.add('hidden'), 3000);
}

function resolveClickContext(btnElement) {
  if (!btnElement) return '';
  const closestBlock = btnElement.closest('.narrative-block, #detailEntityContent') || btnElement.closest('p, div');
  if (!closestBlock) return '';
  
  if (closestBlock.id === 'detailEntityContent') {
    return closestBlock.innerText || '';
  }
  
  const blockText = closestBlock.innerText || '';
  if (typeof conversationHistory === 'undefined' || !conversationHistory || conversationHistory.length === 0) {
    return blockText;
  }
  
  let foundIdx = -1;
  for (let i = conversationHistory.length - 1; i >= 0; i--) {
    const msg = conversationHistory[i];
    if (msg.content) {
      const cleanMsg = msg.content.replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim();
      const cleanBlock = blockText.replace(/\s+/g, ' ').trim();
      if (cleanMsg.indexOf(cleanBlock) !== -1 || cleanBlock.indexOf(cleanMsg) !== -1) {
        foundIdx = i;
        break;
      }
    }
  }
  
  if (foundIdx !== -1) {
    const startIdx = Math.max(0, foundIdx - 2);
    const contextParts = [];
    for (let i = startIdx; i <= foundIdx; i++) {
      const msg = conversationHistory[i];
      const sender = msg.role === 'user' ? 'Player Action' : 'Narrative';
      const cleanContent = msg.content.replace(/<[^>]*>/g, '').trim();
      contextParts.push(`[${sender}]\n${cleanContent}`);
    }
    return contextParts.join('\n\n');
  }
  
  return blockText;
}

function showInvestigationConfirmation(itemName, entityType, cost, btnEl) {
  const existing = currentEntities.find(e => areNamesEquivalent(e.name, itemName));
  if (existing) {
    openInvestigatedEntity(existing.name);
    return;
  }
  
  let contextText = '';
  if (btnEl) {
    contextText = resolveClickContext(btnEl);
  } else {
    const btn = document.querySelector(`.investigate-btn[data-inv-item="${itemName}"]`);
    contextText = resolveClickContext(btn);
  }

  pendingInvestigation = { itemName, entityType, cost, context: contextText };
  document.getElementById("confirmItemName").textContent = itemName;
  document.getElementById("confirmCost").textContent = cost;
  document.getElementById("confirmInvestigationDialog").classList.remove("hidden");
}

function cancelInvestigation() {
  pendingInvestigation = null;
  document.getElementById("confirmInvestigationDialog").classList.add("hidden");
}

async function confirmInvestigationStart() {
  if (!pendingInvestigation) return;
  const { itemName, entityType, cost, context } = pendingInvestigation;
  pendingInvestigation = null;
  document.getElementById("confirmInvestigationDialog").classList.add("hidden");
  await queueInvestigation(itemName, entityType, cost, context);
}

function openInvestigationPanel() {
  cancelPanelClose();
  document.getElementById("investigationPanel").classList.add("panel-open");
}

function closeInvestigationPanel() {
  document.getElementById("investigationPanel").classList.remove("panel-open");
}

function forceCloseInvestigationPanel() {
  cancelPanelClose();
  document.getElementById("investigationPanel").classList.remove("panel-open");
}

function schedulePanelClose() {
  panelCloseTimeout = setTimeout(closeInvestigationPanel, 350);
}

function cancelPanelClose() {
  clearTimeout(panelCloseTimeout);
  panelCloseTimeout = null;
}

function clearCompletedInvestigations() {
  for (const jobId of Object.keys(activeInvestigations)) {
    if (activeInvestigations[jobId].status === 'complete') {
      delete activeInvestigations[jobId];
    }
  }
  renderInvestigationQueue();
}

function renderInvestigationQueue() {
  const queueDiv = document.getElementById("investigationQueue");
  if (!queueDiv) return;
  const jobIds = Object.keys(activeInvestigations);

  const clearBtn = document.getElementById("clearCompletedBtn");
  const hasCompleted = jobIds.some(id => activeInvestigations[id].status === 'complete');
  if (clearBtn) clearBtn.classList.toggle("hidden", !hasCompleted);

  if (jobIds.length === 0) {
    queueDiv.innerHTML = '<p class="text-slate-600 text-sm self-center">No active investigations</p>';
    return;
  }

  let html = '';
  for (const jobId of jobIds) {
    const inv = activeInvestigations[jobId];

    if (inv.status === "queued" || inv.status === "processing") {
      const elapsed = Math.floor((Date.now() - inv.startedAt) / 1000);
      const pacingMax = 60;
      const remaining = Math.max(0, pacingMax - elapsed);
      const circumference = 100.5;
      const dashOffset = circumference * (1 - remaining / pacingMax);

      html += `
        <div class="min-w-[180px] max-w-[180px] flex-none bg-slate-900 border border-amber-900/40 rounded-xl p-3 flex items-center justify-between gap-2">
          <div class="min-w-0 flex-1">
            <p class="text-sm font-medium text-slate-200 truncate" title="${inv.itemName}">${inv.itemName}</p>
            <p class="text-[10px] text-amber-500/80 mt-0.5 truncate tracking-wide font-mono" title="${inv.activeStage || 'Investigating'}">${inv.activeStage || 'Investigating'}</p>
          </div>
          <div class="relative w-10 h-10 flex items-center justify-center flex-none">
            <svg class="w-full h-full transform -rotate-90">
              <circle cx="20" cy="20" r="16" stroke="rgba(180, 83, 9, 0.15)" stroke-width="2.5" fill="transparent" />
              <circle cx="20" cy="20" r="16" stroke="#d97706" stroke-width="2.5" fill="transparent"
                      stroke-dasharray="100.5" stroke-dashoffset="${dashOffset}" stroke-linecap="round" />
            </svg>
            <span class="absolute text-[10px] font-mono font-semibold text-amber-500">${remaining}s</span>
          </div>
        </div>
      `;
    } else if (inv.status === "complete" && inv.result && !inv.reviewed) {
      const entity = inv.result.entity;
      const summary = entity.summary ? entity.summary.substring(0, 90) : '';
      html += `
        <div class="relative min-w-[220px] max-w-[220px] flex-none bg-amber-950/20 border border-amber-700/50 rounded-xl p-3 flex flex-col gap-2">
          <button onclick="dismissCompletedInvestigation('${jobId}')" class="absolute top-2 right-2.5 text-slate-500 hover:text-slate-200 text-sm font-bold leading-none p-1 cursor-pointer select-none" title="Dismiss from queue">×</button>
          <div class="flex items-center gap-1.5 pr-4">
            <svg class="w-3.5 h-3.5 text-amber-400 flex-none" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
            </svg>
            <p class="text-sm font-medium text-amber-200 truncate">${inv.itemName}</p>
          </div>
          ${summary ? `<p class="text-xs text-slate-400 leading-relaxed" style="display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden">${summary}</p>` : ''}
          <div class="flex gap-1.5 mt-auto">
            <button onclick="viewInCompendium('${jobId}', '${entity.entity_id || entity.id}')" class="flex-1 bg-amber-600 hover:bg-amber-500 active:bg-amber-700 text-slate-900 font-semibold py-1 rounded-lg text-xs transition-colors">View Card</button>
            <button onclick="inspectInvestigationStages('${jobId}')" class="bg-slate-800 hover:bg-slate-700 text-amber-500/90 hover:text-amber-400 font-semibold py-1 px-2 rounded-lg text-[10px] transition-colors border border-amber-900/30">Inspect Tiers</button>
          </div>
        </div>
      `;
    }
  }
  queueDiv.innerHTML = html;
}

async function viewInCompendium(jobId, entityId) {
  delete activeInvestigations[jobId];
  renderInvestigationQueue();
  await addToCompendium(entityId);
}

function dismissCompletedInvestigation(jobId) {
  delete activeInvestigations[jobId];
  renderInvestigationQueue();
}

function tickInvestigationTimer() {
  const activeJobs = Object.values(activeInvestigations).some(
    inv => inv.status === "queued" || inv.status === "processing"
  );
  if (!activeJobs) {
    if (timerTickInterval) {
      clearInterval(timerTickInterval);
      timerTickInterval = null;
    }
    return;
  }
  renderInvestigationQueue();
}

function showInsufficientPointsDialog(cost, have) {
  let dialog = document.getElementById('insufficientPointsDialog');
  if (!dialog) {
    dialog = document.createElement('div');
    dialog.id = 'insufficientPointsDialog';
    dialog.className = 'hidden fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50';
    dialog.innerHTML = `
      <div class="bg-slate-900 rounded-xl max-w-sm w-full mx-4 border border-red-900/40 shadow-2xl shadow-red-950/20 transform scale-95 transition-all duration-300">
        <div class="px-6 py-4 border-b border-slate-800 flex items-center gap-2">
          <div class="w-1.5 h-4 bg-red-600 rounded-full flex-none"></div>
          <h3 class="font-semibold text-slate-100 text-sm">Insufficient Points</h3>
        </div>
        <div class="p-6">
          <p class="text-slate-300 text-sm mb-3">You do not have enough investigation points to start this research.</p>
          <div class="bg-slate-950/40 border border-slate-800/80 rounded-lg py-2.5 px-4 flex items-center justify-around text-center mb-3">
            <div>
              <p class="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Cost</p>
              <p id="insufficientCost" class="text-base font-bold text-red-400 font-mono mt-0.5">1</p>
            </div>
            <div class="h-8 w-px bg-slate-800"></div>
            <div>
              <p class="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">You Have</p>
              <p id="insufficientHave" class="text-base font-bold text-slate-400 font-mono mt-0.5">0</p>
            </div>
          </div>
          <p class="text-slate-500 text-[11px] leading-relaxed">
            Pacing timers on active investigations will refund your points upon completion. Review their findings in the top panel once complete!
          </p>
        </div>
        <div class="px-6 py-3.5 border-t border-slate-800 flex justify-end">
          <button onclick="closeInsufficientPointsDialog()" class="bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm px-5 py-2 rounded-lg transition-colors font-medium border border-slate-700/50 hover:border-slate-600 cursor-pointer shadow-sm">
            Close
          </button>
        </div>
      </div>
    `;
    dialog.addEventListener('click', (e) => {
      if (e.target === dialog) {
        closeInsufficientPointsDialog();
      }
    });
    document.body.appendChild(dialog);
  }

  document.getElementById('insufficientCost').textContent = cost;
  document.getElementById('insufficientHave').textContent = have;

  dialog.classList.remove('hidden');
  setTimeout(() => {
    const card = dialog.querySelector('.transform');
    if (card) {
      card.classList.remove('scale-95');
      card.classList.add('scale-100');
    }
  }, 10);
}

function closeInsufficientPointsDialog() {
  const dialog = document.getElementById('insufficientPointsDialog');
  if (dialog) {
    const card = dialog.querySelector('.transform');
    if (card) {
      card.classList.remove('scale-100');
      card.classList.add('scale-95');
    }
    setTimeout(() => {
      dialog.classList.add('hidden');
    }, 150);
  }
}

window.showInsufficientPointsDialog = showInsufficientPointsDialog;
window.closeInsufficientPointsDialog = closeInsufficientPointsDialog;

