// components/AcademicChatbot/AcademicChatbot.tsx
'use client';
import React from 'react';
import { useChat } from '@/hooks/useChat';
import ChatMessages from './ChatMessages';
import Sidebar from './Sidebar';
import ChatInput from './ChatInput';
import Header from './Header';

const AcademicChatbot = () => {
  const chat = useChat();

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Header />
      <div className="flex-1 flex max-w-6xl mx-auto w-full">
        <Sidebar {...chat} />
        <div className="flex-1 flex flex-col">
          <ChatMessages
            messages={chat.messages}
            isTyping={chat.isTyping}
            messagesEndRef={chat.messagesEndRef}
          />
          <ChatInput {...chat} />
        </div>
      </div>
    </div>
  );
};

export default AcademicChatbot;
