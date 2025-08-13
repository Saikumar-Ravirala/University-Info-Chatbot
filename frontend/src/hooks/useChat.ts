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

  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // const handleSendMessage = async () => {
  //   if (!inputMessage.trim() || uploadedFiles.length === 0) return;

  //   const userMessage = {
  //     id: messages.length + 1,
  //     text: inputMessage,
  //     sender: 'user',
  //     timestamp: new Date()
  //   };

  //   setMessages(prev => [...prev, userMessage]);
  //   setInputMessage('');
  //   setIsLoading(true);
  //   setIsTyping(true);

  //   const formData = new FormData();
  //   formData.append("query", inputMessage);
  //   formData.append("file", uploadedFiles[0].rawFile);

  //   try {
  //     const response = await fetch("http://localhost:8000/chat", {
  //       method: "POST",
  //       body: formData
  //     });

  //     const data = await response.json();

  //     const botMessage = {
  //       id: messages.length + 2,
  //       text: data.answer || "I'm having trouble processing your request.",
  //       sender: 'bot',
  //       timestamp: new Date()
  //     };

  //     setMessages(prev => [...prev, botMessage]);
  //   } catch (error) {
  //     console.error(error);
  //     setMessages(prev => [...prev, {
  //       id: messages.length + 2,
  //       text: "Server error. Please try again.",
  //       sender: 'bot',
  //       timestamp: new Date()
  //     }]);
  //   }

  //   setIsLoading(false);
  //   setIsTyping(false);
  // };

  

    // const handleSendMessage = async () => {
    //   if (!inputMessage.trim() || uploadedFiles.length === 0) return;

    //   const userMessage = {
    //     id: messages.length + 1,
    //     text: inputMessage,
    //     sender: 'user',
    //     timestamp: new Date()
    //   };

    //   setMessages(prev => [...prev, userMessage]);
    //   setInputMessage('');
    //   setIsLoading(true);
    //   setIsTyping(true);

    //   const formData = new FormData();
    //   formData.append("query", inputMessage);
    //   uploadedFiles.forEach((file) => {
    //     formData.append("files", file.rawFile);
    //   });

    //   try {
    //     const data = await sendChatMessage(formData);

    //     const botMessage = {
    //       id: messages.length + 2,
    //       text: data.answer || "I'm having trouble processing your request.",
    //       sender: 'bot',
    //       timestamp: new Date()
    //     };

    //     setMessages(prev => [...prev, botMessage]);
    //   } catch (error) {
    //     console.error(error);
    //     setMessages(prev => [...prev, {
    //       id: messages.length + 2,
    //       text: "Server error. Please try again.",
    //       sender: 'bot',
    //       timestamp: new Date()
    //     }]);
    //   }

    //   setIsLoading(false);
    //   setIsTyping(false);
    // };


  // const handleFileUpload = (event: any) => {
  //   const files = Array.from(event.target.files);
  //   const pdfFiles = files.filter((file: any) => file.type === 'application/pdf');

  //   if (pdfFiles.length === 0) {
  //     alert('Only PDFs allowed');
  //     return;
  //   }

  //   const newFile = {
  //     id: Date.now() + Math.random(),
  //     name: pdfFiles[0].name,
  //     size: pdfFiles[0].size,
  //     uploadTime: new Date(),
  //     rawFile: pdfFiles[0]
  //   };

  //   setUploadedFiles([newFile]);
  //   setMessages(prev => [...prev, {
  //     id: Date.now(),
  //     text: `📄 Uploaded: ${newFile.name}`,
  //     sender: 'bot',
  //     timestamp: new Date()
  //   }]);
  // };

    // const handleSendMessage = async () => {
    //   if (!inputMessage.trim() || uploadedFiles.length === 0) return;

    //   const userMessage = {
    //     id: messages.length + 1,
    //     text: inputMessage,
    //     sender: 'user',
    //     timestamp: new Date()
    //   };

    //   setMessages(prev => [...prev, userMessage]);
    //   setInputMessage('');
    //   setIsLoading(true);
    //   setIsTyping(true);

    //   const formData = new FormData();
    //   formData.append("query", inputMessage);
    //   uploadedFiles.forEach((file) => {
    //     formData.append("files", file.rawFile);
    //   });

    //   try {
    //     const data = await sendChatMessage(formData);

    //     const botMessage = {
    //       id: messages.length + 2,
    //       text: data.answer || "I'm having trouble processing your request.",
    //       sender: 'bot',
    //       timestamp: new Date()
    //     };

    //     setMessages(prev => [...prev, botMessage]);
    //   } catch (error) {
    //     console.error(error);
    //     setMessages(prev => [...prev, {
    //       id: messages.length + 2,
    //       text: "Server error. Please try again.",
    //       sender: 'bot',
    //       timestamp: new Date()
    //     }]);
    //   }

    //   setIsLoading(false);
    //   setIsTyping(false);
    // };
  
    const handleSendMessage = async () => {
  if (!inputMessage.trim() || uploadedFiles.length === 0) return;

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
            setMessages(prev => prev.map(m => m.id === botMessage.id ? { ...m, text: botText } : m));
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


//     const handleFileUpload = async (event: any) => {
//       const files = Array.from(event.target.files);
//       const pdfFiles = files.filter((file: any) => file.type === 'application/pdf');

//       if (pdfFiles.length === 0) {
//         alert('Only PDFs allowed');
//         return;
//       }

//       const newFiles = pdfFiles.map((file: any) => ({
//         id: Date.now() + Math.random(),
//         name: file.name,
//         size: file.size,
//         uploadTime: new Date(),
//         rawFile: file
//     }));

//   setUploadedFiles(prev => [...prev, ...newFiles]);

//   const uploadMessages = newFiles.map(file => ({
//     id: Date.now() + Math.random(),
//     text: `📄 Uploaded: ${file.name}`,
//     sender: 'bot',
//     timestamp: new Date()
//   }));

//   setMessages(prev => [...prev, ...uploadMessages]);

//    // 🔹 Immediately request suggested questions
//       try {
//         const formData = new FormData();
//         pdfFiles.forEach(file => formData.append("files", file));

//         const res = await fetch("http://localhost:8000/generate-suggested-questions", {
//           method: "POST",
//           body: formData
//         });

//         const data = await res.json();
//         if (data.questions) {
//           setSuggestedQuestions(data.questions);
//         }
//       } catch (err) {
//         console.error("Error generating suggested questions", err);
//       }
// };

const handleFileUpload = async (event: any) => {
  const files = Array.from(event.target.files);
  const pdfFiles = files.filter((file: any) => file.type === 'application/pdf');

  if (pdfFiles.length === 0) {
    alert('Only PDFs allowed');
    return;
  }

  const newFiles = pdfFiles.map((file: any) => ({
    id: Date.now() + Math.random(),
    name: file.name,
    size: file.size,
    uploadTime: new Date(),
    rawFile: file
  }));

  // Update uploaded files in state
  setUploadedFiles(prev => [...prev, ...newFiles]);

  // Show "uploaded" messages in chat
  const uploadMessages = newFiles.map(file => ({
    id: Date.now() + Math.random(),
    text: `📄 Uploaded: ${file.name}`,
    sender: 'bot',
    timestamp: new Date()
  }));
  setMessages(prev => [...prev, ...uploadMessages]);

  try {
    // 1️⃣ Upload and index PDFs in Qdrant
    const uploadFormData = new FormData();
    pdfFiles.forEach(file => uploadFormData.append("files", file));

    await fetch("http://localhost:8000/upload-pdfs", {
      method: "POST",
      body: uploadFormData
    });

    // 2️⃣ Request suggested questions
    const suggestFormData = new FormData();
    pdfFiles.forEach(file => suggestFormData.append("files", file));

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
  }
};


  const removeFile = (fileId: number) => {
    setUploadedFiles(prev => prev.filter(file => file.id !== fileId));
  };

  // const formatFileSize = (bytes: number) => {
  //   if (bytes === 0) return '0 Bytes';
  //   const k = 1024;
  //   const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  //   const i = Math.floor(Math.log(bytes) / Math.log(k));
  //   return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  // };

  

  // const suggestedQuestions = [
  //   "How do I apply for admission?",
  //   "What undergraduate programs are offered?",
  //   "Can you tell me about campus facilities?",
  //   "What scholarships are available?",
  //   "How do I contact the admissions office?",
  //   "What student clubs and organizations are there?"
  // ];

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
// import { useState, useEffect, useRef } from 'react';

// export const useChat = () => {
//   const [messages, setMessages] = useState<any[]>([
//     {
//       id: 1,
//       text: "Hello! I'm your University Info Assistant...",
//       sender: 'bot',
//       timestamp: new Date()
//     }
//   ]);
//   const [inputMessage, setInputMessage] = useState('');
//   const [isLoading, setIsLoading] = useState(false);
//   const [uploadedFiles, setUploadedFiles] = useState<any[]>([]);
//   const [isTyping, setIsTyping] = useState(false);
//   const messagesEndRef = useRef(null);

//   const scrollToBottom = () => {
//     messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
//   };

//   useEffect(() => {
//     scrollToBottom();
//   }, [messages]);

//   const handleSendMessage = async () => {
//     if (!inputMessage.trim() || uploadedFiles.length === 0) return;

//     const userMessage = {
//       id: messages.length + 1,
//       text: inputMessage,
//       sender: 'user',
//       timestamp: new Date()
//     };

//     setMessages(prev => [...prev, userMessage]);
//     setInputMessage('');
//     setIsLoading(true);
//     setIsTyping(true);

//     const formData = new FormData();
//     formData.append("query", inputMessage);
//     formData.append("file", uploadedFiles[0].rawFile);

//     try {
//       const response = await fetch("http://localhost:8000/chat", {
//         method: "POST",
//         body: formData
//       });

//       const data = await response.json();

//       const botMessage = {
//         id: messages.length + 2,
//         text: data.answer || "I'm having trouble processing your request.",
//         sender: 'bot',
//         timestamp: new Date()
//       };

//       setMessages(prev => [...prev, botMessage]);
//     } catch (error) {
//       console.error(error);
//       setMessages(prev => [...prev, {
//         id: messages.length + 2,
//         text: "Server error. Please try again.",
//         sender: 'bot',
//         timestamp: new Date()
//       }]);
//     }

//     setIsLoading(false);
//     setIsTyping(false);
//   };

//   const handleFileUpload = (event: any) => {
//     const files = Array.from(event.target.files);
//     const pdfFiles = files.filter((file: any) => file.type === 'application/pdf');

//     if (pdfFiles.length === 0) {
//       alert('Only PDFs allowed');
//       return;
//     }

//     const newFile = {
//       id: Date.now() + Math.random(),
//       name: pdfFiles[0].name,
//       size: pdfFiles[0].size,
//       uploadTime: new Date(),
//       rawFile: pdfFiles[0]
//     };

//     setUploadedFiles([newFile]);

//     setMessages(prev => [...prev, {
//       id: Date.now(),
//       text: `📄 Uploaded: ${newFile.name}`,
//       sender: 'bot',
//       timestamp: new Date()
//     }]);
//   };

//   const removeFile = (fileId: number) => {
//     setUploadedFiles(prev => prev.filter(file => file.id !== fileId));
//   };

//   const formatFileSize = (bytes: number) => {
//     if (bytes === 0) return '0 Bytes';
//     const k = 1024;
//     const sizes = ['Bytes', 'KB', 'MB', 'GB'];
//     const i = Math.floor(Math.log(bytes) / Math.log(k));
//     return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
//   };

//   const suggestedQuestions = [
//     "How do I apply for admission?",
//     "What undergraduate programs are offered?",
//     "Can you tell me about campus facilities?",
//     "What scholarships are available?",
//     "How do I contact the admissions office?",
//     "What student clubs and organizations are there?"
//   ];

//   return {
//     messages,
//     inputMessage,
//     setInputMessage,
//     isLoading,
//     handleSendMessage,
//     handleFileUpload,
//     uploadedFiles,
//     removeFile,
//     formatFileSize,
//     isTyping,
//     messagesEndRef,
//     suggestedQuestions
//   };
// };

// hooks/useChat.ts
