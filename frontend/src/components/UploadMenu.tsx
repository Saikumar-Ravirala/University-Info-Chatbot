// components/UploadMenu.tsx
import React, { useState, useRef, useEffect } from 'react';
import { Paperclip, Upload, Link as LinkIcon } from 'lucide-react';

interface UploadMenuProps {
  handleFileUpload: (event: React.ChangeEvent<HTMLInputElement>) => void;
  handleUrlUpload: (url: string) => void;
  isLoading: boolean;
}

const UploadMenu: React.FC<UploadMenuProps> = ({ handleFileUpload, handleUrlUpload, isLoading }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [urlInput, setUrlInput] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  const handleUrlInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUrlInput(e.target.value);
  };

  const submitUrl = () => {
    if (urlInput.trim()) {
      handleUrlUpload(urlInput.trim());
      setUrlInput('');
      setIsOpen(false);
    }
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={isLoading}
        className="p-2 rounded-full hover:bg-gray-200 disabled:opacity-50"
      >
        <Paperclip className="w-6 h-6 text-gray-600" />
      </button>
      {isOpen && (
        <div className="absolute bottom-full right-0 mb-2 w-56 bg-white rounded-lg shadow-xl border border-gray-200 z-20">
          <div className="p-2">
            <button
              onClick={() => fileInputRef.current?.click()}
              className="w-full flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
            >
              <Upload className="w-4 h-4 mr-3" />
              Upload Documents
            </button>
            <div className="mt-2 pt-2 border-t border-gray-200">
              <p className="px-3 py-1 text-xs text-gray-500">Upload from URL</p>
              <div className="flex items-center px-2 py-1">
                <input
                  type="text"
                  value={urlInput}
                  onChange={handleUrlInputChange}
                  placeholder="https://..."
                  className="w-full px-2 py-1 border border-gray-300 text-black rounded-md text-sm focus:ring-1 focus:ring-blue-500 focus:border-transparent"
                />
                <button onClick={submitUrl} className="ml-2 p-1 bg-blue-600 text-white rounded-md hover:bg-blue-700">
                  <LinkIcon className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
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
};

export default UploadMenu;
