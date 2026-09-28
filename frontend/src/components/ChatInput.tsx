import React, { useState, useRef, useEffect } from "react";
import { Send, Sparkles } from "lucide-react";

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
}

const SUGGESTED_PROMPTS = [
  { text: "Show total sales and profit by region for 2024", color: "bg-[#FFD93D]", rot: "rotate-[-1deg]" },
  { text: "Which 5 products generated the highest revenue?", color: "bg-[#C4B5FD]", rot: "rotate-[1deg]" },
  { text: "Show brand count as a pie chart", color: "bg-[#FF6B6B] text-white", rot: "rotate-[-1deg]" },
  { text: "Forecast monthly sales for the next 6 months", color: "bg-[#10B981] text-white", rot: "rotate-[1deg]" },
];

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  disabled = false,
}) => {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [input]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || disabled) return;
    onSendMessage(input.trim());
    setInput("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="border-t-4 border-black bg-[#FFFDF5] p-4 z-20">
      <div className="max-w-4xl mx-auto space-y-3">
        {/* Suggestion Chips */}
        <div className="flex items-center space-x-2 overflow-x-auto pb-1 no-scrollbar">
          <div className="flex items-center space-x-1.5 text-[11px] font-black uppercase text-black shrink-0 px-2 py-1 bg-[#FFD93D] border-2 border-black shadow-[2px_2px_0px_0px_#000]">
            <Sparkles className="w-3.5 h-3.5 stroke-[3px]" />
            <span>TRY:</span>
          </div>
          {SUGGESTED_PROMPTS.map((prompt, idx) => (
            <button
              key={idx}
              onClick={() => onSendMessage(prompt.text)}
              disabled={disabled}
              className={`shrink-0 px-3 py-1.5 text-xs font-black uppercase tracking-wide border-2 border-black shadow-[3px_3px_0px_0px_#000] hover:-translate-y-0.5 transition-all neo-btn ${prompt.color} ${prompt.rot}`}
            >
              {prompt.text}
            </button>
          ))}
        </div>

        {/* Input Bar Form */}
        <form onSubmit={handleSubmit} className="flex items-end space-x-3">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="ASK A BUSINESS QUESTION IN NATURAL LANGUAGE..."
              disabled={disabled}
              rows={1}
              className="w-full px-4 py-3 bg-white border-4 border-black text-black placeholder:text-gray-500 text-xs sm:text-sm font-bold resize-none focus:outline-none focus:bg-[#FFFDF5] focus:shadow-[4px_4px_0px_0px_#000] transition-all max-h-32"
            />
          </div>

          <button
            type="submit"
            disabled={!input.trim() || disabled}
            className="p-3.5 bg-[#FF6B6B] hover:bg-[#ff5252] disabled:opacity-40 text-white font-black border-4 border-black shadow-[4px_4px_0px_0px_#000] neo-btn shrink-0 flex items-center justify-center cursor-pointer"
          >
            <Send className="w-5 h-5 stroke-[3px]" />
          </button>
        </form>
      </div>
    </div>
  );
};
