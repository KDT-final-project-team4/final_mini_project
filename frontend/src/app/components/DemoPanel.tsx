import { useState } from 'react';
import { ChevronDown, ChevronUp, HelpCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

export function DemoPanel() {
  const [isOpen, setIsOpen] = useState(false);

  const demoScenarios = [
    {
      title: 'FAQ Response',
      query: 'I need a refund',
      description: 'Triggers structured FAQ response with steps'
    },
    {
      title: 'Callback Request',
      query: 'I want to speak with someone',
      description: 'Initiates callback flow with multi-step form'
    },
    {
      title: 'Vision Analysis',
      query: 'I received a damaged item',
      description: 'Requests image upload for visual inspection'
    },
    {
      title: 'General Query',
      query: 'How can you help me?',
      description: 'Shows structured suggestions and system capabilities'
    }
  ];

  return (
    <div className="fixed bottom-20 right-4 z-30 md:bottom-24 md:right-6">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="mb-3 bg-white rounded-xl shadow-xl border border-gray-200 overflow-hidden w-72"
          >
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-3">
              <h3 className="font-semibold text-white text-sm">Try Demo Scenarios</h3>
              <p className="text-xs text-blue-100 mt-0.5">
                Test different AI agent flows
              </p>
            </div>
            
            <div className="p-3 space-y-2 max-h-80 overflow-y-auto">
              {demoScenarios.map((scenario, idx) => (
                <div
                  key={idx}
                  className="p-3 bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 cursor-pointer transition-colors"
                >
                  <div className="flex items-start gap-2">
                    <HelpCircle className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {scenario.title}
                      </p>
                      <p className="text-xs text-gray-600 mt-0.5">
                        "{scenario.query}"
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {scenario.description}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="px-3 py-2.5 bg-blue-50 border-t border-blue-100">
              <p className="text-xs text-blue-800">
                💡 Type or speak any of these queries to see the system in action
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <button
        onClick={() => setIsOpen(!isOpen)}
        className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-full shadow-lg px-4 py-3 flex items-center gap-2 font-medium text-sm transition-all hover:shadow-xl"
      >
        <HelpCircle className="w-5 h-5" />
        <span>Demo Guide</span>
        {isOpen ? (
          <ChevronDown className="w-4 h-4" />
        ) : (
          <ChevronUp className="w-4 h-4" />
        )}
      </button>
    </div>
  );
}
