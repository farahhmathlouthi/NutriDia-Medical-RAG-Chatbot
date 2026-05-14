import React, { useState, useCallback } from 'react';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';
import ChatInput from './components/ChatInput';
import { sendMessage } from './api';
import './App.css';

let msgId = 0;

export default function App() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const addMessage = (role, content, extra = {}) => {
    const msg = { id: ++msgId, role, content, ...extra };
    setMessages((prev) => [...prev, msg]);
    return msg.id;
  };

  const handleSend = useCallback(async (query) => {
    if (isLoading) return;

    addMessage('user', query);
    setIsLoading(true);

    try {
      const data = await sendMessage(query);
      addMessage('bot', data.answer);
    } catch (err) {
      addMessage('error', `Error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading]);

  return (
    <div className="app-layout">
      <Sidebar onSuggest={handleSend} disabled={isLoading} />
      <div className="chat-area">
        <header className="chat-header">
          <div className="header-title">
            <span className="header-badge">AI</span>
            Diabetes & Nutrition Assistant
          </div>
          <div className="header-status">
            <span className="status-dot" />
            Connected
          </div>
        </header>
        <ChatWindow messages={messages} isLoading={isLoading} />
        <ChatInput onSend={handleSend} isLoading={isLoading} />
      </div>
    </div>
  );
}
