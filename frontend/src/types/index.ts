// types/index.ts
export interface Message {
  id: number;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  responseTime?: number; // in milliseconds
}

export interface UploadedFile {
  id: number;
  name: string;
  size: number;
  uploadTime: Date;
  rawFile: File;
  status: 'uploading' | 'processing' | 'completed' | 'error';
}
