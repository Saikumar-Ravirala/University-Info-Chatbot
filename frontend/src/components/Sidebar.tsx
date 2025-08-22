"use client";
import React from "react";
import UploadedFiles from "./UploadedFiles";
import SuggestedQuestions from "./SuggestedQuestions";
import { UploadedFile } from "@/types";

interface SidebarProps {
  isLoading: boolean;
  uploadedFiles: UploadedFile[];
  removeFile: (fileId: number) => void;
  formatFileSize: (bytes: number) => string;
  suggestedQuestions: string[];
  setInputMessage: (value: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  isLoading,
  uploadedFiles,
  removeFile,
  formatFileSize,
  suggestedQuestions,
  setInputMessage,
}) => {
  return (
    <aside className="w-80 bg-white border-r shadow-sm h-screen sticky top-0 flex flex-col min-h-0">
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
