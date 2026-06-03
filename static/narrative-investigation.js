// Sequential dynamic script loader for narrative-investigation client submodules
// Ensures backward compatibility and strict compliance with maximum file lengths
(function() {
  const submodules = [
    '/static/narrative-investigation-api.js',
    '/static/narrative-investigation-ui.js'
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