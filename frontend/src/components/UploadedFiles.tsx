import React from "react";
import { FileText, CheckCircle, Loader, AlertCircle, Upload } from "lucide-react";
import { UploadedFile } from "@/types";

interface UploadedFilesProps {
  uploadedFiles: UploadedFile[];
  removeFile: (fileId: number) => void;
  formatFileSize: (size: number) => string;
}

const StatusIcon = ({ status }: { status: string }) => {
  switch (status) {
    case "uploading":
      return <Upload className="w-4 h-4 text-blue-500 animate-pulse" />;
    case "processing":
      return <Loader className="w-4 h-4 text-yellow-500 animate-spin" />;
    case "completed":
      return <CheckCircle className="w-4 h-4 text-green-500" />;
    case "error":
      return <AlertCircle className="w-4 h-4 text-red-500" />;
    default:
      return <FileText className="w-4 h-4 text-gray-500" />;
  }
};

const getStatusColor = (status: string) => {
  switch (status) {
    case "uploading":
      return "text-blue-600 bg-blue-50 border-blue-200";
    case "processing":
      return "text-yellow-600 bg-yellow-50 border-yellow-200";
    case "completed":
      return "text-green-600 bg-green-50 border-green-200";
    case "error":
      return "text-red-600 bg-red-50 border-red-200";
    default:
      return "text-gray-600 bg-gray-50 border-gray-200";
  }
};

const UploadedFiles: React.FC<UploadedFilesProps> = ({
  uploadedFiles,
  removeFile,
  formatFileSize,
}) => (
  <div className="flex flex-col">
    {/* Title aligns with sidebar padding */}
    <div className="px-4 pt-3 pb-2">
      <h3 className="font-semibold text-gray-700 mb-3 flex items-center">
        <FileText className="w-4 h-4 mr-2" />
        Uploaded Documents ({uploadedFiles.length})
      </h3>
    </div>

    {/* SMALL scroll area */}
    {/* Adjust max-h-* to your taste: 64=16rem, 72=18rem, 80=20rem */}
    <div className="max-h-64 overflow-y-auto px-4 pb-3">
      {uploadedFiles.length === 0 ? (
        <p className="text-gray-500 text-sm">No documents uploaded yet</p>
      ) : (
        <div className="space-y-2">
          {uploadedFiles.map((file: UploadedFile) => (
            <div
              key={file.id}
              className={`group p-3 rounded-lg border ${getStatusColor(
                file.status
              )} hover:shadow-sm transition-shadow`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <StatusIcon status={file.status} />
                    <p className="text-sm font-medium text-gray-800 truncate" title={file.name}>
                      {file.name}
                    </p>
                  </div>
                  <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                </div>
                <button
                  onClick={() => removeFile(file.id)}
                  className="ml-2 text-red-500 hover:text-red-700 text-xs opacity-0 group-hover:opacity-100 transition-opacity"
                  disabled={file.status === "uploading" || file.status === "processing"}
                >
                  Remove
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  </div>
);

export default UploadedFiles;
