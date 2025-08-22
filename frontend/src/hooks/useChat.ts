/* eslint-disable @typescript-eslint/no-explicit-any */

import { useState, useEffect, useRef } from 'react';
import { formatFileSize } from '@/utils/formatFileSize';

export const useChat = () => {
  // const API_BASE = process.env.NEXT_PUBLIC_API_URL;
  const API_BASE = "https://university-info-chatbot-cy9d.onrender.com";

  const [messages, setMessages] = useState<any[]>([{
    id: 1,
    text: "Hello! I'm your University Info Assistant...",
    sender: 'bot',
    timestamp: new Date()
  }]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<any[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([]);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef(null);

  // ✅ Generate session ID once per user
  const [sessionId] = useState(() => `session-${crypto.randomUUID()}`);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // ✅ Cleanup session on tab close
  useEffect(() => {
    const handleUnload = async () => {
      try {
        await fetch(`${API_BASE}/cleanup-session`, {
          method: "POST",
          body: JSON.stringify({ session_id: sessionId }),
          headers: { "Content-Type": "application/json" }
        });
      } catch (err) {
        console.warn("Session cleanup failed", err);
      }
    };

    window.addEventListener("beforeunload", handleUnload);
    return () => window.removeEventListener("beforeunload", handleUnload);
  }, [sessionId, API_BASE]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || uploadedFiles.length === 0) return;

    const startTime = Date.now();
    const userMessage = {
      id: messages.length + 1,
      text: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setIsTyping(true);

    const formData = new FormData();
    formData.append("query", inputMessage);
    formData.append("session_id", sessionId); // ✅ Pass session ID
    uploadedFiles.forEach((file) => {
      formData.append("files", file.rawFile);
    });

    try {
      const response = await fetch(`${API_BASE}/chat-stream`, {
        method: "POST",
        body: formData,
      });

      if (!response.body) throw new Error("No response stream");

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");

      let botText = '';
      const botMessage = {
        id: messages.length + 2,
        text: '',
        sender: 'bot',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });

        chunk.split('\n\n').forEach((msg) => {
          if (msg.startsWith("data: ")) {
            try {
              const parsed = JSON.parse(msg.slice(6));
              botText += parsed.chunk;
              const responseTime = Date.now() - startTime;
              setMessages(prev => prev.map(m => m.id === botMessage.id ? { ...m, text: botText, responseTime } : m));
            } catch (e) {
              console.error("Parse error", e);
            }
          }
        });
      }
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, {
        id: messages.length + 2,
        text: "Server error. Please try again.",
        sender: 'bot',
        timestamp: new Date()
      }]);
    }

    setIsLoading(false);
    setIsTyping(false);
  };

  const handleFileUpload = async (event: any) => {
    const files = Array.from(event.target.files) as File[];
    const pdfFiles = files.filter((file: File) => file.type === 'application/pdf');

    if (pdfFiles.length === 0) {
      alert('Only PDFs allowed');
      return;
    }

    const newFiles = pdfFiles.map((file: any) => ({
      id: Date.now() + Math.random(),
      name: file.name,
      size: file.size,
      uploadTime: new Date(),
      rawFile: file,
      status: 'uploading' as const
    }));

    setUploadedFiles(prev => [...prev, ...newFiles]);

    const uploadMessages = newFiles.map(file => ({
      id: Date.now() + Math.random(),
      text: `📄 Uploading: ${file.name}`,
      sender: 'bot',
      timestamp: new Date()
    }));
    setMessages(prev => [...prev, ...uploadMessages]);

    try {
      setUploadedFiles(prev => prev.map(file =>
        newFiles.some(newFile => newFile.id === file.id)
          ? { ...file, status: 'processing' as const }
          : file
      ));

      // ✅ Upload PDFs with session ID
      const uploadFormData = new FormData();
      uploadFormData.append("session_id", sessionId);
      pdfFiles.forEach((file: File) => uploadFormData.append("files", file));

      const uploadResponse = await fetch(`${API_BASE}/upload-pdfs`, {
        method: "POST",
        body: uploadFormData
      });

      if (uploadResponse.ok) {
        setUploadedFiles(prev => prev.map(file =>
          newFiles.some(newFile => newFile.id === file.id)
            ? { ...file, status: 'completed' as const }
            : file
        ));

        const completedMessages = newFiles.map(file => ({
          id: Date.now() + Math.random(),
          text: `✅ Ready: ${file.name}`,
          sender: 'bot',
          timestamp: new Date()
        }));
        setMessages(prev => [...prev, ...completedMessages]);
      } else {
        throw new Error('Upload failed');
      }

      // ✅ Request suggested questions with session ID
      const suggestFormData = new FormData();
      suggestFormData.append("session_id", sessionId);
      pdfFiles.forEach((file: File) => suggestFormData.append("files", file));

      const res = await fetch(`${API_BASE}/generate-suggested-questions`, {
        method: "POST",
        body: suggestFormData
      });

      const data = await res.json();
      if (data.questions) {
        setSuggestedQuestions(data.questions);
      }
    } catch (err) {
      console.error("Error uploading PDFs or generating suggested questions", err);

      setUploadedFiles(prev => prev.map(file =>
        newFiles.some(newFile => newFile.id === file.id)
          ? { ...file, status: 'error' as const }
          : file
      ));

      const errorMessages = newFiles.map(file => ({
        id: Date.now() + Math.random(),
        text: `❌ Error uploading: ${file.name}`,
        sender: 'bot',
        timestamp: new Date()
      }));
      setMessages(prev => [...prev, ...errorMessages]);
    }
  };

  const removeFile = (fileId: number) => {
    setUploadedFiles(prev => prev.filter(file => file.id !== fileId));
  };

  return {
    messages,
    inputMessage,
    setInputMessage,
    isLoading,
    handleSendMessage,
    handleFileUpload,
    uploadedFiles,
    setUploadedFiles,
    removeFile,
    formatFileSize,
    isTyping,
    messagesEndRef,
    fileInputRef,
    suggestedQuestions
  };
};

