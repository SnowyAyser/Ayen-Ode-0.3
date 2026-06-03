function linkifyDOMTextNodes(node) {
  if (node.nodeType === Node.TEXT_NODE) {
    const text = node.nodeValue;
    if (!text) return;

    // Build unified candidates list
    const completed = (currentEntities || []).map(e => ({ name: e.name, type: 'completed', entity: e }));
    
    const active = Object.values(activeInvestigations || {})
      .filter(inv => inv.status === 'queued' || inv.status === 'processing')
      .map(inv => ({ name: inv.itemName, type: 'active', inv }));
      
    const available = Array.from(document.querySelectorAll('.investigate-btn'))
      .filter(el => el.getAttribute('data-investigating') !== 'true')
      .map(el => ({
        name: el.getAttribute('data-inv-item'),
        type: 'available',
        entityType: el.getAttribute('data-inv-type') || 'object',
        cost: parseInt(el.getAttribute('data-inv-cost') || '1')
      }))
      .filter(c => c.name);

    const candidateMap = new Map();
    available.forEach(c => candidateMap.set(c.name.toLowerCase(), c));
    active.forEach(c => candidateMap.set(c.name.toLowerCase(), c));
    completed.forEach(c => candidateMap.set(c.name.toLowerCase(), c));

    const candidates = Array.from(candidateMap.values())
      .filter(c => c.name && c.name.length >= 2)
      .sort((a, b) => b.name.length - a.name.length);

    if (!candidates.length) return;

    const matches = [];
    candidates.forEach(candidate => {
      const escaped = candidate.name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const base = escaped.endsWith('s') ? (escaped.endsWith('es') ? escaped.slice(0, -2) + '(es)?' : escaped.slice(0, -1) + 's?') : escaped;
      
      let regex;
      if (candidate.name.includes(' ')) {
        regex = new RegExp(`\\b${base}(s|es)?\\b`, 'gi');
      } else {
        const capitalized = base.charAt(0).toUpperCase() + base.slice(1);
        regex = new RegExp(`\\b${capitalized}(s|es)?\\b`, 'g');
      }
      let m;
      while ((m = regex.exec(text)) !== null) {
        matches.push({ start: m.index, end: m.index + m[0].length, candidate, matched: m[0] });
      }
    });
    if (!matches.length) return;

    // Sort matches by length descending so longer matching phrases are kept first
    matches.sort((a, b) => {
      const lenA = a.end - a.start;
      const lenB = b.end - b.start;
      if (lenA !== lenB) return lenB - lenA;
      return a.start - b.start;
    });

    const noOverlap = [];
    for (const m of matches) {
      const overlaps = noOverlap.some(selected => !(m.end <= selected.start || m.start >= selected.end));
      if (!overlaps) noOverlap.push(m);
    }
    noOverlap.sort((a, b) => a.start - b.start);

    const fragment = document.createDocumentFragment();
    let pos = 0;
    for (const m of noOverlap) {
      if (m.start > pos) {
        fragment.appendChild(document.createTextNode(text.slice(pos, m.start)));
      }
      
      let btn;
      if (m.candidate.type === 'completed') {
        btn = document.createElement('button');
        btn.className = "text-slate-300 hover:text-emerald-400 underline decoration-dotted decoration-emerald-500 underline-offset-2 transition-colors text-[inherit] leading-[inherit] investigated-btn";
        const ename = m.candidate.entity.name.replace(/'/g, "\\'");
        btn.setAttribute('onclick', `openInvestigatedEntity('${ename}')`);
        btn.textContent = m.matched;
      } else if (m.candidate.type === 'active') {
        const inv = m.candidate.inv;
        btn = _htmlToElement(investigatingBtnHtml(inv.itemName, inv.entityType, inv.cost || 1, m.matched));
      } else {
        const c = m.candidate;
        btn = _htmlToElement(investigateBtnHtml(c.name, c.entityType, c.cost, m.matched));
      }
      
      fragment.appendChild(btn);
      pos = m.end;
    }
    if (pos < text.length) {
      fragment.appendChild(document.createTextNode(text.slice(pos)));
    }

    node.parentNode.replaceChild(fragment, node);
    return;
  }

  const skipTags = ['BUTTON', 'A', 'SCRIPT', 'STYLE', 'TEXTAREA', 'INPUT'];
  if (node.nodeType === Node.ELEMENT_NODE && skipTags.includes(node.tagName)) {
    return;
  }

  const children = Array.from(node.childNodes);
  for (const child of children) {
    linkifyDOMTextNodes(child);
  }
}

function _makeNarrativeBlock(content, stageReports = null) {
  const parsed = parseInvestigateText(content);
  const html = parsed.text.split('\n').map(p => p.trim()).filter(p => p).map(p => `<p>${p}</p>`).join('');
  const div = document.createElement('div');
  div.className = 'narrative-block text-slate-200 leading-7 space-y-3 relative group';
  div.innerHTML = html;
  linkifyDOMTextNodes(div);

  if (stageReports && (stageReports.theme_report || stageReports.quest_report || stageReports.mechanics_report)) {
    const inspectBtn = document.createElement('button');
    inspectBtn.className = 'mt-3 text-[10px] text-amber-500/40 hover:text-amber-400 font-mono tracking-wider bg-amber-950/10 border border-amber-900/20 hover:border-amber-700/50 rounded px-2 py-0.5 transition-all block cursor-pointer select-none';
    inspectBtn.textContent = '[Inspect AI Tiers]';
    inspectBtn.onclick = () => showAISplashModal(stageReports);
    div.appendChild(inspectBtn);
  }

  return div;
}

function showAISplashModal(reports) {
  if (!reports) return;
  const existing = document.getElementById('aiInspectModal');
  if (existing) existing.remove();

  const modal = document.createElement('div');
  modal.id = 'aiInspectModal';
  modal.className = 'fixed inset-0 z-50 bg-slate-950/90 backdrop-blur-md flex items-center justify-center p-4 md:p-8';
  
  const formatJSON = (obj) => {
    if (!obj) return 'Not available';
    try {
      return JSON.stringify(obj, null, 2);
    } catch(e) {
      return String(obj);
    }
  };

  const themeHtml = typeof reports.theme_report === 'object' ? formatJSON(reports.theme_report) : String(reports.theme_report || 'Not available');
  const questHtml = typeof reports.quest_report === 'object' ? formatJSON(reports.quest_report) : String(reports.quest_report || 'Not available');
  const mechHtml = typeof reports.mechanics_report === 'object' ? formatJSON(reports.mechanics_report) : String(reports.mechanics_report || 'Not available');

  modal.innerHTML = `
    <div class="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-4xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
      <!-- Modal Header -->
      <div class="px-6 py-4 border-b border-slate-800 flex justify-between items-center bg-slate-950/40">
        <div>
          <h3 class="text-xs font-bold text-amber-500 font-mono tracking-wider uppercase">AI Multi-Tier Pipeline Auditor</h3>
          <p class="text-[10px] text-slate-500 font-mono mt-0.5">Inspect intermediate reasoning stages & database tools evidence</p>
        </div>
        <button onclick="document.getElementById('aiInspectModal').remove()" class="text-slate-400 hover:text-slate-100 text-2xl font-bold leading-none p-2 rounded-lg hover:bg-slate-800 transition-colors cursor-pointer">&times;</button>
      </div>
      
      <!-- Modal Body -->
      <div class="p-6 overflow-y-auto space-y-6 flex-1 custom-scrollbar">
        <!-- Tier 1 -->
        <div class="space-y-2">
          <div class="flex items-center gap-2">
            <span class="bg-amber-950/40 text-amber-400 border border-amber-900/40 text-[10px] font-mono font-bold px-2 py-0.5 rounded">Tier 1</span>
            <h4 class="text-xs font-bold text-slate-300 font-mono uppercase tracking-wider">Theme & Tone Analyzer</h4>
          </div>
          <pre class="bg-slate-950 border border-slate-800/80 rounded-xl p-4 text-[11px] text-amber-500/90 font-mono overflow-x-auto leading-relaxed max-h-48 select-text">${escapeHtml(themeHtml)}</pre>
        </div>

        <!-- Tier 2 -->
        <div class="space-y-2">
          <div class="flex items-center gap-2">
            <span class="bg-amber-950/40 text-amber-400 border border-amber-900/40 text-[10px] font-mono font-bold px-2 py-0.5 rounded">Tier 2</span>
            <h4 class="text-xs font-bold text-slate-300 font-mono uppercase tracking-wider">Quest & Debt Progress Evaluator</h4>
          </div>
          <pre class="bg-slate-950 border border-slate-800/80 rounded-xl p-4 text-[11px] text-amber-500/90 font-mono overflow-x-auto leading-relaxed max-h-48 select-text">${escapeHtml(questHtml)}</pre>
        </div>

        <!-- Tier 3 -->
        <div class="space-y-2">
          <div class="flex items-center gap-2">
            <span class="bg-amber-950/40 text-amber-400 border border-amber-900/40 text-[10px] font-mono font-bold px-2 py-0.5 rounded">Tier 3</span>
            <h4 class="text-xs font-bold text-slate-300 font-mono uppercase tracking-wider">Mechanical & Database Tool Planner</h4>
          </div>
          <pre class="bg-slate-950 border border-slate-800/80 rounded-xl p-4 text-[11px] text-amber-500/90 font-mono overflow-x-auto leading-relaxed max-h-48 select-text">${escapeHtml(mechHtml)}</pre>
        </div>
      </div>
      
      <!-- Modal Footer -->
      <div class="px-6 py-3 border-t border-slate-800 flex justify-end bg-slate-950/40">
        <button onclick="document.getElementById('aiInspectModal').remove()" class="bg-slate-850 hover:bg-slate-800 text-slate-200 border border-slate-700/50 font-mono font-semibold py-1.5 px-4 rounded-lg text-xs transition-colors cursor-pointer">Close Auditor</button>
      </div>
    </div>
  `;

  document.body.appendChild(modal);
}

function inspectInvestigationStages(jobId) {
  const inv = activeInvestigations[jobId];
  if (inv && inv.result) {
    showAISplashModal({
      theme_report: inv.result.theme_report,
      quest_report: inv.result.quest_report,
      mechanics_report: inv.result.mechanics_report
    });
  }
}

function _makeUserBlock(content) {
  const div = document.createElement('div');
  div.className = 'border-l-2 border-blue-600/50 pl-4 py-2 bg-blue-950/10 rounded-r-lg';
  div.innerHTML = `<p class="text-blue-500 text-xs font-semibold uppercase tracking-widest mb-1">You</p><p class="text-slate-300 italic">${escapeHtml(content)}</p>`;
  return div;
}

function renderHistoryToPage(history) {
  const narrativeDiv = document.getElementById("narrativeContent");
  historyRenderOffset = Math.max(0, history.length - HISTORY_PAGE);
  for (let i = historyRenderOffset; i < history.length; i++) {
    const msg = history[i];
    if (msg.role === 'assistant') narrativeDiv.appendChild(_makeNarrativeBlock(msg.content));
    else if (msg.role === 'user') narrativeDiv.appendChild(_makeUserBlock(msg.content));
  }
  if (!historyScrollListenerAttached) {
    historyScrollListenerAttached = true;
    narrativeDiv.addEventListener('scroll', function () {
      if (narrativeDiv.scrollTop < 20 && historyRenderOffset > 0) {
        const newOffset = Math.max(0, historyRenderOffset - HISTORY_PAGE);
        const slice = conversationHistory.slice(newOffset, historyRenderOffset);
        const prevHeight = narrativeDiv.scrollHeight;
        const insertRef = narrativeDiv.firstChild;
        for (let i = 0; i < slice.length; i++) {
          const msg = slice[i];
          if (msg.role === 'assistant') narrativeDiv.insertBefore(_makeNarrativeBlock(msg.content), insertRef);
          else if (msg.role === 'user') narrativeDiv.insertBefore(_makeUserBlock(msg.content), insertRef);
        }
        narrativeDiv.scrollTop += narrativeDiv.scrollHeight - prevHeight;
        historyRenderOffset = newOffset;
      }
    }, { passive: true });
  }
}

// Staggered stagger-fade effects for opening scene intro reveal
const _entryParams = new URLSearchParams(window.location.search);
const _isFreshEntry = _entryParams.get('fresh') === '1' || sessionStorage.getItem('worldEntering') === '1';
const _isReplayIntro = _entryParams.get('replay_intro') === '1' || sessionStorage.getItem('replayIntro') === '1';
sessionStorage.removeItem('worldEntering');
sessionStorage.removeItem('replayIntro');

let _introSkipRequested = false;

function _splitIntoLines(text) {
  return text.split('\n').map(s => s.trim()).filter(Boolean);
}

function _showReplayBadge() {
  const b = document.createElement('div');
  b.id = 'introReplayBadge';
  b.textContent = 'Replay';
  document.body.appendChild(b);
  setTimeout(() => b.remove(), 4000);
}

function _showSkipButton(onSkip) {
  const btn = document.createElement('button');
  btn.id = 'introSkipBtn';
  btn.textContent = 'Skip ›';
  btn.onclick = () => { _introSkipRequested = true; btn.remove(); onSkip(); };
  document.body.appendChild(btn);
  return btn;
}

function _sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function playOpeningSceneIntro(handoffText) {
  const parsed = parseInvestigateText(handoffText);
  const lines = _splitIntoLines(parsed.text);
  const narrativeDiv = document.getElementById('narrativeContent');
  narrativeDiv.innerHTML = `<div class="narrative-block text-slate-200 leading-7 space-y-3" id="introBlock"></div>`;
  const block = document.getElementById('introBlock');

  if (lines.length === 0) return;

  block.innerHTML = lines.map(l => `<p>${l}</p>`).join('');
  linkifyDOMTextNodes(block);
}
