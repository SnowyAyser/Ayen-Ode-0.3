// Sequential dynamic script loader for narrative client submodules
// Ensures backward compatibility and strict compliance with maximum file lengths
(function() {
  const submodules = [
    '/static/narrative-core.js',
    '/static/narrative-dom.js',
    '/static/narrative-actions.js',
    '/static/narrative-settings.js'
  ];

  function loadModule(index) {
    if (index >= submodules.length) return;
    const script = document.createElement('script');
    script.src = submodules[index];
    script.async = false;
    script.onload = () => loadModule(index + 1);
    document.body.appendChild(script);
  }

  loadModule(0);
})();