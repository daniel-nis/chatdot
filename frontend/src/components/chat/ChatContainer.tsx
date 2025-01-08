import React, { useState, useEffect } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import { Message } from '../../types/chat';

const ChatContainer: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);

  useEffect(() => {
    const clientId = Date.now();
    const websocket = new WebSocket(`ws://localhost:8000/api/v1/ws/${clientId}`);

    websocket.onopen = () => {
      console.log('Connected to chat server');
    };

    websocket.onmessage = (event) => {
      const message: Message = {
        id: Date.now().toString(),
        content: event.data,
        sender: 'dot',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, message]);
      setIsLoading(false);
    };

    setWs(websocket);

    return () => {
      websocket.close();
    };
  }, []);

  const handleSendMessage = (content: string) => {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    const message: Message = {
      id: Date.now().toString(),
      content,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, message]);
    setIsLoading(true);
    ws.send(content);
  };

  return (
    <div className="min-h-screen bg-[#0B0F17] flex flex-col items-center pt-8">
      {/* Radial gradient for the glow effect */}
      <div className="absolute top-0 w-full h-[300px] bg-gradient-to-b from-[#1B1B1F] to-transparent opacity-50" />
      
      <div className="w-full max-w-3xl relative">
        {/* Container with glowing border effect */}
        <div className="relative rounded-lg overflow-hidden bg-[#13151A] border border-[#1F2128]">
          {/* Header */}
          <div className="p-4 border-b border-[#1F2128] bg-[#13151A]">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-[#1F2128]" />
              <div>
                <h1 className="text-lg font-medium text-gray-200">chat with dot</h1>
              </div>
            </div>
          </div>

          {/* Messages area */}
          <div className="h-[600px] overflow-auto">
            <MessageList 
              messages={messages}
              isLoading={isLoading}
            />
          </div>

          {/* Input area */}
          <MessageInput 
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
          />
        </div>
      </div>
    </div>
  );
};

export default ChatContainer;