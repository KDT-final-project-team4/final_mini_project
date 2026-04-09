import { MessageType } from '../App';
import { CheckCircle, Info } from 'lucide-react';
import { format } from 'date-fns';

type Props = {
  message: MessageType;
};

export function MessageBubble({ message }: Props) {
  const isUser = message.type === 'user';
  const isSystem = message.type === 'system';

  if (isSystem) {
    return (
      <div className="flex items-center justify-center gap-2 py-2">
        <div className="flex items-center gap-2 bg-gray-100 text-gray-600 px-4 py-2 rounded-full text-sm whitespace-pre-line">
          <Info className="w-4 h-4" />
          <span>{message.content}</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex flex-col max-w-[85%] md:max-w-[75%] ${isUser ? 'items-end' : 'items-start'}`}>
        {/* Message Bubble */}
        <div
          className={`rounded-2xl px-4 py-3 ${
            isUser
              ? 'bg-blue-600 text-white rounded-br-sm'
              : 'bg-white border border-gray-200 text-gray-900 rounded-bl-sm shadow-sm'
          }`}
        >
          {/* Main Content */}
          <p className={`text-sm leading-relaxed whitespace-pre-line ${isUser ? '' : 'text-gray-800'}`}>
            {message.content}
          </p>

          {/* Structured Data - FAQ */}
          {message.structuredData?.type === 'faq' && message.structuredData.data && (
            <div className="mt-3 pt-3 border-t border-gray-100">
              <h4 className="font-semibold text-sm text-gray-900 mb-2">
                {message.structuredData.data.title}
              </h4>
              <ul className="space-y-1.5">
                {message.structuredData.data.steps.map((step: string, idx: number) => (
                  <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                    <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <span>{step}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Structured Data - Suggestions */}
          {message.structuredData?.type === 'structured' && 
           message.structuredData.data?.suggestions && (
            <div className="mt-3 pt-3 border-t border-gray-100">
              <p className="text-xs font-medium text-gray-600 mb-2">Quick Actions:</p>
              <div className="flex flex-wrap gap-2">
                {message.structuredData.data.suggestions.map((suggestion: string, idx: number) => (
                  <button
                    key={idx}
                    className="px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg text-xs font-medium transition-colors"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Structured Data - Analysis Results */}
          {message.structuredData?.type === 'structured' && 
           message.structuredData.data?.actions && (
            <div className="mt-3 pt-3 border-t border-gray-100">
              <ul className="space-y-1.5">
                {message.structuredData.data.actions.map((action: string, idx: number) => (
                  <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                    <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <span>{action}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Structured Data - Confirmation */}
          {message.structuredData?.type === 'structured' && 
           message.structuredData.data?.confirmation && (
            <div className="mt-3 pt-3 border-t border-gray-100">
              <div className="flex items-center gap-2 text-sm">
                <span className="font-medium text-gray-700">Reference:</span>
                <code className="bg-gray-100 px-2 py-0.5 rounded text-gray-900 font-mono">
                  {message.structuredData.data.reference}
                </code>
              </div>
            </div>
          )}
        </div>

        {/* Timestamp */}
        <span className={`text-xs text-gray-500 mt-1 px-1 ${isUser ? 'text-right' : 'text-left'}`}>
          {format(message.timestamp, 'HH:mm')}
        </span>
      </div>
    </div>
  );
}
