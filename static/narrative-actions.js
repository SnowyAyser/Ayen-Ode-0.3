// Narrative Client Module: Actions Form & Narrative Execution Submission
// Line limit compliance: Under 270 lines
let lastUserBlockNode = null;

async function executeNarrativeSubmit(actionText, isClarificationSubmit = false) {
  const submitBtn = document.getElementById("submitBtn");
  submitBtn.disabled = true;
  const btnLoader = document.createElement('div');
  btnLoader.className = 'flex items-center justify-center gap-1.5';
  const cloverWrap = document.createElement('div');
  CloverLoader.createLoader(cloverWrap, 16, 38);
  btnLoader.appendChild(cloverWrap);
  
  const statusSpan = Object.assign(document.createElement('span'), {
    id: 'actionStageStatus',
    textContent: '…',
    className: 'text-xs text-slate-400 font-mono ml-1 max-w-[200px] truncate'
  });
  btnLoader.appendChild(statusSpan);
  submitBtn.replaceChildren(btnLoader);

  let activeStageInterval = null;
  if (currentWorldId) {
    activeStageInterval = setInterval(async () => {
      try {
        const res = await fetch(`/api/worlds/${currentWorldId}/active-stage`, {
          headers: { "Authorization": `Bearer ${getToken()}` }
        });
        if (res.ok) {
          const d = await res.json();
          const statusEl = document.getElementById('actionStageStatus');
          if (statusEl && d.active_stage) {
            statusEl.textContent = d.active_stage;
          }
        }
      } catch (err) {
        console.warn("Failed to fetch active stage status", err);
      }
    }, 500);
  }

  const narrativeDiv = document.getElementById("narrativeContent");
  if (!isClarificationSubmit) {
    lastUserBlockNode = _makeUserBlock(actionText);
    narrativeDiv.appendChild(lastUserBlockNode);
    narrativeDiv.scrollTop = narrativeDiv.scrollHeight;
  }

  try {
    const response = await fetch("/api/narrative", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${getToken()}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        world_id: currentWorldId,
        action: actionText,
        history: conversationHistory,
      }),
    });

    if (!response.ok) throw new Error("Failed to process action");

    const data = await response.json();
    let narrativeResponse = data.narrative;

    // Check if narrativeResponse is JSON
    let isJson = false;
    let jsonPayload = null;
    try {
      jsonPayload = JSON.parse(narrativeResponse);
      isJson = true;
    } catch (_) {}

    if (isJson && jsonPayload && jsonPayload["player.move"] === true) {
      const subj = (jsonPayload["towards.subject"] || "").trim().toLowerCase();
      if (subj === "self" || subj === "you") {
        jsonPayload["towards.subject"] = "self";
      }
      
      const dir = (jsonPayload["move.direction"] || "").toLowerCase();
      if (["north", "south", "east", "west", "forwards", "back"].includes(dir)) {
        if (!jsonPayload["towards.subject"]) {
          jsonPayload["towards.subject"] = "self";
        }
      }
    }

    // Door Proximity range-checking
    if (isJson && jsonPayload && jsonPayload["player.door_use"] === true) {
      if (!checkProximityDoorUse(jsonPayload, actionText, submitBtn, activeStageInterval)) {
        return;
      }
      narrativeResponse = JSON.stringify(jsonPayload, null, 2);
    }

    // Identify Proximity range-checking
    if (isJson && jsonPayload && jsonPayload["player.identify"] === true) {
      if (!checkProximityIdentify(jsonPayload, actionText, submitBtn, activeStageInterval)) {
        return;
      }
    }

    const needsClarification = isJson && jsonPayload && jsonPayload["player.move"] === true && (
      !jsonPayload["towards.subject"] ||
      jsonPayload["move.distance_inches"] === null ||
      !jsonPayload["move.direction"]
    );

    if (!isJson || (jsonPayload && jsonPayload["player.move"] === false)) {
      if (activeStageInterval) clearInterval(activeStageInterval);
      submitBtn.disabled = false;
      submitBtn.textContent = 'Act';
      
      if (lastUserBlockNode) {
        lastUserBlockNode.remove();
        lastUserBlockNode = null;
      }
      
      const inputEl = document.getElementById("actionInput");
      inputEl.value = actionText;
      autoResizeTextarea(inputEl);
      updateCharCount(inputEl);
      inputEl.focus();
      
      const errBanner = document.getElementById("noMovementError");
      const errText = document.getElementById("noMovementErrorText");
      if (errBanner && errText) {
        let msg = "No movement detected. Please clarify your movement action to proceed.";
        if (!isJson) {
          msg = narrativeResponse || msg;
        } else if (jsonPayload && jsonPayload.clarification_prompt) {
          msg = jsonPayload.clarification_prompt;
        }
        errText.textContent = msg;
        errBanner.classList.remove("hidden");
      }
      return;
    } else if (needsClarification) {
      if (activeStageInterval) clearInterval(activeStageInterval);
      submitBtn.disabled = false;
      submitBtn.textContent = 'Act';
      
      document.getElementById("noMovementError")?.classList.add("hidden");
      
      let missingFields = [];
      if (!jsonPayload["towards.subject"]) {
        missingFields.push("target subject (e.g. 'old man')");
      }
      if (jsonPayload["move.distance_inches"] === null) {
        missingFields.push("distance (e.g. 3 feet)");
      }
      if (!jsonPayload["move.direction"]) {
        missingFields.push("direction (e.g. 'towards' or 'away')");
      }
      
      const promptText = "Clarification needed: please provide the missing movement details: " + missingFields.join(", ") + ".";
      openClarifyModal(promptText, jsonPayload);
      return;
    }

    // Success: movement or identify action is complete
    lastUserBlockNode = null;
    document.getElementById("noMovementError")?.classList.add("hidden");

    if (isJson && jsonPayload && jsonPayload["player.move"] === true) {
      updatePlayerLocationFromPayload(jsonPayload);
    }

    conversationHistory = data.history || conversationHistory;
    // Sync the local history if we amended the door use proximity state parameters
    if (isJson && jsonPayload && jsonPayload["player.door_use"] === true && conversationHistory.length > 0) {
      const lastHist = conversationHistory[conversationHistory.length - 1];
      if (lastHist.role === "assistant") {
        lastHist.content = narrativeResponse;
      }
    }
    saveHistoryToStorage();

    if (data.investigation_points !== undefined) {
      investigationPoints = data.investigation_points;
      if (data.max_investigation_points !== undefined) maxInvestigationPoints = data.max_investigation_points;
      updateInvestigationPointsDisplay();
    }
    if (data.game_time) updateTimeDisplay(data.game_time);

    narrativeDiv.appendChild(_makeNarrativeBlock(narrativeResponse, {
      theme_report: data.theme_report,
      quest_report: data.quest_report,
      mechanics_report: data.mechanics_report
    }));
    refreshNarrativeLinks();

    narrativeDiv.scrollTop = narrativeDiv.scrollHeight;

    try {
      const worldResp = await fetch(`/api/world?world_id=${currentWorldId}`, {
        headers: { "Authorization": `Bearer ${getToken()}` }
      });
      if (worldResp.ok) {
        const worldData = await worldResp.json();
        currentEntities = worldData.entities || [];
        for (const key in entityCache) delete entityCache[key];
      }
    } catch (_) {}

    await updateCurrencyFromServer();
    loadWorldState();
    loadQuests();
  } catch (error) {
    console.error("Error processing action:", error);
    document.getElementById("narrativeContent").innerHTML +=
      `<div class="text-red-400 text-sm p-3 bg-red-950/20 border border-red-900/30 rounded-lg">Error: ${error.message}</div>`;
  } finally {
    if (activeStageInterval) {
      clearInterval(activeStageInterval);
    }
    submitBtn.disabled = false;
    submitBtn.textContent = 'Act';
    document.getElementById("actionInput").focus();
  }
}

document.getElementById("actionForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const actionText = document.getElementById("actionInput").value.trim();
  if (!actionText) return;

  if (getSettings().confirmBeforeSend && !pendingConfirm) {
    pendingConfirm = true;
    const inputEl = document.getElementById('actionInput');
    inputEl.classList.add('border-amber-600');
    inputEl.readOnly = true;
    const hint = document.getElementById('inputHintText');
    if (hint) hint.textContent = 'Press Enter to send  ·  Esc to cancel';
    return;
  }
  pendingConfirm = false;
  const inputEl0 = document.getElementById('actionInput');
  inputEl0.classList.remove('border-amber-600');
  inputEl0.readOnly = false;
  _restoreHintText();

  const inputEl = document.getElementById("actionInput");
  inputEl.value = "";
  autoResizeTextarea(inputEl);
  updateCharCount(inputEl);
  if (currentWorldId) localStorage.removeItem(_draftKey());

  await executeNarrativeSubmit(actionText, false);
});

setTimeout(() => { const el = document.getElementById("actionInput"); el.focus(); autoResizeTextarea(el); }, 500);
document.getElementById("compendiumSearch").addEventListener("input", loadWorldState);
