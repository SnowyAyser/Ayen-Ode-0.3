function getToken() {
  return localStorage.getItem("apiKey");
}

function setToken(token) {
  localStorage.setItem("apiKey", token);
}

function clearToken() {
  localStorage.removeItem("apiKey");
}

function hasToken() {
  return !!getToken();
}

function checkAuth() {
  if (!hasToken()) {
    window.location.href = "/";
  }
}

function unwrapJsonRpcResponse(response) {
  if (response && response.jsonrpc === "2.0" && response.result) {
    return response.result;
  }
  return response;
}

async function apiCall(endpoint, method = "GET", body = null) {
  const token = getToken();
  if (!token) {
    checkAuth();
    return;
  }

  const options = {
    method,
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(endpoint, options);
  if (response.status === 401) {
    clearToken();
    window.location.href = "/";
    return null;
  }

  const data = await response.json();
  return unwrapJsonRpcResponse(data);
}

async function logout() {
  const token = getToken();
  if (token) {
    await fetch("/api/logout", {
      method: "POST",
      headers: { "Authorization": `Bearer ${token}` },
    }).catch(() => {});
  }
  if (window.pywebview && window.pywebview.api && typeof window.pywebview.api.save_auto_login === "function") {
    try { await window.pywebview.api.save_auto_login(false); } catch (e) {}
  }
  localStorage.removeItem('autoLogin');
  clearToken();
  window.location.href = "/";
}

// F11 fullscreen — works from any page that includes app.js.
// In pywebview we route through the JS-Python bridge (which toggles the
// native window). In a regular browser we fall back to the standard
// Fullscreen API so the same key still works.
document.addEventListener("keydown", (e) => {
  if (e.key !== "F11") return;
  e.preventDefault();
  if (window.pywebview && window.pywebview.api && typeof window.pywebview.api.toggle_fullscreen === "function") {
    try { window.pywebview.api.toggle_fullscreen(); } catch (err) {}
  } else if (document.fullscreenElement) {
    document.exitFullscreen();
  } else {
    document.documentElement.requestFullscreen?.();
  }
});

window.onerror = function(message, source, lineno, colno, error) {
  const token = localStorage.getItem("apiKey");
  fetch('/api/logs/error', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      message: message || "Unknown",
      source: source || "unknown",
      lineno: lineno || 0,
      colno: colno || 0,
      stack: error ? error.stack : ""
    })
  }).catch(() => {});
};
