"use client";
import React, { useRef, Dispatch, SetStateAction } from "react";
import { Upload } from "lucide-react";
import { UploadedFile } from "../types";
import UploadedFiles from "./UploadedFiles";
import SuggestedQuestions from "./SuggestedQuestions";
import { formatFileSize } from "@/utils/formatFileSize";

interface SidebarProps {
  uploadedFiles: UploadedFile[];
  setUploadedFiles: Dispatch<SetStateAction<UploadedFile[]>>;
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
  handleFileUpload,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const removeFile = (fileId: number) => {
    setUploadedFiles((prev) => prev.filter((file) => file.id !== fileId));
  };

  return (
    <aside className="w-80 bg-white border-r shadow-sm h-screen sticky top-0 flex flex-col min-h-0">
      {/* Upload section */}
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

      {/* Uploaded Files — small scroll area (fixed height) */}
      <div className="px-0 py-0">
        <UploadedFiles
          uploadedFiles={uploadedFiles}
          removeFile={removeFile}
          formatFileSize={formatFileSize}
        />
      </div>

      {/* Suggested Questions — pinned at bottom, seamless divider */}
      <div className="mt-auto border-t border-gray-200">
        <SuggestedQuestions
          suggestedQuestions={suggestedQuestions}
          setInputMessage={setInputMessage}
        />
      </div>
    </aside>
  );
};

export default Sidebar;
