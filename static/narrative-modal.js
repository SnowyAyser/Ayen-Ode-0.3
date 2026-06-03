// Narrative Client Module: Clarification Modal Handling
// Line limit compliance: Under 150 lines
let currentClarifyPayload = null;

function openClarifyModal(promptText, jsonPayload) {
  currentClarifyPayload = jsonPayload;
  
  const modal = document.getElementById("movementClarifyModal");
  document.getElementById("clarifyPromptText").textContent = promptText;
  
  document.getElementById("fieldFullAction").classList.add("hidden");
  document.getElementById("fieldSubject").classList.add("hidden");
  document.getElementById("fieldDistance").classList.add("hidden");
  document.getElementById("fieldDirection").classList.add("hidden");
  
  const detailsBox = document.getElementById("statusDetails");
  const detectedText = document.getElementById("statusDetected");
  
  const datalist = document.getElementById("sceneSubjectsList");
  if (datalist) {
    const subjects = (typeof currentEntities !== "undefined" ? currentEntities.map(e => e.name) : []).filter(Boolean);
    if (!subjects.includes("old man")) subjects.push("old man");
    datalist.innerHTML = subjects.map(s => `<option value="${s}"></option>`).join("");
  }

  document.getElementById("inputFullAction").value = "";
  document.getElementById("inputSubject").value = "";
  document.getElementById("inputDistanceValue").value = "";
  document.getElementById("inputDistanceUnit").value = "feet";
  document.getElementById("inputDirection").value = "";

  if (!jsonPayload) {
    detectedText.textContent = "No";
    detectedText.className = "text-red-400 font-semibold";
    detailsBox.classList.add("hidden");
    document.getElementById("fieldFullAction").classList.remove("hidden");
    setTimeout(() => document.getElementById("inputFullAction").focus(), 100);
  } else {
    detectedText.textContent = "Yes";
    detectedText.className = "text-emerald-400 font-semibold";
    detailsBox.classList.remove("hidden");
    
    document.getElementById("statusSubject").textContent = jsonPayload["towards.subject"] || "—";
    document.getElementById("statusDistance").textContent = jsonPayload["move.distance_inches"] !== null ? `${jsonPayload["move.distance_inches"]} inches` : "—";
    document.getElementById("statusDirection").textContent = jsonPayload["move.direction"] || "—";
    
    let focusElement = null;
    
    if (!jsonPayload["towards.subject"]) {
      document.getElementById("fieldSubject").classList.remove("hidden");
      if (!focusElement) focusElement = document.getElementById("inputSubject");
    }
    
    if (jsonPayload["move.distance_inches"] === null) {
      document.getElementById("fieldDistance").classList.remove("hidden");
      if (!focusElement) focusElement = document.getElementById("inputDistanceValue");
    }
    
    if (!jsonPayload["move.direction"]) {
      document.getElementById("fieldDirection").classList.remove("hidden");
      if (!focusElement) focusElement = document.getElementById("inputDirection");
    }
    
    if (focusElement) {
      setTimeout(() => focusElement.focus(), 100);
    }
  }
  
  modal.classList.remove("hidden");
}

function closeClarifyModal() {
  document.getElementById("movementClarifyModal").classList.add("hidden");
  if (lastUserBlockNode) {
    lastUserBlockNode.remove();
    lastUserBlockNode = null;
  }
  document.getElementById("actionInput").focus();
}

async function submitClarifiedAction() {
  const modal = document.getElementById("movementClarifyModal");
  
  let reconstructedText = "";
  if (!currentClarifyPayload) {
    reconstructedText = document.getElementById("inputFullAction").value.trim();
    if (!reconstructedText) return;
  } else {
    const subjectVal = document.getElementById("inputSubject").value.trim() || currentClarifyPayload["towards.subject"] || "";
    
    let distanceVal = "";
    if (!document.getElementById("fieldDistance").classList.contains("hidden")) {
      const distNum = document.getElementById("inputDistanceValue").value.trim();
      const distUnit = document.getElementById("inputDistanceUnit").value;
      if (distNum) {
        distanceVal = `${distNum} ${distUnit}`;
      }
    } else {
      distanceVal = currentClarifyPayload["move.distance_inches"] !== null ? `${currentClarifyPayload["move.distance_inches"]} inches` : "";
    }
    
    const directionVal = document.getElementById("inputDirection").value || currentClarifyPayload["move.direction"] || "towards";
    
    if (!subjectVal && !document.getElementById("fieldSubject").classList.contains("hidden")) {
      alert("Please clarify the target subject.");
      return;
    }
    if (!distanceVal && !document.getElementById("fieldDistance").classList.contains("hidden")) {
      alert("Please clarify the distance.");
      return;
    }
    
    reconstructedText = `I move ${distanceVal} ${directionVal} ${subjectVal}`.trim();
  }
  
  modal.classList.add("hidden");
  
  if (lastUserBlockNode) {
    lastUserBlockNode.querySelector(".italic").textContent = reconstructedText;
  } else {
    const narrativeDiv = document.getElementById("narrativeContent");
    lastUserBlockNode = _makeUserBlock(reconstructedText);
    narrativeDiv.appendChild(lastUserBlockNode);
    narrativeDiv.scrollTop = narrativeDiv.scrollHeight;
  }
  
  await executeNarrativeSubmit(reconstructedText, true);
}

document.addEventListener("DOMContentLoaded", () => {
  const confirmBtn = document.getElementById("confirmClarifyBtn");
  if (confirmBtn) {
    confirmBtn.addEventListener("click", submitClarifiedAction);
  }
});
