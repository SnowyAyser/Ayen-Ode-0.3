const dispatchedPreGenerations = new Set();

function areNamesEquivalent(a, b) {
  if (!a || !b) return false;
  const stripArticles = (str) => {
    let s = str.trim().toLowerCase();
    for (const art of ["the ", "a ", "an "]) {
      if (s.startsWith(art)) {
        s = s.substring(art.length).trim();
        break;
      }
    }
    return s;
  };
  const aC = stripArticles(a), bC = stripArticles(b);
  if (aC === bC) return true;
  const getV = (n) => {
    const s = new Set([n]);
    if (n.endsWith("s")) {
      if (n.endsWith("es")) s.add(n.slice(0, -2));
      s.add(n.slice(0, -1));
    } else { s.add(n + "s"); s.add(n + "es"); }
    return s;
  };
  const aV = getV(aC), bV = getV(bC);
  for (const v of aV) { if (bV.has(v)) return true; }
  return false;
}

const getActiveJob = (name) => Object.values(activeInvestigations).find(i => (i.status === 'queued' || i.status === 'processing') && areNamesEquivalent(i.itemName, name)) || null;
const isItemInvestigated = (name) => Object.values(activeInvestigations).some(i => i.status === 'complete' && areNamesEquivalent(i.itemName, name)) || currentEntities.some(e => areNamesEquivalent(e.name, name));

const investigateBtnHtml = (name, type, cost, text) => `<button class="investigate-btn text-orange-500 underline decoration-dotted underline-offset-2 hover:text-orange-400 transition-colors text-[inherit] leading-[inherit]" data-inv-item="${name}" data-inv-type="${type}" data-inv-cost="${cost}" onclick="showInvestigationConfirmation('${name.replace(/'/g, "\\'")}', '${type}', ${cost}, this);">${text}</button>`;
const investigatingBtnHtml = (name, type, cost, text) => `<button class="investigate-btn text-emerald-400 underline decoration-dotted underline-offset-2 hover:text-emerald-300 transition-colors text-[inherit] leading-[inherit]" data-inv-item="${name}" data-inv-type="${type}" data-inv-cost="${cost}" data-investigating="true" data-job-id="${(getActiveJob(name) || {}).jobId || ''}" onclick="showInvestigationStatus('${name.replace(/'/g, "\\'")}', '${type}', ${cost});">${text}</button>`;
const investigatedBtnHtml = (name, text) => `<button class="investigated-btn text-slate-300 hover:text-emerald-400 underline decoration-dotted decoration-emerald-500 underline-offset-2 transition-colors text-[inherit] leading-[inherit]" onclick="openInvestigatedEntity('${name.replace(/'/g, "\\'")}');">${text}</button>`;

function _htmlToElement(html) {
  const tmp = document.createElement('div');
  tmp.innerHTML = html;
  return tmp.firstElementChild;
}

function refreshNarrativeLinks() {
  document.querySelectorAll('.investigate-btn').forEach(el => {
    let itemName = el.getAttribute('data-inv-item');
    let entityType = el.getAttribute('data-inv-type') || 'object';
    let cost = parseInt(el.getAttribute('data-inv-cost') || '1');

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
    const attrs = match[1].replace(/\\/g, '');
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

async function queueInvestigation(itemName, entityType, cost, context = "") {
  if (investigationPoints < cost) {
    if (typeof showInsufficientPointsDialog === 'function') {
      showInsufficientPointsDialog(cost, investigationPoints);
    } else {
      alert(`Insufficient investigation points: need ${cost}, have ${investigationPoints}`);
    }
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
    if (data.already_completed) {
      investigationPoints = data.remaining_points;
      updateInvestigationPointsDisplay();
      if (typeof openInvestigatedEntity === 'function') {
        openInvestigatedEntity(data.item_name || itemName);
      }
      return;
    }
    const jobId = data.investigation_id;

    investigationPoints = data.remaining_points;
    updateInvestigationPointsDisplay();

    const prevJob = activeInvestigations[jobId] || {};
    activeInvestigations[jobId] = {
      jobId,
      itemName,
      entityType,
      status: data.status || "queued",
      priority: data.priority !== undefined ? data.priority : (data.bumped ? 0 : 0),
      result: prevJob.result || null,
      startedAt: data.bumped ? Date.now() : (prevJob.startedAt || Date.now()),
      pointRestored: prevJob.pointRestored || false,
      reviewed: prevJob.reviewed || false,
    };

    if (data.bumped) {
      if (typeof showInvestigationToast === 'function') {
        showInvestigationToast(`Prioritized "${itemName}" — resolving next!`);
      }
    } else if (data.processing) {
      if (typeof showInvestigationToast === 'function') {
        showInvestigationToast(`"${itemName}" is under active investigation!`);
      }
    }

    openInvestigationPanel();
    refreshNarrativeLinks();
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
      if (data.priority !== undefined) {
        inv.priority = data.priority;
      }

      if (data.status === "complete" && data.result) {
        inv.result = data.result;
        if (data.result.entity && !currentEntities.find(e => e.entity_id === data.result.entity.entity_id)) {
          currentEntities.push(data.result.entity);
          if (typeof entityCache !== 'undefined') {
            for (const key in entityCache) delete entityCache[key];
          }
          loadWorldState();
          refreshNarrativeLinks();
        }
        await updateCurrencyFromServer();
      }

      const prevStage = inv.activeStage;
      inv.activeStage = data.active_stage || null;
      if (inv.activeStage !== prevStage) queueChanged = true;

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

function restoreActiveInvestigations(jobs) {
  if (!jobs || jobs.length === 0) return;

  let restoredAny = false;
  jobs.forEach(job => {
    if (job.status === 'queued' || job.status === 'processing') {
      const createdTime = new Date(job.created_at).getTime();
      activeInvestigations[job.job_id] = {
        jobId: job.job_id,
        itemName: job.entity_name,
        entity_type: job.entity_type,
        status: job.status,
        priority: job.priority !== undefined ? job.priority : 1,
        result: null,
        startedAt: createdTime,
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


