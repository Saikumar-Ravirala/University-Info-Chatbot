// types/index.ts
export interface Message {
  id: number;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

export interface UploadedFile {
  id: number;
  name: string;
  size: number;
  uploadTime: Date;
  rawFile: File;
}
