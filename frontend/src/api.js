const BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

export async function sendMessage(query) {
  const res = await fetch(`${BASE_URL}/api/chat/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Server error ${res.status}`);
  }
  return res.json(); // { query, answer }
}

export async function uploadPDF(file) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${BASE_URL}/api/upload/`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Upload error ${res.status}`);
  }
  return res.json(); // { status, filename, chunks_ingested }
}

export async function checkHealth() {
  const res = await fetch(`${BASE_URL}/api/health/`);
  return res.ok;
}
