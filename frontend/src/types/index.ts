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
  size: number | null;
  uploadTime: Date;
  rawFile: File | null;
  status: 'uploading' | 'processing' | 'completed' | 'error';
}
