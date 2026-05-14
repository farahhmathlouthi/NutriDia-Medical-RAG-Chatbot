import React, { useEffect, useRef } from 'react';
import { Leaf, User, AlertCircle } from 'lucide-react';
import './ChatWindow.css';

function TypingDots() {
  return (
    <div className="typing-dots">
      <span /><span /><span />
    </div>
  );
}

function Message({ msg }) {
  const isUser = msg.role === 'user';
  const isError = msg.role === 'error';

  return (
    <div className={`message-row ${isUser ? 'user' : 'bot'}`}>
      <div className="avatar">
        {isUser
          ? <User size={16} />
          : isError
            ? <AlertCircle size={16} />
            : <Leaf size={16} />}
      </div>
      <div className={`bubble ${isError ? 'error-bubble' : ''}`}>
        {msg.typing
          ? <TypingDots />
          : <p>{msg.content}</p>}
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="empty-state">
      <div className="empty-icon">
        <Leaf size={36} />
      </div>
      <h2>How can I help you today?</h2>
      <p>Ask me anything about diabetes management, nutrition plans, or healthy eating habits. You can also upload a PDF to expand my knowledge.</p>
    </div>
  );
}

export default function ChatWindow({ messages, isLoading }) {
  const bottomRef = useRef();

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="chat-window">
      {messages.length === 0 && !isLoading
        ? <EmptyState />
        : (
          <div className="messages-list">
            {messages.map((msg) => (
              <Message key={msg.id} msg={msg} />
            ))}
            {isLoading && (
              <div className="message-row bot">
                <div className="avatar"><Leaf size={16} /></div>
                <div className="bubble"><TypingDots /></div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        )}
    </div>
  );
}
