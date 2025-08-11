// components/AcademicChatbot/AcademicChatbot.tsx
'use client';
import React from 'react';
import { useChat } from '@/hooks/useChat';
import ChatMessages from './ChatMessages';
import FileUploader from './FileUploader';
import UploadedFiles from './UploadedFiles';
import SuggestedQuestions from './SuggestedQuestions';
import ChatInput from './ChatInput';
import Header from './Header';

const AcademicChatbot = () => {
  const chat = useChat();

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Header />
      <div className="flex-1 flex max-w-6xl mx-auto w-full">
        <div className="w-80 bg-white shadow-lg border-r border-gray-200 flex flex-col">
          <FileUploader {...chat} />
          <UploadedFiles {...chat} />
          <SuggestedQuestions {...chat} />
        </div>
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
