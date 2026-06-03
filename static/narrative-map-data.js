// Narrative Client Module: Tactical Map Data & Coordinate Calculation
// Line limit compliance: Under 250 lines
let playerPos = { x: 0, y: 0 };
let manPos = { x: 60, y: 60 }; // 5 feet East, 5 feet North (60 inches)
let lastTargetSubject = "old man";
let hoveredSubject = null;
let mapViewportRadiusInches = 240; // Default visible viewport radius (20 feet)
let mapPan = { x: 0, y: 0 }; // Pan offsets in grid inches

const defaultEntities = [
  { name: "old man", type: "character" },
  { name: "paladin guard", type: "character" },
  { name: "wooden chest", type: "object" },
  { name: "stone archway", type: "location" },
  { name: "door", type: "object" }
];

function resolveSubjectName(name) {
  const normName = (name || "").trim().toLowerCase();
  if (!normName) return "";
  
  if (normName === "self" || normName === "you" || normName === "player") {
    return "self";
  }
  
  const entitiesToDraw = [...(typeof currentEntities !== "undefined" ? currentEntities : [])];
  const defaults = [
    { name: "old man", type: "character" },
    { name: "paladin guard", type: "character" },
    { name: "wooden chest", type: "object" },
    { name: "stone archway", type: "location" },
    { name: "door", type: "object" }
  ];
  
  defaults.forEach(d => {
    if (!entitiesToDraw.some(e => e.name.toLowerCase() === d.name.toLowerCase())) {
      entitiesToDraw.push(d);
    }
  });
  
  for (const e of entitiesToDraw) {
    if (e.name.toLowerCase() === normName) {
      return e.name.toLowerCase();
    }
  }
  
  for (const e of entitiesToDraw) {
    const sName = e.name.toLowerCase();
    if (sName.includes(normName) || normName.includes(sName)) {
      return sName;
    }
  }
  
  return normName;
}

function getSubjectCoord(name) {
  const resolved = resolveSubjectName(name);
  if (resolved === "self") return playerPos;
  if (resolved === "old man") return { x: 60, y: 60 };
  if (resolved === "door" || resolved.includes("door")) return { x: -120, y: 0 };
  
  // Simple hash function to generate reproducible coordinates for dynamic entities
  let hash = 0;
  for (let i = 0; i < resolved.length; i++) {
    hash = resolved.charCodeAt(i) + ((hash << 5) - hash);
  }
  
  // Distribute angle between 0 and 2*PI deterministically
  const angle = Math.abs(hash % 360) * (Math.PI / 180);
  // Keep all dynamic subjects strictly inside the 20ft viewport: 3.5ft (42 inches) to 15ft (180 inches)
  const dist = 42 + (Math.abs(hash >> 8) % 138);
  
  let ex = Math.round(dist * Math.cos(angle));
  let gy = Math.round(dist * Math.sin(angle));
  // Clamp inside the 20x20ft room with a 15-inch margin so they don't sit on the walls
  ex = Math.max(-105, Math.min(105, ex));
  gy = Math.max(-105, Math.min(105, gy));
  return { x: ex, y: gy };
}

function initMapPositions() {
  const savedPlayer = localStorage.getItem("mapPlayerPos");
  const savedTarget = localStorage.getItem("mapLastTarget");
  if (savedPlayer) {
    try { playerPos = JSON.parse(savedPlayer); } catch(_) {}
  } else {
    playerPos = { x: 0, y: 0 };
  }
  mapPan = { x: 0, y: 0 };
  
  if (savedTarget) {
    lastTargetSubject = savedTarget;
  }
  drawMap();
}

function saveMapPositions() {
  localStorage.setItem("mapPlayerPos", JSON.stringify(playerPos));
  localStorage.setItem("mapLastTarget", lastTargetSubject);
}

function getMapViewParams() {
  const canvas = document.getElementById("mapCanvas");
  if (!canvas) return null;
  const rect = canvas.getBoundingClientRect();
  const width = rect.width;
  const height = rect.height;
  if (width < 50 || height < 50) return null;
  
  const entitiesToDraw = [...(typeof currentEntities !== "undefined" ? currentEntities : [])];
  defaultEntities.forEach(d => {
    if (!entitiesToDraw.some(e => e.name.toLowerCase() === d.name.toLowerCase())) {
      entitiesToDraw.push(d);
    }
  });

  let minX = playerPos.x;
  let maxX = playerPos.x;
  let minY = playerPos.y;
  let maxY = playerPos.y;

  entitiesToDraw.forEach(e => {
    const coords = getSubjectCoord(e.name);
    minX = Math.min(minX, coords.x);
    maxX = Math.max(maxX, coords.x);
    minY = Math.min(minY, coords.y);
    maxY = Math.max(maxY, coords.y);
  });
  
  const dx = maxX - minX;
  const dy = maxY - minY;
  const centerX = minX + dx / 2;
  const centerY = minY + dy / 2;
  const padding = 35;
  const minDimension = Math.min(width - padding * 2, height - padding * 2);
  let scale = minDimension / (mapViewportRadiusInches * 2);
  let viewCenterX = centerX + mapPan.x;
  let viewCenterY = centerY + mapPan.y;
  
  let px = width / 2 + (playerPos.x - viewCenterX) * scale;
  let py = height / 2 - (playerPos.y - viewCenterY) * scale;
  
  const maxCornerDistPx = Math.max(
    Math.sqrt(px * px + py * py),
    Math.sqrt((width - px) ** 2 + py * py),
    Math.sqrt(px * px + (height - py) ** 2),
    Math.sqrt((width - px) ** 2 + (height - py) ** 2)
  );
  
  const minScale = maxCornerDistPx / 240;
  if (scale < minScale) {
    scale = minScale;
    mapViewportRadiusInches = minDimension / (scale * 2);
    viewCenterX = centerX + mapPan.x;
    viewCenterY = centerY + mapPan.y;
  }
  
  function toCanvas(pos) {
    return {
      x: width / 2 + (pos.x - viewCenterX) * scale,
      y: height / 2 - (pos.y - viewCenterY) * scale
    };
  }
  
  return {
    canvas, rect, width, height, scale, toCanvas,
    centerX, centerY, viewCenterX, viewCenterY,
    minX, maxX, minY, maxY, entitiesToDraw
  };
}

function checkProximityDoorUse(jsonPayload, actionText, submitBtn, activeStageInterval) {
  const targetName = jsonPayload["door.target"] || "door";
  const resolvedTarget = resolveSubjectName(targetName);
  const targetPos = getSubjectCoord(resolvedTarget);
  const dx = targetPos.x - playerPos.x;
  const dy = targetPos.y - playerPos.y;
  const distInches = Math.sqrt(dx * dx + dy * dy);
  
  if (distInches > 36) {
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
      const distFt = (distInches / 12).toFixed(1);
      const prettyTarget = resolvedTarget.split(" ").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
      errText.textContent = `You are too far away to use the ${prettyTarget}. You must be within 3 feet (currently ${distFt} ft away).`;
      errBanner.classList.remove("hidden");
    }
    return false;
  }
  
  jsonPayload["door.within_range"] = true;
  return true;
}

function checkProximityIdentify(jsonPayload, actionText, submitBtn, activeStageInterval) {
  const targetName = jsonPayload["identify.target"];
  if (!targetName) {
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
      errText.textContent = "Please specify a target to identify or inspect.";
      errBanner.classList.remove("hidden");
    }
    return false;
  }
  
  const resolvedTarget = resolveSubjectName(targetName);
  const targetPos = getSubjectCoord(resolvedTarget);
  const dx = targetPos.x - playerPos.x;
  const dy = targetPos.y - playerPos.y;
  const distInches = Math.sqrt(dx * dx + dy * dy);
  
  if (distInches > 36) {
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
      const distFt = (distInches / 12).toFixed(1);
      const prettyTarget = resolvedTarget.split(" ").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
      errText.textContent = `You are too far away to identify or inspect the ${prettyTarget}. You must be within 3 feet (currently ${distFt} ft away).`;
      errBanner.classList.remove("hidden");
    }
    return false;
  }
  
  return true;
}
