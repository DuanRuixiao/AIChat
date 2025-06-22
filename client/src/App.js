import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [socket, setSocket] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Create WebSocket connection
    const ws = new WebSocket('ws://localhost:3001/ws');
    
    ws.onopen = () => {
      setIsConnected(true);
      console.log('Connected to server');
    };

    ws.onclose = () => {
      setIsConnected(false);
      console.log('Disconnected from server');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        switch (data.type) {
          case 'receiveMessage':
            setMessages(prev => [...prev, {
              id: Date.now(),
              text: data.message,
              sender: 'ai',
              timestamp: new Date().toLocaleTimeString()
            }]);
            break;
            
          case 'typing':
            setIsTyping(data.isTyping);
            break;
            
          case 'error':
            setMessages(prev => [...prev, {
              id: Date.now(),
              text: data.message,
              sender: 'error',
              timestamp: new Date().toLocaleTimeString()
            }]);
            break;
            
          default:
            console.log('Unknown message type:', data.type);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    setSocket(ws);

    // Cleanup on unmount
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  const sendMessage = (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || !isConnected || !socket) return;

    const newMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, newMessage]);
    
    // Send message to Python backend
    socket.send(JSON.stringify({
      message: inputMessage,
      conversationId: Date.now()
    }));

    setInputMessage('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      sendMessage(e);
    }
  };

  return (
    <div className="app">
      <div className="chat-container">
        <div className="chat-header">
          <div className="header-content">
            <Bot className="header-icon" />
            <div className="header-text">
              <h1>AI Agent</h1>
              <p>Your intelligent conversation partner</p>
            </div>
          </div>
          <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
          </div>
        </div>

        <div className="messages-container">
          {messages.length === 0 && (
            <div className="welcome-message">
              <Bot className="welcome-icon" />
              <h2>Welcome to AI Agent!</h2>
              <p>I'm here to help you with any questions or tasks. What would you like to know?</p>
            </div>
          )}
          
          {messages.map((message) => (
            <div key={message.id} className={`message ${message.sender}`}>
              <div className="message-avatar">
                {message.sender === 'user' ? <User size={20} /> : <Bot size={20} />}
              </div>
              <div className="message-content">
                <div className="message-text">{message.text}</div>
                <div className="message-timestamp">{message.timestamp}</div>
              </div>
            </div>
          ))}
          
          {isTyping && (
            <div className="message ai">
              <div className="message-avatar">
                <Bot size={20} />
              </div>
              <div className="message-content">
                <div className="typing-indicator">
                  <Loader2 className="typing-spinner" />
                  <span>AI is typing...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <form className="input-container" onSubmit={sendMessage}>
          <div className="input-wrapper">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message here..."
              disabled={!isConnected}
              rows="1"
            />
            <button 
              type="submit" 
              disabled={!inputMessage.trim() || !isConnected || isTyping}
              className="send-button"
            >
              <Send size={20} />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default App; 