import React, { useRef, useState } from 'react';
import { uploadPDF } from '../api';
import { Upload, FileText, CheckCircle, AlertCircle, Loader, Leaf } from 'lucide-react';
import './Sidebar.css';

const SUGGESTED = [
  "What foods should a diabetic avoid?",
  "How does insulin resistance develop?",
  "Best diet plan for type 2 diabetes?",
  "What is the glycemic index?",
  "How much sugar per day is safe?",
  "Signs of hypoglycemia to watch for?",
];

export default function Sidebar({ onSuggest, disabled }) {
  const fileRef = useRef();
  const [status, setStatus] = useState(null); // null | loading | success | error
  const [message, setMessage] = useState('');

  async function handleFile(e) {
    const file = e.target.files[0];
    if (!file) return;
    if (!file.name.endsWith('.pdf')) {
      setStatus('error');
      setMessage('Only PDF files are supported.');
      return;
    }
    setStatus('loading');
    setMessage(`Uploading ${file.name}…`);
    try {
      const data = await uploadPDF(file);
      setStatus('success');
      setMessage(`✔ ${data.filename} — ${data.chunks_ingested} chunks indexed`);
    } catch (err) {
      setStatus('error');
      setMessage(err.message);
    }
    fileRef.current.value = '';
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <Leaf size={22} className="logo-icon" />
        <span className="logo-text">NutriDia <em>AI</em></span>
      </div>

      <p className="sidebar-tagline">Your diabetes & nutrition assistant</p>

      {/* Upload */}
      <div className="upload-section">
        <p className="section-label">Upload Knowledge</p>
        <button
          className="upload-btn"
          onClick={() => fileRef.current.click()}
          disabled={status === 'loading'}
        >
          {status === 'loading'
            ? <Loader size={16} className="spin" />
            : <Upload size={16} />}
          Upload PDF
        </button>
        <input
          ref={fileRef}
          type="file"
          accept=".pdf"
          style={{ display: 'none' }}
          onChange={handleFile}
        />

        {status && (
          <div className={`upload-feedback ${status}`}>
            {status === 'loading' && <Loader size={13} className="spin" />}
            {status === 'success' && <CheckCircle size={13} />}
            {status === 'error' && <AlertCircle size={13} />}
            <span>{message}</span>
          </div>
        )}
      </div>

      {/* Suggestions */}
      <div className="suggestions-section">
        <p className="section-label">Try asking…</p>
        <ul className="suggestions-list">
          {SUGGESTED.map((q) => (
            <li key={q}>
              <button
                className="suggestion-btn"
                onClick={() => onSuggest(q)}
                disabled={disabled}
              >
                <FileText size={13} />
                {q}
              </button>
            </li>
          ))}
        </ul>
      </div>

      <div className="sidebar-footer">
        <p>Powered by Ollama · LangChain · ChromaDB</p>
      </div>
    </aside>
  );
}
