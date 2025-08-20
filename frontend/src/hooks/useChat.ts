import { useState, useEffect, useRef } from 'react';
import { sendChatMessage } from '@/services/chatService'; // Adjust the import based on your project structure
import { formatFileSize } from '@/utils/formatFileSize'; // Adjust the import based on your project structure

export const useChat = () => {
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

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
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
  uploadedFiles.forEach((file) => {
    formData.append("files", file.rawFile);
  });

  try {
    const response = await fetch("http://localhost:8000/chat-stream", {
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

      // SSE format: data: {"chunk": "Some text"}\n\n
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

  // Update uploaded files in state with uploading status
  setUploadedFiles(prev => [...prev, ...newFiles]);

  // Show "uploaded" messages in chat
  const uploadMessages = newFiles.map(file => ({
    id: Date.now() + Math.random(),
    text: `📄 Uploading: ${file.name}`,
    sender: 'bot',
    timestamp: new Date()
  }));
  setMessages(prev => [...prev, ...uploadMessages]);

  try {
    // Update status to processing
    setUploadedFiles(prev => prev.map(file => 
      newFiles.some(newFile => newFile.id === file.id) 
        ? { ...file, status: 'processing' as const }
        : file
    ));

    // 1️⃣ Upload and index PDFs in Qdrant
    const uploadFormData = new FormData();
    pdfFiles.forEach((file: File) => uploadFormData.append("files", file));

    const uploadResponse = await fetch("http://localhost:8000/upload-pdfs", {
      method: "POST",
      body: uploadFormData
    });

    if (uploadResponse.ok) {
      // Update status to completed
      setUploadedFiles(prev => prev.map(file => 
        newFiles.some(newFile => newFile.id === file.id) 
          ? { ...file, status: 'completed' as const }
          : file
      ));

      // Update chat messages
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

    // 2️⃣ Request suggested questions
    const suggestFormData = new FormData();
    pdfFiles.forEach((file: File) => suggestFormData.append("files", file));

    const res = await fetch("http://localhost:8000/generate-suggested-questions", {
      method: "POST",
      body: suggestFormData
    });

    const data = await res.json();
    if (data.questions) {
      setSuggestedQuestions(data.questions);
    }
  } catch (err) {
    console.error("Error uploading PDFs or generating suggested questions", err);
    
    // Update status to error
    setUploadedFiles(prev => prev.map(file => 
      newFiles.some(newFile => newFile.id === file.id) 
        ? { ...file, status: 'error' as const }
        : file
    ));

    // Show error messages
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
    removeFile,
    formatFileSize,
    isTyping,
    messagesEndRef,
    fileInputRef,
    suggestedQuestions
  };
};
