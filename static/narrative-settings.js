// Settings popover
(function () {
  const btn = document.getElementById('settingsBtn');
  const popover = document.getElementById('settingsPopover');
  const toggle = document.getElementById('confirmToggle');
  console.log("[SettingsPopover] Elements found:", { btn, popover, toggle });
  if (!btn || !popover || !toggle) {
    console.warn("[SettingsPopover] Initialization failed: missing element!");
    return;
  }

  function syncToggle() {
    const on = !!getSettings().confirmBeforeSend;
    toggle.setAttribute('data-on', on ? '1' : '0');
    toggle.className = on
      ? 'relative inline-flex h-5 w-9 items-center rounded-full bg-amber-600 transition-colors focus:outline-none flex-none'
      : 'relative inline-flex h-5 w-9 items-center rounded-full bg-slate-600 transition-colors focus:outline-none flex-none';
    toggle.innerHTML = `<span class="inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform ${on ? 'translate-x-4' : 'translate-x-1'}"></span>`;
  }
  syncToggle();

  btn.addEventListener('click', (e) => {
    console.log("[SettingsPopover] Click registered!");
    e.stopPropagation();
    popover.classList.toggle('hidden');
    syncToggle();
  });

  toggle.addEventListener('click', () => {
    const current = !!getSettings().confirmBeforeSend;
    updateSettings({ confirmBeforeSend: !current });
    if (!current === false) _cancelPendingConfirm();
    syncToggle();
  });

  document.addEventListener('click', (e) => {
    if (!popover.classList.contains('hidden') && !popover.contains(e.target) && e.target !== btn) {
      popover.classList.add('hidden');
    }
  });
})();

function showSkipPicker() {
  document.getElementById('skipPickerPopover')?.classList.remove('hidden');
}

function cancelSkipPicker() {
  document.getElementById('skipPickerPopover')?.classList.add('hidden');
}

async function doSkipTime(seconds) {
  if (!currentWorldId) return;
  cancelSkipPicker();
  try {
    const resp = await fetch(`/api/worlds/${currentWorldId}/skip-time`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${getToken()}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ seconds }),
    });
    const data = await resp.json();
    if (!resp.ok) {
      const blocking = data.blocking || {};
      const jobNames = (blocking.investigation || []).map(j => j.name).join(', ');
      const msg = jobNames ? `Active: ${jobNames}` : (data.error || 'Cannot skip time');
      const lbl = document.getElementById('gameTimeLabel');
      if (lbl) {
        const saved = lbl.textContent;
        lbl.textContent = `⚠ ${msg}`;
        lbl.classList.add('text-amber-500', 'text-right');
        setTimeout(() => { lbl.textContent = saved; lbl.classList.remove('text-amber-500', 'text-right'); }, 3500);
      }
      return;
    }
    if (data.game_time) updateTimeDisplay(data.game_time);
  } catch (_) {}
}

// Close skip picker on outside click
document.addEventListener('click', (e) => {
  const pop = document.getElementById('skipPickerPopover');
  const btn = document.getElementById('skipTimeBtn');
  if (pop && !pop.classList.contains('hidden') && !pop.contains(e.target) && e.target !== btn) {
    pop.classList.add('hidden');
  }
});

// Textarea: auto-resize, char count, draft, history navigation
(function () {
  const el = document.getElementById('actionInput');
  if (!el) return;

  autoResizeTextarea(el);

  el.addEventListener('input', () => {
    autoResizeTextarea(el);
    updateCharCount(el);
    saveDraft();
    document.getElementById("noMovementError")?.classList.add("hidden");
  });

  el.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      document.getElementById('actionForm').requestSubmit();
    } else if (e.key === 'Escape' && pendingConfirm) {
      e.preventDefault();
      _cancelPendingConfirm();
    } else if (e.key === 'PageUp') {
      const chat = document.getElementById('narrativeContent');
      if (chat) {
        e.preventDefault();
        chat.scrollBy({ top: -chat.clientHeight * 0.8, behavior: 'smooth' });
      }
    } else if (e.key === 'PageDown') {
      const chat = document.getElementById('narrativeContent');
      if (chat) {
        e.preventDefault();
        chat.scrollBy({ top: chat.clientHeight * 0.8, behavior: 'smooth' });
      }
    }
  });
})();

// Keyboard scrolling shortcuts when page body/main action input is active
document.addEventListener('keydown', (e) => {
  const active = document.activeElement;
  if (active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA') && active.id !== 'actionInput') {
    return;
  }
  
  if (e.key === 'PageUp' || e.key === 'PageDown' || e.key === 'ArrowUp' || e.key === 'ArrowDown') {
    const chat = document.getElementById('narrativeContent');
    if (!chat) return;
    
    // Let standard caret movement happen inside textarea for arrows
    if (active && active.id === 'actionInput' && (e.key === 'ArrowUp' || e.key === 'ArrowDown')) {
      return;
    }
    
    e.preventDefault();
    let scrollAmount = 0;
    if (e.key === 'PageUp') scrollAmount = -chat.clientHeight * 0.8;
    else if (e.key === 'PageDown') scrollAmount = chat.clientHeight * 0.8;
    else if (e.key === 'ArrowUp') scrollAmount = -60;
    else if (e.key === 'ArrowDown') scrollAmount = 60;
    
    chat.scrollBy({ top: scrollAmount, behavior: 'smooth' });
  }
});

