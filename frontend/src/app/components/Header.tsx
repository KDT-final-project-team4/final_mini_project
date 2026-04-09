import { Bot } from 'lucide-react';

export function Header() {
  return (
    <header className="bg-white border-b border-gray-200 px-4 py-4 md:px-6">
      <div className="flex items-center gap-3 max-w-4xl mx-auto">
        <div className="flex items-center justify-center w-10 h-10 bg-blue-600 rounded-lg">
          <Bot className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="text-lg font-semibold text-gray-900">CallFlow AI</h1>
          <p className="text-xs text-gray-500">Multi-Agent 고객 서비스 시스템</p>
        </div>
      </div>
    </header>
  );
}
