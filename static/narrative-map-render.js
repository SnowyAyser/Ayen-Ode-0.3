// Narrative Client Module: Tactical Map Canvas Rendering & Controls
// Line limit compliance: Under 280 lines
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
  ctx.fillStyle = "rgba(148, 163, 184, 0.4)";
  ctx.font = "7px monospace";
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
      
      ctx.strokeStyle = "rgba(148, 163, 184, 0.15)";
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
  
  ctx.strokeStyle = "rgba(245, 158, 11, 0.15)";
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
    
    if (e.name.toLowerCase() === "door") {
      const doorTop = toCanvas({ x: -120, y: 18 });
      const doorBottom = toCanvas({ x: -120, y: -18 });
      
      ctx.fillStyle = "#b45309"; // amber-700
      ctx.shadowColor = "#f59e0b";
      ctx.shadowBlur = isHovered ? 12 : 6;
      ctx.fillRect(
        canvasPos.x - 3,
        doorTop.y,
        6,
        doorBottom.y - doorTop.y
      );
      ctx.shadowBlur = 0;
      
      ctx.strokeStyle = isHovered || isFocused ? "#ffffff" : "#f59e0b";
      ctx.lineWidth = isHovered ? 2 : 1.5;
      ctx.strokeRect(
        canvasPos.x - 3,
        doorTop.y,
        6,
        doorBottom.y - doorTop.y
      );

      const labelText = "Door Module";
      if (isFocused) {
        ctx.fillStyle = "#f59e0b";
        ctx.font = "bold 9px sans-serif";
      } else if (isHovered) {
        ctx.fillStyle = "#f8fafc";
        ctx.font = "bold 9px sans-serif";
      } else {
        ctx.fillStyle = "#94a3b8";
        ctx.font = "9px sans-serif";
      }
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
      color = "#f59e0b"; // amber-500 for old man
    } else if (type === "character") {
      color = "#f43f5e"; // rose-500
    } else if (type === "object" || type === "item") {
      color = "#06b6d4"; // cyan-500
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
    
    if (isFocused) {
      ctx.fillStyle = "#f59e0b";
      ctx.font = "bold 9px sans-serif";
    } else if (isHovered) {
      ctx.fillStyle = "#f8fafc";
      ctx.font = "bold 9px sans-serif";
    } else {
      ctx.fillStyle = "#94a3b8";
      ctx.font = "9px sans-serif";
    }
    
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

window.addEventListener("resize", drawMap);

(function() {
  const canvas = document.getElementById("mapCanvas");
  if (!canvas) return;
  
  let isDragging = false;
  let startMouse = { x: 0, y: 0 };
  let startPan = { x: 0, y: 0 };
  let draggedDistance = 0;
  
  function getSubjectUnderMouse(clientX, clientY) {
    const rect = canvas.getBoundingClientRect();
    const clickX = clientX - rect.left;
    const clickY = clientY - rect.top;
    
    const params = getMapViewParams();
    if (!params) return null;
    
    const ctx = canvas.getContext("2d");
    ctx.save();
    ctx.font = "9px sans-serif";
    
    let found = null;
    for (const s of params.entitiesToDraw) {
      const coords = getSubjectCoord(s.name);
      const canvasPos = params.toCanvas(coords);
      
      if (s.name.toLowerCase() === "door") {
        const doorTopY = canvasPos.y - 18 * params.scale;
        const doorBottomY = canvasPos.y + 18 * params.scale;
        if (Math.abs(clickX - canvasPos.x) <= 6 && clickY >= doorTopY && clickY <= doorBottomY) {
          found = s.name;
          break;
        }
      } else {
        const dist = Math.sqrt((clickX - canvasPos.x) ** 2 + (clickY - canvasPos.y) ** 2);
        if (dist <= 15) {
          found = s.name;
          break;
        }
      }
      
      let labelText = s.name.split(" ").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
      if (s.name.toLowerCase() === "door") {
        labelText = "Door Module";
      }
      const textWidth = ctx.measureText(labelText).width;
      const textLeft = canvasPos.x + 7;
      const textRight = textLeft + textWidth;
      const textTop = canvasPos.y - 10;
      const textBottom = canvasPos.y + 6;
      
      if (clickX >= textLeft && clickX <= textRight && clickY >= textTop && clickY <= textBottom) {
        found = s.name;
        break;
      }
    }
    
    ctx.restore();
    return found;
  }
  
  canvas.addEventListener("mousedown", (e) => {
    isDragging = true;
    startMouse = { x: e.clientX, y: e.clientY };
    startPan = { ...mapPan };
    draggedDistance = 0;
    canvas.style.cursor = "grabbing";
  });
  
  canvas.addEventListener("mousemove", (e) => {
    if (isDragging) {
      const dxPx = e.clientX - startMouse.x;
      const dyPx = e.clientY - startMouse.y;
      draggedDistance += Math.sqrt(dxPx * dxPx + dyPx * dyPx);
      
      const params = getMapViewParams();
      if (params) {
        mapPan.x = startPan.x - dxPx / params.scale;
        mapPan.y = startPan.y + dyPx / params.scale;
        drawMap();
      }
    } else {
      const subject = getSubjectUnderMouse(e.clientX, e.clientY);
      if (subject !== hoveredSubject) {
        hoveredSubject = subject;
        drawMap();
      }
      canvas.style.cursor = hoveredSubject ? "pointer" : "default";
    }
  });
  
  window.addEventListener("mouseup", () => {
    if (isDragging) {
      isDragging = false;
      canvas.style.cursor = hoveredSubject ? "pointer" : "default";
    }
  });
  
  canvas.addEventListener("click", (e) => {
    if (draggedDistance > 5) return;
    const subject = getSubjectUnderMouse(e.clientX, e.clientY);
    if (subject) {
      lastTargetSubject = subject;
      saveMapPositions();
      drawMap();
    }
  });
  
  canvas.addEventListener("wheel", (e) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 0.9 : 1.1;
    const oldRadius = mapViewportRadiusInches;
    mapViewportRadiusInches = Math.max(36, Math.min(480, mapViewportRadiusInches * zoomFactor));
    if (mapViewportRadiusInches !== oldRadius) {
      drawMap();
    }
  }, { passive: false });
})();
