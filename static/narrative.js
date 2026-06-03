// Sequential dynamic script loader for narrative client submodules
// Ensures backward compatibility and strict compliance with maximum file lengths
(function() {
  const submodules = [
    '/static/narrative-core.js',
    '/static/narrative-dom.js',
    '/static/narrative-bootstrap.js',
    '/static/narrative-compendium.js',
    '/static/narrative-map-data.js',
    '/static/narrative-map-render.js',
    '/static/narrative-map-controls.js',
    '/static/narrative-modal.js',
    '/static/narrative-actions.js',
    '/static/narrative-settings.js'
  ];

  function loadModule(index) {
    if (index >= submodules.length) {
      if (typeof bootstrapNarrativeWorld === 'function') {
        bootstrapNarrativeWorld();
      }
      return;
    }
    const script = document.createElement('script');
    script.src = submodules[index];
    script.async = false;
    script.onload = () => loadModule(index + 1);
    document.body.appendChild(script);
  }

  loadModule(0);
})();