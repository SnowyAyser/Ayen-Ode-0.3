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
  clearToken();
  window.location.href = "/";
}
