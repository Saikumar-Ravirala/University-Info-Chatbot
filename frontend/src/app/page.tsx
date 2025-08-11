// src/app/page.tsx (server component)
import AcademicChatbot from '@/components/AcademicChatbot';

export default function Page() {
  return <AcademicChatbot />;
}


// "use client";
// import React, { useState, useRef, useEffect } from 'react';
// import { Send, FileText, Upload, Bot, User, Loader, Download, Search, BookOpen } from 'lucide-react';
// import ReactMarkdown from 'react-markdown';


// const AcademicChatbot = () => {
//   const [messages, setMessages] = useState([
//     {
//       id: 1,
//       text: "Hello! I'm your University Info Assistant. Ask me anything about admissions, courses, campus life, departments, or student services. I'm here to help you explore and understand your university experience.",
//       sender: 'bot',
//       timestamp: new Date()
//     }
//   ]);
//   const [inputMessage, setInputMessage] = useState('');
//   const [isLoading, setIsLoading] = useState(false);
//   const [uploadedFiles, setUploadedFiles] = useState([]);
//   const [isTyping, setIsTyping] = useState(false);
//   const messagesEndRef = useRef(null);
//   const fileInputRef = useRef(null);

//   // const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([]);
//   // const [loadingQuestions, setLoadingQuestions] = useState(false);


//   const scrollToBottom = () => {
//     messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
//   };

//   useEffect(() => {
//     scrollToBottom();
//   }, [messages]);

//   const handleSendMessage = async () => {
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
//   formData.append("file", uploadedFiles[0].rawFile); // assuming only 1 PDF is used at a time

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
//   };


//   // const handleSendMessage = async () => {
//   //   if (!inputMessage.trim()) return;

//   //   const userMessage = {
//   //     id: messages.length + 1,
//   //     text: inputMessage,
//   //     sender: 'user',
//   //     timestamp: new Date()
//   //   };

//   //   setMessages(prev => [...prev, userMessage]);
//   //   setInputMessage('');
//   //   setIsLoading(true);
//   //   setIsTyping(true);

//   //   try {
//   //     // Replace with your FastAPI backend URL
//   //     const response = await fetch('http://localhost:8000/chat', {
//   //       method: 'POST',
//   //       headers: {
//   //         'Content-Type': 'application/json',
//   //       },
//   //       body: JSON.stringify({
//   //         message: inputMessage,
//   //         files: uploadedFiles.map(f => f.name)
//   //       }),
//   //     });

//   //     const data = await response.json();
      
//   //     setTimeout(() => {
//   //       const botMessage = {
//   //         id: messages.length + 2,
//   //         text: data.response || "I'm having trouble processing your request. Please try again.",
//   //         sender: 'bot',
//   //         timestamp: new Date()
//   //       };
//   //       setMessages(prev => [...prev, botMessage]);
//   //       setIsLoading(false);
//   //       setIsTyping(false);
//   //     }, 1000);

//   //   } catch (error) {
//   //     console.error('Error:', error);
//   //     const errorMessage = {
//   //       id: messages.length + 2,
//   //       text: "Sorry, I'm having trouble connecting to the server. Please check your connection and try again.",
//   //       sender: 'bot',
//   //       timestamp: new Date()
//   //     };
//   //     setMessages(prev => [...prev, errorMessage]);
//   //     setIsLoading(false);
//   //     setIsTyping(false);
//   //   }
//   // };

//   // const handleFileUpload = async (event) => {
//   //   const files = Array.from(event.target.files);
//   //   const pdfFiles = files.filter(file => file.type === 'application/pdf');
    
//   //   if (pdfFiles.length === 0) {
//   //     alert('Please upload only PDF files.');
//   //     return;
//   //   }

//   //   setIsLoading(true);
    
//   //   for (const file of pdfFiles) {
//   //     const formData = new FormData();
//   //     formData.append('file', file);

//   //     try {
//   //       // Replace with your FastAPI backend URL for file upload
//   //       const response = await fetch('http://localhost:8000/upload', {
//   //         method: 'POST',
//   //         body: formData,
//   //       });

//   //       if (response.ok) {
//   //         const newFile = {
//   //           id: Date.now() + Math.random(),
//   //           name: file.name,
//   //           size: file.size,
//   //           uploadTime: new Date()
//   //         };
//   //         setUploadedFiles(prev => [...prev, newFile]);
          
//   //         const uploadMessage = {
//   //           id: messages.length + Date.now(),
//   //           text: `📄 Successfully uploaded: ${file.name}. You can now ask questions about this document!`,
//   //           sender: 'bot',
//   //           timestamp: new Date()
//   //         };
//   //         setMessages(prev => [...prev, uploadMessage]);
//   //       }
//   //     } catch (error) {
//   //       console.error('Upload error:', error);
//   //       alert(`Failed to upload ${file.name}`);
//   //     }
//   //   }
    
//   //   setIsLoading(false);
//   //   event.target.value = '';
//   // };

//   const handleFileUpload = async (event) => {
//   const files = Array.from(event.target.files);
//   const pdfFiles = files.filter(file => file.type === 'application/pdf');

//   if (pdfFiles.length === 0) {
//     alert('Only PDFs allowed');
//     return;
//   }

//   const newFile = {
//     id: Date.now() + Math.random(),
//     name: pdfFiles[0].name,
//     size: pdfFiles[0].size,
//     uploadTime: new Date(),
//     rawFile: pdfFiles[0] // store the file itself for sending later
//   };
  
//   setUploadedFiles([newFile]); // Only one file supported per session for now

//   setMessages(prev => [...prev, {
//     id: Date.now(),
//     text: `📄 Uploaded: ${newFile.name}`,
//     sender: 'bot',
//     timestamp: new Date()
//   }]);
// };
// //   const handleFileUpload = async (event) => {
// //   const files = Array.from(event.target.files);
// //   const pdfFiles = files.filter(file => file.type === 'application/pdf');

// //   if (pdfFiles.length === 0) {
// //     alert('Only PDFs allowed');
// //     return;
// //   }

// //   const file = pdfFiles[0];

// //   const newFile = {
// //     id: Date.now() + Math.random(),
// //     name: file.name,
// //     size: file.size,
// //     uploadTime: new Date(),
// //     rawFile: file
// //   };

// //   setUploadedFiles([newFile]); // Replace existing files

// //   setMessages(prev => [...prev, {
// //     id: Date.now(),
// //     text: `📄 Uploaded: ${newFile.name}`,
// //     sender: 'bot',
// //     timestamp: new Date()
// //   }]);

// //   // 🔁 Fetch suggested questions
// //   setLoadingQuestions(true);
// //   const formData = new FormData();
// //   formData.append('file', file);

// //   try {
// //     const res = await fetch('http://localhost:8000/suggested-questions', {
// //       method: 'POST',
// //       body: formData
// //     });

// //     if (!res.ok) throw new Error('Failed to get questions');

// //     const data = await res.json();
// //     setSuggestedQuestions(data.questions || []);
// //   } catch (err) {
// //     console.error('Failed to fetch questions:', err);
// //     setSuggestedQuestions([]);
// //   } finally {
// //     setLoadingQuestions(false);
// //   }
// // };


//   const removeFile = (fileId) => {
//     setUploadedFiles(prev => prev.filter(file => file.id !== fileId));
//   };

//   const formatFileSize = (bytes) => {
//     if (bytes === 0) return '0 Bytes';
//     const k = 1024;
//     const sizes = ['Bytes', 'KB', 'MB', 'GB'];
//     const i = Math.floor(Math.log(bytes) / Math.log(k));
//     return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
//   };

//   // const suggestedQuestions = [
//   //   "Summarize the main findings of this paper",
//   //   "What methodology was used in this research?",
//   //   "List the key references cited",
//   //   "Explain the theoretical framework",
//   //   "What are the limitations mentioned?",
//   //   "Compare the results with previous studies"
//   // ];

//   const suggestedQuestions = [
//     "How do I apply for admission?",
//     "What undergraduate programs are offered?",
//     "Can you tell me about campus facilities?",
//     "What scholarships are available?",
//     "How do I contact the admissions office?",
//     "What student clubs and organizations are there?"
//   ];


//   return (
//      <div className="flex flex-col min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
    

//       {/* Header */}
//       <div className="bg-white shadow-lg border-b border-gray-200">
//         <div className="max-w-4xl mx-auto px-4 py-4">
//           <div className="flex items-center space-x-3">
//             <div className="bg-blue-600 p-2 rounded-lg">
//               <BookOpen className="w-6 h-6 text-white" />
//             </div>
//             <div>
//               <h1 className="text-xl font-bold text-gray-800">University Info Assistant</h1>
//               <p className="text-sm text-gray-600">Ask me anything to start exploring university information</p>
//             </div>
//           </div>
//         </div>
//       </div>

//       <div className="flex-1 flex max-w-6xl mx-auto w-full">
//         {/* Sidebar */}
//         <div className="w-80 bg-white shadow-lg border-r border-gray-200 flex flex-col">
//           {/* Upload Section */}
//           <div className="p-4 border-b border-gray-200">
//             <button
//               onClick={() => fileInputRef.current?.click()}
//               className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg flex items-center justify-center space-x-2 transition-colors"
//               disabled={isLoading}
//             >
//               <Upload className="w-5 h-5" />
//               <span>Upload PDF</span>
//             </button>
//             <input
//               ref={fileInputRef}
//               type="file"
//               multiple
//               accept=".pdf"
//               onChange={handleFileUpload}
//               className="hidden"
//             />
//           </div>

//           {/* Uploaded Files */}
//           <div className="flex-1 overflow-y-auto">
//             <div className="p-4">
//               <h3 className="font-semibold text-gray-700 mb-3 flex items-center">
//                 <FileText className="w-4 h-4 mr-2" />
//                 Uploaded Documents ({uploadedFiles.length})
//               </h3>
//               {uploadedFiles.length === 0 ? (
//                 <p className="text-gray-500 text-sm">No documents uploaded yet</p>
//               ) : (
//                 <div className="space-y-2">
//                   {uploadedFiles.map((file) => (
//                     <div key={file.id} className="bg-gray-50 p-3 rounded-lg border">
//                       <div className="flex items-start justify-between">
//                         <div className="flex-1 min-w-0">
//                           <p className="text-sm font-medium text-gray-800 truncate" title={file.name}>
//                             {file.name}
//                           </p>
//                           <p className="text-xs text-gray-500">
//                             {formatFileSize(file.size)}
//                           </p>
//                         </div>
//                         <button
//                           onClick={() => removeFile(file.id)}
//                           className="ml-2 text-red-500 hover:text-red-700 text-xs"
//                         >
//                           Remove
//                         </button>
//                       </div>
//                     </div>
//                   ))}
//                 </div>
//               )}
//             </div>
//           </div>

//           {/* Suggested Questions */}
//           {/* <div className="p-4 border-t border-gray-200" > */}
//           <div className="p-4 border-t border-gray-200 sticky bottom-0 z-10">
//             <h3 className="font-semibold text-gray-700 mb-3 flex items-center">
//               <Search className="w-4 h-4 mr-2" />
//               Suggested Questions
//             </h3>
//             <div className="space-y-2">
//               {suggestedQuestions.map((question, index) => (
//                 <button
//                   key={index}
//                   onClick={() => setInputMessage(question)}
//                   className="w-full text-left text-xs text-gray-600 hover:text-blue-600 hover:bg-blue-50 p-2 rounded transition-colors"
//                 >
//                   {question}
//                 </button>
//               ))}
//             </div>
//           </div>
//           {/* <div className="p-4 border-t border-gray-200">
//   <h3 className="font-semibold text-gray-700 mb-3 flex items-center">
//     <Search className="w-4 h-4 mr-2" />
//     Suggested Questions
//   </h3>
//   {loadingQuestions ? (
//     <p className="text-xs text-gray-500">Loading questions...</p>
//   ) : suggestedQuestions.length > 0 ? (
//     <div className="space-y-2">
//       {suggestedQuestions.map((question, index) => (
//         <button
//           key={index}
//           onClick={() => setInputMessage(question)}
//           className="w-full text-left text-xs text-gray-600 hover:text-blue-600 hover:bg-blue-50 p-2 rounded transition-colors"
//         >
//           {question}
//         </button>
//       ))}
//     </div>
//   ) : (
//     <p className="text-xs text-gray-500">No suggestions available</p>
//   )}
//           </div> */}


//         </div>

//         {/* Main Chat Area */}
//         <div className="flex-1 flex flex-col">
//           {/* Messages */}
//           <div className="flex-1 overflow-y-auto p-4 space-y-4">
//             {messages.map((message) => (
//               <div
//                 key={message.id}
//                 className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
//               >
//                 <div
//                   className={`max-w-3xl px-4 py-3 rounded-lg ${
//                     message.sender === 'user'
//                       ? 'bg-blue-600 text-white ml-12'
//                       : 'bg-white text-gray-800 shadow-md mr-12 border border-gray-200'
//                   }`}
//                 >
//                   <div className="flex items-start space-x-3">
//                     {message.sender === 'bot' && (
//                       <div className="bg-blue-100 p-1 rounded-full flex-shrink-0 mt-1">
//                         <Bot className="w-4 h-4 text-blue-600" />
//                       </div>
//                     )}
//                     {message.sender === 'user' && (
//                       <div className="bg-blue-500 p-1 rounded-full flex-shrink-0 mt-1">
//                         <User className="w-4 h-4 text-white" />
//                       </div>
//                     )}
//                     <div className="flex-1">
//                       {/* <p className="whitespace-pre-wrap">{message.text}</p> */}
//                       <div className="prose prose-sm max-w-none whitespace-pre-wrap text-sm">
//                           <ReactMarkdown>
//                           {message.text}
//                           </ReactMarkdown>
//                       </div>


//                       <p className={`text-xs mt-2 ${
//                         message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
//                       }`}>
//                         {message.timestamp.toLocaleTimeString()}
//                       </p>
//                     </div>
//                   </div>
//                 </div>
//               </div>
//             ))}
            
//             {isTyping && (
//               <div className="flex justify-start">
//                 <div className="bg-white text-gray-800 shadow-md mr-12 border border-gray-200 px-4 py-3 rounded-lg">
//                   <div className="flex items-center space-x-3">
//                     <div className="bg-blue-100 p-1 rounded-full">
//                       <Bot className="w-4 h-4 text-blue-600" />
//                     </div>
//                     <div className="flex items-center space-x-1">
//                       <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
//                       <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
//                       <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
//                     </div>
//                   </div>
//                 </div>
//               </div>
//             )}
//             <div ref={messagesEndRef} />
//           </div>

//           {/* Input Area */}
//           {/* <div className="border-t border-gray-200 bg-white p-4"> */}
//           <div className="border-t border-gray-200 bg-white p-4 sticky bottom-0 z-10">

//             <div className="flex space-x-3">
//               <div className="flex-1 relative">
//                 <input
//   type="text"
//   value={inputMessage}
//   onChange={(e) => setInputMessage(e.target.value)}
//   onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
//   placeholder={uploadedFiles.length > 0 ? "Ask questions about your documents..." : "Upload a PDF first to start asking questions..."}
//   disabled={isLoading || uploadedFiles.length === 0}
//   className="w-full px-4 py-3 border border-gray-300 rounded-lg bg-white text-black focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed"
// />

//               </div>
//               <button
//                 onClick={handleSendMessage}
//                 disabled={!inputMessage.trim() || isLoading || uploadedFiles.length === 0}
//                 className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg transition-colors flex items-center space-x-2 disabled:cursor-not-allowed"
//               >
//                 {isLoading ? (
//                   <Loader className="w-5 h-5 animate-spin" />
//                 ) : (
//                   <Send className="w-5 h-5" />
//                 )}
//               </button>
//             </div>
//             {uploadedFiles.length === 0 && (
//               <p className="text-xs text-gray-500 mt-2">
//                 Get answers about admissions, programs, campus life, and more
//               </p>
//             )}
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default AcademicChatbot;