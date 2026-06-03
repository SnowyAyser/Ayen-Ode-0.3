// Narrative Client Module: Tactical Map Controls & Canvas Interaction
// Line limit compliance: Under 150 lines
window.addEventListener("resize", () => {
  if (typeof drawMap === "function") drawMap();
});

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
