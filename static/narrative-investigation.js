// Investigation system: panel, polling, queue, timer, points

const dispatchedPreGenerations = new Set();

function areNamesEquivalent(a, b) {
  if (!a || !b) return false;
  const aClean = a.trim().toLowerCase();
  const bClean = b.trim().toLowerCase();
  if (aClean === bClean) return true;

  const getVariants = (name) => {
    const s = new Set([name]);
    if (name.endsWith("s")) {
      if (name.endsWith("es")) {
        s.add(name.slice(0, -2));
      }
      s.add(name.slice(0, -1));
    } else {
      s.add(name + "s");
      s.add(name + "es");
    }
    return s;
  };

  const aVars = getVariants(aClean);
  const bVars = getVariants(bClean);
  for (const v of aVars) {
    if (bVars.has(v)) return true;
  }
  return false;
}

function getActiveJob(itemName) {
  return Object.values(activeInvestigations).find(
    inv => (inv.status === 'queued' || inv.status === 'processing') && areNamesEquivalent(inv.itemName, itemName)
  ) || null;
}

function isItemInvestigated(itemName) {
  if (Object.values(activeInvestigations).some(inv => inv.status === 'complete' && areNamesEquivalent(inv.itemName, itemName))) return true;
  return currentEntities.some(e => areNamesEquivalent(e.name, itemName));
}

function investigateBtnHtml(itemName, entityType, cost, displayText) {
  const escaped = itemName.replace(/'/g, "\\'");
  return `<button class="investigate-btn text-orange-500 underline decoration-dotted underline-offset-2 hover:text-orange-400 transition-colors text-[inherit] leading-[inherit]" data-inv-item="${itemName}" data-inv-type="${entityType}" data-inv-cost="${cost}" onclick="showInvestigationConfirmation('${escaped}', '${entityType}', ${cost}, this);">${displayText}</button>`;
}

function investigatingBtnHtml(itemName, entityType, cost, displayText) {
  const escaped = itemName.replace(/'/g, "\\'");
  const job = getActiveJob(itemName);
  const jobId = job ? job.jobId : '';
  return `<button class="investigate-btn text-emerald-400 underline decoration-dotted underline-offset-2 hover:text-emerald-300 transition-colors text-[inherit] leading-[inherit]" data-inv-item="${itemName}" data-inv-type="${entityType}" data-inv-cost="${cost}" data-investigating="true" data-job-id="${jobId}" onclick="showInvestigationStatus('${escaped}', '${entityType}', ${cost});">${displayText}</button>`;
}

function investigatedBtnHtml(itemName, displayText) {
  const escaped = itemName.replace(/'/g, "\\'");
  return `<button class="investigated-btn text-slate-300 hover:text-emerald-400 underline decoration-dotted decoration-emerald-500 underline-offset-2 transition-colors text-[inherit] leading-[inherit]" onclick="openInvestigatedEntity('${escaped}');">${displayText}</button>`;
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
      el.replaceWith(_htmlToElement(investigatedBtnHtml(itemName, displayText)));
    } else if (getActiveJob(itemName)) {
      el.replaceWith(_htmlToElement(investigatingBtnHtml(itemName, entityType, cost, displayText)));
    } else {
      el.replaceWith(_htmlToElement(investigateBtnHtml(itemName, entityType, cost, displayText)));
    }
  });

  preFetchInvestigationLinks();
}

function preFetchInvestigationLinks() {
  if (!currentWorldId) return;
  document.querySelectorAll('.investigate-btn').forEach(el => {
    if (el.getAttribute('data-investigating') === 'true') return;
    const itemName = el.getAttribute('data-inv-item');
    const entityType = el.getAttribute('data-inv-type') || 'object';
    if (!itemName || isItemInvestigated(itemName)) return;

    // session caching optimization
    const cacheKey = `${currentWorldId}:${itemName.toLowerCase()}`;
    if (dispatchedPreGenerations.has(cacheKey)) return;
    dispatchedPreGenerations.add(cacheKey);

    const closestBlock = el.closest('.narrative-block, #detailEntityContent') || el.closest('p, div');
    const contextText = closestBlock ? (closestBlock.innerText || '') : '';

    fetch("/api/investigate/pre-generate", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${getToken()}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        world_id: currentWorldId,
        item_name: itemName,
        entity_type: entityType,
        context: contextText
      })
    }).catch(err => {
      console.warn("Pre-generation failed for", itemName, err);
      dispatchedPreGenerations.delete(cacheKey);
    });
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

    let itemMatch = attrs.match(/(?:item|npc|location|faction|event)=(['"])(.*?)\1/);
    if (itemMatch) {
      itemName = itemMatch[2];
    } else {
      itemMatch = attrs.match(/(?:item|npc|location|faction|event)=([^'"\s>]+)/);
      if (itemMatch) {
        itemName = itemMatch[1];
      }
    }

    if (itemMatch) {
      if (/\bnpc\b/.test(attrs)) entityType = 'character';
      else if (/\blocation\b/.test(attrs)) entityType = 'location';
      else if (/\bfaction\b/.test(attrs)) entityType = 'faction';
      else if (/\bevent\b/.test(attrs)) entityType = 'event';
    }

    const costMatch = attrs.match(/cost=(['"]?)(\d+)\1/);
    if (costMatch) cost = parseInt(costMatch[2]);

    processedText += text.substring(lastIndex, match.index);

    if (isItemInvestigated(itemName)) {
      processedText += investigatedBtnHtml(itemName, displayText);
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

function showInvestigationConfirmation(itemName, entityType, cost, btnEl) {
  const existing = currentEntities.find(e => (e.name || '').toLowerCase() === itemName.toLowerCase());
  if (existing) {
    openInvestigatedEntity(itemName);
    return;
  }
  
  let contextText = '';
  if (btnEl) {
    const closestBlock = btnEl.closest('.narrative-block, #detailEntityContent') || btnEl.closest('p, div');
    if (closestBlock) {
      contextText = closestBlock.innerText || '';
    }
  } else {
    // Fallback: try to query the button
    const btn = document.querySelector(`.investigate-btn[data-inv-item="${itemName}"]`);
    const closestBlock = btn ? (btn.closest('.narrative-block, #detailEntityContent') || btn.closest('p, div')) : null;
    if (closestBlock) {
      contextText = closestBlock.innerText || '';
    }
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

async function queueInvestigation(itemName, entityType, cost, context = "") {
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
        context: context,
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
    // Auto-close after 2.5 seconds so it doesn't get stuck open, allowing hovering to cancel it!
    cancelPanelClose();
    panelCloseTimeout = setTimeout(closeInvestigationPanel, 2500);

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
      const response = await fetch(`/api/investigate/${jobId}`, {
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
        await updateCurrencyFromServer();
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
      const elapsed = Math.floor((Date.now() - inv.startedAt) / 1000);
      const remaining = Math.max(0, 60 - elapsed);
      const circumference = 100.5;
      const dashOffset = circumference * (1 - remaining / 60);

      html += `
        <div class="min-w-[180px] max-w-[180px] flex-none bg-slate-900 border border-amber-900/40 rounded-xl p-3 flex items-center justify-between gap-2">
          <div class="min-w-0 flex-1">
            <p class="text-sm font-medium text-slate-200 truncate" title="${inv.itemName}">${inv.itemName}</p>
            <p class="text-[10px] text-slate-500 mt-0.5 uppercase tracking-wider font-semibold">Investigating</p>
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
          <button onclick="viewInCompendium('${jobId}', '${entity.entity_id || entity.id}')" class="mt-auto bg-amber-600 hover:bg-amber-500 active:bg-amber-700 text-slate-900 font-semibold py-1 px-3 rounded-lg text-xs transition-colors">View in Compendium</button>
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

function restoreActiveInvestigations(jobs) {
  if (!jobs || jobs.length === 0) return;

  let restoredAny = false;
  jobs.forEach(job => {
    if (job.status === 'queued' || job.status === 'processing') {
      // Parse ISO string properly on all browsers
      const createdTime = new Date(job.created_at).getTime();
      activeInvestigations[job.job_id] = {
        jobId: job.job_id,
        itemName: job.entity_name,
        entityType: job.entity_type,
        status: job.status,
        result: null,
        startedAt: createdTime, // Maintain precise elapsed time relative to when it was queued!
        pointRestored: false,
        reviewed: false,
      };
      restoredAny = true;
    }
  });

  if (restoredAny) {
    openInvestigationPanel();
    refreshNarrativeLinks();
    renderInvestigationQueue();

    if (!investigationPollInterval) {
      investigationPollInterval = setInterval(pollInvestigations, 500);
    }
    if (!timerTickInterval) {
      tickInvestigationTimer();
      timerTickInterval = setInterval(tickInvestigationTimer, 1000);
    }
  }
}