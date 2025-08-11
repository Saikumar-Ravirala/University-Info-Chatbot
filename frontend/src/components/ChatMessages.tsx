// // components/ChatMessages.tsx
// import React from 'react';
// import ReactMarkdown from 'react-markdown';
// import { Bot, User } from 'lucide-react';
// import { Message } from '../types';

// interface ChatMessagesProps {
//   messages: Message[];
//   isTyping: boolean;
//   messagesEndRef: React.RefObject<HTMLDivElement>;
// }

// const ChatMessages: React.FC<ChatMessagesProps> = ({ messages, isTyping, messagesEndRef }) => {
//   return (
//     <div className="flex-1 overflow-y-auto p-4 space-y-4">
//       {messages.map((message) => (
//         <div
//           key={message.id}
//           className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
//         >
//           <div
//             className={`max-w-3xl px-4 py-3 rounded-lg ${
//               message.sender === 'user'
//                 ? 'bg-blue-600 text-white ml-12'
//                 : 'bg-white text-gray-800 shadow-md mr-12 border border-gray-200'
//             }`}
//           >
//             <div className="flex items-start space-x-3">
//               <div className={`p-1 rounded-full flex-shrink-0 mt-1 ${
//                 message.sender === 'bot' ? 'bg-blue-100' : 'bg-blue-500'
//               }`}>
//                 {message.sender === 'bot' ? (
//                   <Bot className="w-4 h-4 text-blue-600" />
//                 ) : (
//                   <User className="w-4 h-4 text-white" />
//                 )}
//               </div>
//               <div className="flex-1">
//                 <div className="prose prose-sm max-w-none whitespace-pre-wrap text-sm">
//                   <ReactMarkdown>{message.text}</ReactMarkdown>
//                 </div>
//                 <p className={`text-xs mt-2 ${
//                   message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
//                 }`}>
//                   {message.timestamp.toLocaleTimeString()}
//                 </p>
//               </div>
//             </div>
//           </div>
//         </div>
//       ))}

//       {isTyping && (
//         <div className="flex justify-start">
//           <div className="bg-white text-gray-800 shadow-md mr-12 border border-gray-200 px-4 py-3 rounded-lg">
//             <div className="flex items-center space-x-3">
//               <div className="bg-blue-100 p-1 rounded-full">
//                 <Bot className="w-4 h-4 text-blue-600" />
//               </div>
//               <div className="flex items-center space-x-1">
//                 <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
//                 <div
//                   className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
//                   style={{ animationDelay: '0.1s' }}
//                 />
//                 <div
//                   className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
//                   style={{ animationDelay: '0.2s' }}
//                 />
//               </div>
//             </div>
//           </div>
//         </div>
//       )}

//       <div ref={messagesEndRef} />
//     </div>
//   );
// };

// export default ChatMessages;
// components/AcademicChatbot/ChatMessages.tsx
import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Bot, User } from 'lucide-react';

const ChatMessages = ({ messages, isTyping, messagesEndRef }) => (
  <div className="flex-1 overflow-y-auto p-4 space-y-4">
    {messages.map((message) => (
      <div key={message.id} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
        <div className={`max-w-3xl px-4 py-3 rounded-lg ${
          message.sender === 'user' ? 'bg-blue-600 text-white ml-12' : 'bg-white text-gray-800 shadow-md mr-12 border'
        }`}>
          <div className="flex items-start space-x-3">
            <div className="p-1 rounded-full mt-1">
              {message.sender === 'bot' ? <Bot className="w-4 h-4 text-blue-600" /> : <User className="w-4 h-4 text-white" />}
            </div>
            <div>
              <div className="prose prose-sm max-w-none whitespace-pre-wrap text-sm">
                <ReactMarkdown>{message.text}</ReactMarkdown>
              </div>
              <p className={`text-xs mt-2 ${message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'}`}>
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        </div>
      </div>
    ))}
    {isTyping && (
      <div className="flex justify-start">
        <div className="bg-white text-gray-800 shadow-md mr-12 border px-4 py-3 rounded-lg">
          <div className="flex items-center space-x-3">
            <Bot className="w-4 h-4 text-blue-600" />
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
            </div>
          </div>
        </div>
      </div>
    )}
    <div ref={messagesEndRef} />
  </div>
);

export default ChatMessages;
