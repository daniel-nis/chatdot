import React from 'react';
import type { Message } from '../../types/chat';

interface MessageProps {
  message: Message;
}

const Message: React.FC<MessageProps> = ({ message }) => {
  const isUser = message.sender === 'user';
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 px-4`}>
      <div
        className={`
          max-w-[80%] py-2 px-3 rounded-md
          ${isUser ? 
            'bg-[#4b69ff] text-white' : 
            'bg-[#383c41] text-gray-200'
          }
        `}
      >
        <p className="text-sm break-words">
          {message.content}
        </p>
      </div>
    </div>
  );
};

export default Message;