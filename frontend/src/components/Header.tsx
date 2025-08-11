
// components/Header.tsx
import React from 'react';
import { BookOpen } from 'lucide-react';

const Header = () => (
  <div className="bg-white shadow-lg border-b border-gray-200">
    <div className="max-w-4xl mx-auto px-4 py-4">
      <div className="flex items-center space-x-3">
        <div className="bg-blue-600 p-2 rounded-lg">
          <BookOpen className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-gray-800">University Info Assistant</h1>
          <p className="text-sm text-gray-600">Ask me anything to start exploring university information</p>
        </div>
      </div>
    </div>
  </div>
);

export default Header;