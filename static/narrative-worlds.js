// World switcher modal

function showWorldList() {
  document.getElementById("worldsModal").classList.remove("hidden");
  loadWorldsList();
}

function closeWorldsModal() {
  document.getElementById("worldsModal").classList.add("hidden");
}

async function loadWorldsList() {
  try {
    const worlds = await apiCall("/api/worlds");
    if (!worlds || !worlds.worlds) {
      document.getElementById("worldsList").innerHTML =
        '<p class="text-slate-500">No worlds found</p>';
      return;
    }

    const html = worlds.worlds.map(w => `
      <div class="p-3 border border-slate-700/60 rounded-lg hover:bg-slate-800 transition-colors">
        <div class="font-medium text-slate-100 mb-1">${w.name}</div>
        <p class="text-sm text-slate-500 mb-3">${(w.premise || '').substring(0, 70)}…</p>
        ${w.status !== 'active' ? `
          <button onclick="switchToWorld('${w.world_id}')" class="w-full bg-amber-800 hover:bg-amber-700 border border-amber-700/50 text-sm py-1.5 rounded-md transition-colors text-amber-100 font-medium">
            Enter
          </button>
        ` : '<div class="text-center text-xs text-emerald-400 font-semibold bg-emerald-950/40 border border-emerald-800/30 py-1.5 rounded-md">Currently Playing</div>'}
      </div>
    `).join('');

    document.getElementById("worldsList").innerHTML = html;
  } catch (error) {
    console.error("Error loading worlds:", error);
  }
}

async function switchToWorld(worldId) {
  try {
    await apiCall("/api/worlds/switch", "POST", { world_id: worldId });
    currentWorldId = worldId;
    closeWorldsModal();
    loadWorld();
  } catch (error) {
    console.error("Error switching world:", error);
  }
}
