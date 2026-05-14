import React, { useState } from 'react';
import { Send, Loader } from 'lucide-react';
import './ChatInput.css';

export default function ChatInput({ onSend, isLoading }) {
  const [value, setValue] = useState('');

  function handleSubmit(e) {
    e.preventDefault();
    const q = value.trim();
    if (!q || isLoading) return;
    onSend(q);
    setValue('');
  }

  function handleKey(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      handleSubmit(e);
    }
  }

  return (
    <div className="input-bar-wrapper">
      <form className="input-bar" onSubmit={handleSubmit}>
        <textarea
          className="input-textarea"
          placeholder="Ask about diabetes, nutrition, diet plans…"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKey}
          rows={1}
          disabled={isLoading}
        />
        <button
          className="send-btn"
          type="submit"
          disabled={!value.trim() || isLoading}
          aria-label="Send"
        >
          {isLoading
            ? <Loader size={18} className="spin" />
            : <Send size={18} />}
        </button>
      </form>
      <p className="input-hint">Press Enter to send · Shift+Enter for new line</p>
    </div>
  );
}
