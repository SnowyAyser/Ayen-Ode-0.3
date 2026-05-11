// Investigation system: panel, polling, queue, timer, points

function getActiveJob(itemName) {
  const lower = itemName.toLowerCase();
  return Object.values(activeInvestigations).find(
    inv => (inv.status === 'queued' || inv.status === 'processing') && inv.itemName.toLowerCase() === lower
  ) || null;
}

function isItemInvestigated(itemName) {
  const lower = itemName.toLowerCase();
  if (Object.values(activeInvestigations).some(inv => inv.status === 'complete' && inv.itemName.toLowerCase() === lower)) return true;
  return currentEntities.some(e => (e.name || '').toLowerCase() === lower);
}

function investigateBtnHtml(itemName, entityType, cost, displayText) {
  const escaped = itemName.replace(/'/g, "\\'");
  return `<button class="investigate-btn text-amber-400 underline decoration-dotted underline-offset-2 hover:text-amber-200 hover:bg-amber-950/50 px-1 py-0.5 rounded transition-all text-[inherit] leading-[inherit]" data-inv-item="${itemName}" data-inv-type="${entityType}" data-inv-cost="${cost}" onclick="showInvestigationConfirmation('${escaped}', '${entityType}', ${cost});">${displayText}</button>`;
}

function investigatingBtnHtml(itemName, entityType, cost, displayText) {
  const escaped = itemName.replace(/'/g, "\\'");
  const job = getActiveJob(itemName);
  const jobId = job ? job.jobId : '';
  return `<button class="investigate-btn text-emerald-400 underline decoration-dotted underline-offset-2 hover:text-emerald-200 hover:bg-emerald-950/50 px-1 py-0.5 rounded transition-all text-[inherit] leading-[inherit]" data-inv-item="${itemName}" data-inv-type="${entityType}" data-inv-cost="${cost}" data-investigating="true" data-job-id="${jobId}" onclick="showInvestigationStatus('${escaped}', '${entityType}', ${cost});">${displayText}</button>`;
}

function _htmlToElement(html) {
  const tmp = document.createElement('div');
  tmp.innerHTML = html;
  return tmp.firstElementChild;
}

function refreshNarrativeLinks() {
  // Support both new buttons (data-inv-item) and old buttons (onclick attr)
  // querySelectorAll returns a static snapshot so replaceWith is safe inside forEach
  document.querySelectorAll('.investigate-btn').forEach(el => {
    let itemName = el.getAttribute('data-inv-item');
    let entityType = el.getAttribute('data-inv-type') || 'object';
    let cost = parseInt(el.getAttribute('data-inv-cost') || '1');

    // Fallback: parse onclick for buttons rendered before data attributes were added
    if (!itemName) {
      const onclick = el.getAttribute('onclick') || '';
      const nameMatch = onclick.match(/['"]([^'"]+)['"]/);
      if (!nameMatch) return;
      itemName = nameMatch[1];
      const typeMatch = onclick.match(/,\s*'([^']+)'/);
      if (typeMatch) entityType = typeMatch[1];
      const costMatch = onclick.match(/,\s*(\d+)\s*\)/);
      if (costMatch) cost = parseInt(costMatch[1]);
    }

    const displayText = el.textContent;

    if (isItemInvestigated(itemName)) {
      const span = document.createElement('span');
      span.className = 'text-slate-300';
      span.textContent = displayText;
      el.replaceWith(span);
    } else if (getActiveJob(itemName)) {
      el.replaceWith(_htmlToElement(investigatingBtnHtml(itemName, entityType, cost, displayText)));
    } else {
      el.replaceWith(_htmlToElement(investigateBtnHtml(itemName, entityType, cost, displayText)));
    }
  });
}

function parseInvestigateText(text) {
  const regex = /<investigate\s+([^>]*?)>([^<]*?)<\/investigate>/g;
  let match;
  let lastIndex = 0;
  let processedText = '';

  while ((match = regex.exec(text)) !== null) {
    const attrs = match[1];
    const displayText = match[2];

    let itemName = '';
    let cost = 1;
    let entityType = 'object';

    const itemMatch = attrs.match(/(?:item|npc|location|faction|event)='([^']+)'/);
    const costMatch = attrs.match(/cost='(\d+)'/);

    if (itemMatch) {
      itemName = itemMatch[1];
      if (attrs.includes("npc='")) entityType = 'character';
      else if (attrs.includes("location='")) entityType = 'location';
      else if (attrs.includes("faction='")) entityType = 'faction';
      else if (attrs.includes("event='")) entityType = 'event';
    }

    if (costMatch) cost = parseInt(costMatch[1]);

    processedText += text.substring(lastIndex, match.index);

    if (isItemInvestigated(itemName)) {
      processedText += `<span class="text-slate-300">${displayText}</span>`;
    } else if (getActiveJob(itemName)) {
      processedText += investigatingBtnHtml(itemName, entityType, cost, displayText);
    } else {
      processedText += investigateBtnHtml(itemName, entityType, cost, displayText);
    }

    lastIndex = regex.lastIndex;
  }

  processedText += text.substring(lastIndex);
  return { text: processedText };
}

function showInvestigationStatus(itemName, entityType, cost) {
  const job = getActiveJob(itemName);
  if (job) {
    // Show the "Under Investigation" modal
    document.getElementById('statusItemName').textContent = itemName;
    document.getElementById('investigationStatusDialog').classList.remove('hidden');
  } else {
    // Flash a brief toast then auto-open the confirmation dialog to retry
    showInvestigationToast(`Investigation for "${itemName}" failed — trying again…`);
    setTimeout(() => showInvestigationConfirmation(itemName, entityType, cost), 1200);
  }
}

function closeInvestigationStatusDialog() {
  document.getElementById('investigationStatusDialog').classList.add('hidden');
}

let _toastTimeout = null;
function showInvestigationToast(message) {
  const toast = document.getElementById('investigationToast');
  document.getElementById('investigationToastMsg').textContent = message;
  toast.classList.remove('hidden');
  clearTimeout(_toastTimeout);
  _toastTimeout = setTimeout(() => toast.classList.add('hidden'), 3000);
}

function showInvestigationConfirmation(itemName, entityType, cost) {
  const existing = currentEntities.find(e => (e.name || '').toLowerCase() === itemName.toLowerCase());
  if (existing) {
    openInvestigatedEntity(itemName);
    return;
  }
  pendingInvestigation = { itemName, entityType, cost };
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
  const { itemName, entityType, cost } = pendingInvestigation;
  pendingInvestigation = null;
  document.getElementById("confirmInvestigationDialog").classList.add("hidden");
  await queueInvestigation(itemName, entityType, cost);
}

async function queueInvestigation(itemName, entityType, cost) {
  if (investigationPoints < cost) {
    alert(`Insufficient investigation points: need ${cost}, have ${investigationPoints}`);
    return;
  }

  try {
    const response = await fetch("/api/investigate", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${getToken()}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        world_id: currentWorldId,
        item_name: itemName,
        entity_type: entityType,
        cost: cost,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || "Failed to queue investigation");
    }

    const data = await response.json();
    const jobId = data.investigation_id;

    investigationPoints = data.remaining_points;
    updateInvestigationPointsDisplay();

    activeInvestigations[jobId] = {
      jobId,
      itemName,
      entityType,
      status: "queued",
      result: null,
      startedAt: Date.now(),
      pointRestored: false,
      reviewed: false,
    };

    openInvestigationPanel();
    refreshNarrativeLinks();

    if (!investigationPollInterval) {
      investigationPollInterval = setInterval(pollInvestigations, 500);
    }
    if (!timerTickInterval) {
      tickInvestigationTimer();
      timerTickInterval = setInterval(tickInvestigationTimer, 1000);
    }

    renderInvestigationQueue();
  } catch (error) {
    console.error("Error queuing investigation:", error);
    alert(`Error: ${error.message}`);
  }
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

async function pollInvestigations() {
  const jobIds = Object.keys(activeInvestigations);
  if (jobIds.length === 0) {
    if (investigationPollInterval) {
      clearInterval(investigationPollInterval);
      investigationPollInterval = null;
    }
    return;
  }

  let queueChanged = false;
  for (const jobId of jobIds) {
    const inv = activeInvestigations[jobId];
    if (inv.status !== "queued" && inv.status !== "processing") continue;

    try {
      const response = await fetch(`/api/investigations/${jobId}`, {
        headers: { "Authorization": `Bearer ${getToken()}` },
      });
      if (!response.ok) continue;

      const data = await response.json();
      const prevStatus = inv.status;
      inv.status = data.status;

      if (data.status === "complete" && data.result) {
        inv.result = data.result;
        if (data.result.entity && !currentEntities.find(e => e.entity_id === data.result.entity.entity_id)) {
          currentEntities.push(data.result.entity);
          loadWorldState();
          refreshNarrativeLinks();
        }
      }

      if (inv.status !== prevStatus) queueChanged = true;
    } catch (error) {
      console.error("Error polling investigation:", error);
    }
  }

  if (queueChanged) {
    renderInvestigationQueue();
    refreshNarrativeLinks();
  }
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
      html += `
        <div class="min-w-[180px] max-w-[180px] flex-none bg-slate-900 border border-amber-900/40 rounded-xl p-3">
          <div class="flex items-center gap-2 mb-1.5">
            <div data-clover data-size="20" data-hue="38" class="flex-none"></div>
            <p class="text-sm font-medium text-slate-200 truncate">${inv.itemName}</p>
          </div>
          <p class="text-xs text-slate-600">Investigating…</p>
        </div>
      `;
    } else if (inv.status === "complete" && inv.result && !inv.reviewed) {
      const entity = inv.result.entity;
      const summary = entity.summary ? entity.summary.substring(0, 90) : '';
      html += `
        <div class="min-w-[220px] max-w-[220px] flex-none bg-amber-950/20 border border-amber-700/50 rounded-xl p-3 flex flex-col gap-2">
          <div class="flex items-center gap-1.5">
            <svg class="w-3.5 h-3.5 text-amber-400 flex-none" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
            </svg>
            <p class="text-sm font-medium text-amber-200 truncate">${inv.itemName}</p>
          </div>
          ${summary ? `<p class="text-xs text-slate-400 leading-relaxed" style="display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden">${summary}</p>` : ''}
          <button onclick="addToCompendiu