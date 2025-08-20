// // components/Sidebar.tsx
// "use client"
// import React, { useRef } from 'react';
// import { Upload, FileText } from 'lucide-react';
// import { UploadedFile } from '../types';
// import SuggestedQuestions from './SuggestedQuestions';
// import { formatFileSize } from '@/utils/formatFileSize';

// interface SidebarProps {
//   uploadedFiles: UploadedFile[];
//   setUploadedFiles: (files: UploadedFile[]) => void;
//   isLoading: boolean;
//   suggestedQuestions: string[];
//   setInputMessage: (value: string) => void;
//   handleFileUpload: (e: React.ChangeEvent<HTMLInputElement>) => void;
// }

// const Sidebar: React.FC<SidebarProps> = ({
//   uploadedFiles,
//   setUploadedFiles,
//   isLoading,
//   suggestedQuestions,
//   setInputMessage,
//   handleFileUpload
// }) => {
//   const fileInputRef = useRef<HTMLInputElement>(null);

//   const removeFile = (fileId: number) => {
//     setUploadedFiles(prev => prev.filter(file => file.id !== fileId));
//   };

//   return (
//     <div className="w-80 bg-white shadow-lg border-r border-gray-200 flex flex-col">
//       {/* Upload Section */}
//       <div className="p-4 border-b border-gray-200">
//         <button
//           onClick={() => fileInputRef.current?.click()}
//           className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg flex items-center justify-center space-x-2 transition-colors"
//           disabled={isLoading}
//         >
//           <Upload className="w-5 h-5" />
//           <span>Upload PDF</span>
//         </button>
//         <input
//           ref={fileInputRef}
//           type="file"
//           multiple
//           accept=".pdf"
//           onChange={handleFileUpload}
//           className="hidden"
//         />
//       </div>

//       {/* Uploaded Files */}
//       <div className="flex-1 overflow-y-auto p-4">
//         <h3 className="font-semibold text-gray-700 mb-3 flex items-center">
//           <FileText className="w-4 h-4 mr-2" />
//           Uploaded Files
//         </h3>
//         {uploadedFiles.length === 0 ? (
//           <p className="text-sm text-gray-500">No files uploaded yet.</p>
//         ) : (
//           <ul className="space-y-3">
//             {uploadedFiles.map((file) => (
//               <li
//                 key={file.id}
//                 className="flex justify-between items-center text-sm text-gray-800 border border-gray-200 rounded p-2"
//               >
//                 <div>
//                   <p className="font-medium">{file.name}</p>
//                   <p className="text-xs text-gray-500">
//                     {formatFileSize(file.size)} - {file.uploadTime.toLocaleTimeString()}
//                   </p>
//                 </div>
//                 <button
//                   onClick={() => removeFile(file.id)}
//                   className="text-red-500 hover:text-red-700 text-xs"
//                 >
//                   Remove
//                 </button>
//               </li>
//             ))}
//           </ul>
//         )}
//       </div>

//       {/* Suggested Questions */}
//       <SuggestedQuestions
//         questions={suggestedQuestions}
//         onSelect={(question) => setInputMessage(question)}
//       />
//     </div>
//   );
// };

// export default Sidebar;
// components/Sidebar.tsx
"use client"
import React, { useRef } from 'react';
import { Upload, FileText } from 'lucide-react';
import { UploadedFile } from '../types';
import SuggestedQuestions from './SuggestedQuestions';
import { formatFileSize } from '@/utils/formatFileSize';

interface SidebarProps {
  uploadedFiles: UploadedFile[];
  setUploadedFiles: (files: UploadedFile[]) => void;
  isLoading: boolean;
  suggestedQuestions: string[];
  setInputMessage: (value: string) => void;
  handleFileUpload: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  uploadedFiles,
  setUploadedFiles,
  isLoading,
  suggestedQuestions,
  setInputMessage,
  handleFileUpload
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const removeFile = (fileId: number) => {
    setUploadedFiles(prev => prev.filter(file => file.id !== fileId));
  };

  return (
    <div className="w-80 bg-white shadow-lg border-r border-gray-200 flex flex-col">
      {/* Upload Section */}
      <div className="p-4 border-b border-gray-200">
        <button
          onClick={() => fileInputRef.current?.click()}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg flex items-center justify-center space-x-2 transition-colors"
          disabled={isLoading}
        >
          <Upload className="w-5 h-5" />
          <span>Upload PDF</span>
        </button>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf"
          onChange={handleFileUpload}
          className="hidden"
        />
      </div>

      {/* Uploaded Files (scrollable) */}
      <div className="flex-1 overflow-y-auto p-4">
        <h3 className="font-semibold text-gray-700 mb-3 flex items-center">
          <FileText className="w-4 h-4 mr-2" />
          Uploaded Files
        </h3>
        {uploadedFiles.length === 0 ? (
          <p className="text-sm text-gray-500">No files uploaded yet.</p>
        ) : (
          <ul className="space-y-3">
            {uploadedFiles.map((file) => (
              <li
                key={file.id}
                className="flex justify-between items-center text-sm text-gray-800 border border-gray-200 rounded p-2"
              >
                <div>
                  <p className="font-medium">{file.name}</p>
                  <p className="text-xs text-gray-500">
                    {formatFileSize(file.size)} - {file.uploadTime.toLocaleTimeString()}
                  </p>
                </div>
                <button
                  onClick={() => removeFile(file.id)}
                  className="text-red-500 hover:text-red-700 text-xs"
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Suggested Questions (always pinned at bottom) */}
      <div className="border-t border-gray-200 p-4">
        <SuggestedQuestions
          questions={suggestedQuestions}
          onSelect={(question) => setInputMessage(question)}
        />
      </div>
    </div>
  );
};

export default Sidebar;
