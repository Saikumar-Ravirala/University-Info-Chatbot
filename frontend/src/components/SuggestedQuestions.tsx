import React from "react";
import { Search } from "lucide-react";

const SuggestedQuestions = ({ suggestedQuestions, setInputMessage }) => (
  <div className="p-4 bg-white">
    <h3 className="font-semibold text-gray-700 mb-3 flex items-center">
      <Search className="w-4 h-4 mr-2" />
      Suggested Questions
    </h3>
    <div className="space-y-2">
      {suggestedQuestions.map((question: string, index: number) => (
        <button
          key={index}
          onClick={() => setInputMessage(question)}
          className="w-full text-left text-sm text-gray-700 hover:text-blue-600 hover:bg-blue-50 p-2 rounded transition-colors"
        >
          {question}
        </button>
      ))}
    </div>
  </div>
);

export default SuggestedQuestions;
