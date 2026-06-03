// Narrative Client Module: Tactical Map Canvas Rendering
// Line limit compliance: Under 290 lines

function drawMap() {
  const params = getMapViewParams();
  if (!params) return;
  const { canvas, width, height, scale, toCanvas, viewCenterX, viewCenterY, entitiesToDraw } = params;
  const ctx = canvas.getContext("2d");
  
  const minVisibleX = viewCenterX - (width / 2) / scale;
  const maxVisibleX = viewCenterX + (width / 2) / scale;
  const minVisibleY = viewCenterY - (height / 2) / scale;
  const maxVisibleY = viewCenterY + (height / 2) / scale;

  canvas.width = width * window.devicePixelRatio;
  canvas.height = height * window.devicePixelRatio;
  ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
  
  // Clear canvas
  ctx.fillStyle = "#020617"; // slate-950
  ctx.fillRect(0, 0, width, height);
  
  // Draw grid background (5ft squares = 60 inches) aligned to world coordinates
  ctx.strokeStyle = "#1e293b"; // slate-800
  ctx.lineWidth = 0.5;
  const gridSpacingInches = 60; // 5 feet
  const startGridX = Math.floor(minVisibleX / gridSpacingInches) * gridSpacingInches;
  const endGridX = Math.ceil(maxVisibleX / gridSpacingInches) * gridSpacingInches;
  const startGridY = Math.floor(minVisibleY / gridSpacingInches) * gridSpacingInches;
  const endGridY = Math.ceil(maxVisibleY / gridSpacingInches) * gridSpacingInches;

  for (let gx = startGridX; gx <= endGridX; gx += gridSpacingInches) {
    const canvasX = width / 2 + (gx - viewCenterX) * scale;
    ctx.beginPath();
    ctx.moveTo(canvasX, 0);
    ctx.lineTo(canvasX, height);
    ctx.stroke();
  }
  for (let gy = startGridY; gy <= endGridY; gy += gridSpacingInches) {
    const canvasY = height / 2 - (gy - viewCenterY) * scale;
    ctx.beginPath();
    ctx.moveTo(0, canvasY);
    ctx.lineTo(width, canvasY);
    ctx.stroke();
  }

  // Draw the 20x20 ft room border
  const roomBottomLeft = toCanvas({ x: -120, y: -120 });
  const roomTopRight = toCanvas({ x: 120, y: 120 });
  ctx.strokeStyle = "#334155"; // slate-700 for wall base
  ctx.lineWidth = 5;
  ctx.strokeRect(
    roomBottomLeft.x,
    roomTopRight.y,
    roomTopRight.x - roomBottomLeft.x,
    roomBottomLeft.y - roomTopRight.y
  );
  ctx.strokeStyle = "#64748b"; // slate-500 inner thin line
  ctx.lineWidth = 1.5;
  ctx.strokeRect(
    roomBottomLeft.x,
    roomTopRight.y,
    roomTopRight.x - roomBottomLeft.x,
    roomBottomLeft.y - roomTopRight.y
  );
  
  // Draw step crosshairs and coordinates every 10 feet (120 inches)
  ctx.fillStyle = "rgba(148, 163, 184, 0.8)";
  ctx.font = "9px monospace";
  ctx.textAlign = "center";
  const step = 120;
  const startX = Math.floor(minVisibleX / step) * step;
  const endX = Math.ceil(maxVisibleX / step) * step;
  const startY = Math.floor(minVisibleY / step) * step;
  const endY = Math.ceil(maxVisibleY / step) * step;
  
  for (let gx = startX; gx <= endX; gx += step) {
    for (let gy = startY; gy <= endY; gy += step) {
      const c = toCanvas({ x: gx, y: gy });
      if (c.x < 0 || c.x > width || c.y < 0 || c.y > height) continue;
      
      ctx.strokeStyle = "rgba(148, 163, 184, 0.25)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(c.x - 3, c.y); ctx.lineTo(c.x + 3, c.y);
      ctx.moveTo(c.x, c.y - 3); ctx.lineTo(c.x, c.y + 3);
      ctx.stroke();
      
      const ftX = Math.round(gx / 12);
      const ftY = Math.round(gy / 12);
      ctx.fillText(`(${ftX},${ftY})`, c.x, c.y - 6);
    }
  }
  ctx.textAlign = "left"; // Reset align
  
  // Draw connecting dashed line to active target
  const targetPos = getSubjectCoord(lastTargetSubject);
  const targetCanvas = toCanvas(targetPos);
  const playerCanvas = toCanvas(playerPos);
  
  ctx.strokeStyle = "rgba(245, 158, 11, 0.2)";
  ctx.lineWidth = 1;
  ctx.setLineDash([4, 4]);
  ctx.beginPath();
  ctx.moveTo(playerCanvas.x, playerCanvas.y);
  ctx.lineTo(targetCanvas.x, targetCanvas.y);
  ctx.stroke();
  ctx.setLineDash([]);
  
  // Draw all subjects
  entitiesToDraw.forEach(e => {
    const coords = getSubjectCoord(e.name);
    const canvasPos = toCanvas(coords);
    const type = (e.entity_type || e.type || "").toLowerCase();
    
    const isFocused = e.name.toLowerCase() === lastTargetSubject.toLowerCase();
    const isHovered = hoveredSubject && e.name.toLowerCase() === hoveredSubject.toLowerCase();
    
    if (e.name.toLowerCase().startsWith("door")) {
      const doorTop = toCanvas({ x: -120, y: 18 });
      const doorBottom = toCanvas({ x: -120, y: -18 });
      
      ctx.fillStyle = "#b45309"; // amber-700
      ctx.shadowColor = "#f59e0b";
      ctx.shadowBlur = isHovered ? 12 : 6;
      ctx.fillRect(canvasPos.x - 3, doorTop.y, 6, doorBottom.y - doorTop.y);
      ctx.shadowBlur = 0;
      
      ctx.strokeStyle = isHovered || isFocused ? "#ffffff" : "#f59e0b";
      ctx.lineWidth = isHovered ? 2 : 1.5;
      ctx.strokeRect(canvasPos.x - 3, doorTop.y, 6, doorBottom.y - doorTop.y);

      const labelText = e.name.split(" ").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
      ctx.fillStyle = isFocused ? "#f59e0b" : (isHovered ? "#f8fafc" : "#94a3b8");
      ctx.font = isFocused || isHovered ? "bold 9px sans-serif" : "9px sans-serif";
      ctx.fillText(labelText, canvasPos.x + 8, canvasPos.y + 3);
      
      if (isHovered) {
        const textWidth = ctx.measureText(labelText).width;
        ctx.strokeStyle = ctx.fillStyle;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(canvasPos.x + 8, canvasPos.y + 5);
        ctx.lineTo(canvasPos.x + 8 + textWidth, canvasPos.y + 5);
        ctx.stroke();
      }
      return;
    }
    
    let color = "#a855f7"; // purple-500 for locations
    if (e.name.toLowerCase() === "old man") {
      color = "#f59e0b";
    } else if (type === "character") {
      color = "#f43f5e";
    } else if (type === "object" || type === "item") {
      color = "#06b6d4";
    }
    
    ctx.beginPath();
    if (isHovered) {
      ctx.strokeStyle = "#ffffff";
      ctx.lineWidth = 1.5;
      ctx.arc(canvasPos.x, canvasPos.y, 7, 0, Math.PI * 2);
      ctx.stroke();
      ctx.beginPath();
    }
    
    ctx.shadowColor = color;
    ctx.shadowBlur = isHovered ? 12 : 6;
    ctx.fillStyle = color;
    ctx.arc(canvasPos.x, canvasPos.y, isHovered ? 5.5 : 4, 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0;
    
    const labelText = e.name.split(" ").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
    ctx.fillStyle = isFocused ? "#f59e0b" : (isHovered ? "#f8fafc" : "#94a3b8");
    ctx.font = isFocused || isHovered ? "bold 9px sans-serif" : "9px sans-serif";
    ctx.fillText(labelText, canvasPos.x + 7, canvasPos.y + 3);
    
    if (isHovered) {
      const textWidth = ctx.measureText(labelText).width;
      ctx.strokeStyle = ctx.fillStyle;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(canvasPos.x + 7, canvasPos.y + 5);
      ctx.lineTo(canvasPos.x + 7 + textWidth, canvasPos.y + 5);
      ctx.stroke();
    }
  });
  
  // Draw Player (Blue dot with pulse glow)
  ctx.beginPath();
  ctx.shadowColor = "#3b82f6";
  ctx.shadowBlur = 10;
  ctx.fillStyle = "#3b82f6";
  ctx.arc(playerCanvas.x, playerCanvas.y, 5, 0, Math.PI * 2);
  ctx.fill();
  ctx.shadowBlur = 0;
  
  ctx.fillStyle = "#3b82f6";
  ctx.font = "bold 9px sans-serif";
  ctx.fillText("You", playerCanvas.x + 8, playerCanvas.y + 3);

  // Update status coordinates in DOM
  const playerCoordsEl = document.getElementById("mapPlayerCoords");
  if (playerCoordsEl) {
    playerCoordsEl.textContent = `${(playerPos.x / 12).toFixed(1)} ft, ${(playerPos.y / 12).toFixed(1)} ft`;
  }
  
  const manCoordsEl = document.getElementById("mapManCoords");
  if (manCoordsEl) {
    const targetLabel = lastTargetSubject.split(" ").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
    const container = manCoordsEl.parentElement;
    if (container) {
      container.innerHTML = `${targetLabel}: <span id="mapManCoords">${(targetPos.x / 12).toFixed(1)} ft, ${(targetPos.y / 12).toFixed(1)} ft</span>`;
    }
  }
  
  const distLabelEl = document.getElementById("mapDistanceLabel");
  if (distLabelEl) {
    const dx = targetPos.x - playerPos.x;
    const dy = targetPos.y - playerPos.y;
    const distFt = (Math.sqrt(dx * dx + dy * dy) / 12).toFixed(1);
    distLabelEl.textContent = `Dist: ${distFt} ft`;
  }
}

function updatePlayerLocationFromPayload(payload) {
  const dist = payload["move.distance_inches"];
  if (dist === null || dist === undefined) return;
  
  const dir = (payload["move.direction"] || "").toLowerCase();
  const subjectName = payload["towards.subject"] || "old man";
  const isSelf = subjectName.toLowerCase() === "self" || subjectName.toLowerCase() === "you";
  
  lastTargetSubject = subjectName;
  const targetPos = getSubjectCoord(subjectName);
  
  if (isSelf) {
    if (dir === "forwards" || dir === "north" || dir === "northg") {
      playerPos.y += dist;
    } else if (dir === "back" || dir === "south") {
      playerPos.y -= dist;
    } else if (dir === "east") {
      playerPos.x += dist;
    } else if (dir === "west") {
      playerPos.x -= dist;
    }
  } else {
    if (dir === "north" || dir === "northg") {
      playerPos.y += dist;
    } else if (dir === "south") {
      playerPos.y -= dist;
    } else if (dir === "east") {
      playerPos.x += dist;
    } else if (dir === "west") {
      playerPos.x -= dist;
    } else if (dir === "towards" || dir === "forwards") {
      const dx = targetPos.x - playerPos.x;
      const dy = targetPos.y - playerPos.y;
      const d = Math.sqrt(dx * dx + dy * dy);
      if (d > 0) {
        if (dist >= d) {
          playerPos.x = targetPos.x;
          playerPos.y = targetPos.y;
        } else {
          playerPos.x += dx * (dist / d);
          playerPos.y += dy * (dist / d);
        }
      }
    } else if (dir === "away" || dir === "back") {
      const dx = targetPos.x - playerPos.x;
      const dy = targetPos.y - playerPos.y;
      const d = Math.sqrt(dx * dx + dy * dy);
      if (d > 0) {
        playerPos.x -= dx * (dist / d);
        playerPos.y -= dy * (dist / d);
      } else {
        playerPos.y -= dist;
      }
    }
  }
  playerPos.x = Math.max(-120, Math.min(120, playerPos.x));
  playerPos.y = Math.max(-120, Math.min(120, playerPos.y));
  
  saveMapPositions();
  drawMap();
}
// Setup ResizeObserver to guarantee rendering once canvas is placed/resized
(function() {
  const canvas = document.getElementById("mapCanvas");
  if (canvas) {
    const resizeObserver = new ResizeObserver(() => {
      drawMap();
    });
    resizeObserver.observe(canvas);
  }
})();
