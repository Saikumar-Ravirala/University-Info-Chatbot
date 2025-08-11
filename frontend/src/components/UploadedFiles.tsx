
// components/UploadedFiles.tsx
import React from 'react';
import { FileText } from 'lucide-react';

const UploadedFiles = ({ uploadedFiles, removeFile, formatFileSize }) => (
  <div className="flex-1 overflow-y-auto">
    <div className="p-4">
      <h3 className="font-semibold text-gray-700 mb-3 flex items-center">
        <FileText className="w-4 h-4 mr-2" />
        Uploaded Documents ({uploadedFiles.length})
      </h3>
      {uploadedFiles.length === 0 ? (
        <p className="text-gray-500 text-sm">No documents uploaded yet</p>
      ) : (
        <div className="space-y-2">
          {uploadedFiles.map((file) => (
            <div key={file.id} className="bg-gray-50 p-3 rounded-lg border">
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-800 truncate" title={file.name}>{file.name}</p>
                  <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                </div>
                <button
                  onClick={() => removeFile(file.id)}
                  className="ml-2 text-red-500 hover:text-red-700 text-xs"
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