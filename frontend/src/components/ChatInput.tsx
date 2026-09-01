import React, { useState, useRef, useEffect } from "react";
import { Send, Sparkles } from "lucide-react";

interface ChatInputProps {
  onSendMessage: (query: string) => void;
  disabled: boolean;
}

const EXAMPLE_PROMPTS = [
  "Show total sales and profit by region in 2024",
  "Which 5 products generated the highest revenue?",
  "What about for Chennai only?",
  "Forecast monthly revenue for the next 6 months",
];

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  disabled,
}) => {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSendMessage(input.trim());
      setInput("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handlePromptClick = (prompt: string) => {
    if (!disabled) {
      onSendMessage(prompt);
    }
  };

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [input]);

  return (
    <div className="border-t border-[#1F2937] bg-[#070B14]/90 p-4 backdrop-blur-lg">
      <div className="max-w-4xl mx-auto space-y-3">
        {/* Suggestion Chips */}
        <div className="flex items-center space-x-2 overflow-x-auto pb-1 text-xs no-scrollbar">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
          <span className="text-[11px] text-gray-500 font-medium shrink-0">Try asking:</span>
          {EXAMPLE_PROMPTS.map((p, idx) => (
            <button
              key={idx}
              onClick={() => handlePromptClick(p)}
              disabled={disabled}
              className="shrink-0 px-3 py-1 rounded-full bg-[#111827] hover:bg-indigo-950/60 hover:text-indigo-300 text-gray-400 border border-[#1F2937] hover:border-indigo-800/50 text-[11px] transition-all"
            >
              {p}
            </button>
          ))}
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="relative flex items-center">
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            placeholder="Ask a business question in natural language (e.g. 'Compare sales between Chennai and Bangalore in 2024')..."
            className="w-full pl-4 pr-12 py-3 bg-[#111827]/90 border border-[#1F2937] focus:border-indigo-500 rounded-xl text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 resize-none transition-all"
          />
          <button
            type="submit"
            disabled={!input.trim() || disabled}
            className="absolute right-2 p-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-30 disabled:hover:bg-indigo-600 text-white transition-all shadow-md shadow-indigo-600/30"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
