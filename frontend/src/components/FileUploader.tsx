
// components/FileUploader.tsx
import React from 'react';
import { Upload } from 'lucide-react';

interface FileUploaderProps {
  fileInputRef: React.RefObject<HTMLInputElement>;
  handleFileUpload: (event: React.ChangeEvent<HTMLInputElement>) => void;
  isLoading: boolean;
}

const FileUploader = ({ fileInputRef, handleFileUpload, isLoading }: FileUploaderProps) => (
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
);

export default FileUploader;