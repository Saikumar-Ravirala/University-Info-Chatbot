
// components/AcademicChatbot/ChatInput.tsx
import React from 'react';
import { Send, Loader } from 'lucide-react';
import UploadMenu from './UploadMenu';

interface ChatInputProps {
  inputMessage: string;
  setInputMessage: (message: string) => void;
  handleSendMessage: () => void;
  isLoading: boolean;
  uploadedFiles: Array<{ name: string; id: string }>;
  handleFileUpload: (event: React.ChangeEvent<HTMLInputElement>) => void;
  handleUrlUpload: (url: string) => void;
}

const ChatInput: React.FC<ChatInputProps> = ({
  inputMessage,
  setInputMessage,
  handleSendMessage,
  isLoading,
  uploadedFiles,
  handleFileUpload,
  handleUrlUpload,
}) => (
  <div className="border-t border-gray-200 bg-white p-4 sticky bottom-0 z-10">
        <div className="flex items-center space-x-3">
            <UploadMenu 
        handleFileUpload={handleFileUpload}
        handleUrlUpload={handleUrlUpload} 
        isLoading={isLoading} 
      />
      <div className="flex-1 relative">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
          placeholder={uploadedFiles.length > 0 ? "Ask questions about your documents..." : "Upload a PDF first to start asking questions..."}
          disabled={isLoading || uploadedFiles.length === 0}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg bg-white text-black focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed"
        />
      </div>
      <button
        onClick={handleSendMessage}
        disabled={!inputMessage.trim() || isLoading || uploadedFiles.length === 0}
        className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg transition-colors flex items-center space-x-2 disabled:cursor-not-allowed"
      >
        {isLoading ? <Loader className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
      </button>
    </div>
    {uploadedFiles.length === 0 && (
      <p className="text-xs text-gray-500 mt-2">
        Get answers about admissions, programs, campus life, and more
      </p>
    )}
  </div>
);

export default ChatInput;
