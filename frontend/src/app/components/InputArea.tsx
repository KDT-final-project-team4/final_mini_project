import { useState } from 'react';
import { Mic, Send, MicOff } from 'lucide-react';
import { motion } from 'motion/react';

type Props = {
  onSendMessage: (message: string) => void;
  onVoiceInput: () => void;
  isVoiceActive: boolean;
  disabled?: boolean;
};

export function InputArea({ onSendMessage, onVoiceInput, isVoiceActive, disabled }: Props) {
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim() && !disabled) {
      onSendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  const handleVoiceClick = () => {
    if (!disabled) {
      onVoiceInput();
    }
  };

  return (
    <div className="bg-white border-t border-gray-200 px-4 py-4 md:px-6">
      <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
        <div className="flex items-end gap-3">
          {/* Voice Input Button - Primary Action */}
          <button
            type="button"
            onClick={handleVoiceClick}
            disabled={disabled}
            className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center transition-all ${
              isVoiceActive
                ? 'bg-red-600 hover:bg-red-700 animate-pulse'
                : 'bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300'
            } ${disabled ? 'cursor-not-allowed' : 'cursor-pointer'} shadow-lg`}
          >
            {isVoiceActive ? (
              <MicOff className="w-6 h-6 text-white" />
            ) : (
              <Mic className="w-6 h-6 text-white" />
            )}
          </button>

          {/* Voice Active Indicator */}
          {isVoiceActive && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex-1 bg-red-50 border-2 border-red-200 rounded-2xl px-4 py-3 flex items-center gap-3"
            >
              <div className="flex gap-1">
                {[0, 1, 2].map((i) => (
                  <motion.div
                    key={i}
                    className="w-1 bg-red-600 rounded-full"
                    animate={{
                      height: [8, 20, 8],
                    }}
                    transition={{
                      duration: 0.8,
                      repeat: Infinity,
                      delay: i * 0.15,
                    }}
                  />
                ))}
              </div>
              <span className="text-sm font-medium text-red-700">Listening...</span>
            </motion.div>
          )}

          {/* Text Input */}
          {!isVoiceActive && (
            <div className="flex-1 relative">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Type your message or use voice input..."
                disabled={disabled}
                className="w-full pl-4 pr-12 py-3 bg-gray-50 border border-gray-200 rounded-2xl text-sm focus:outline-none focus:border-blue-500 focus:bg-white transition-colors disabled:bg-gray-100 disabled:cursor-not-allowed"
              />
              <button
                type="submit"
                disabled={!inputValue.trim() || disabled}
                className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 flex items-center justify-center rounded-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                <Send className="w-4 h-4 text-white" />
              </button>
            </div>
          )}
        </div>

        {/* Helper Text */}
        <div className="mt-2 px-1 flex items-center justify-between">
          <p className="text-xs text-gray-500">
            Voice-first support system • Press mic to speak
          </p>
          {disabled && (
            <span className="text-xs text-amber-600 font-medium">
              Processing request...
            </span>
          )}
        </div>
      </form>
    </div>
  );
}
