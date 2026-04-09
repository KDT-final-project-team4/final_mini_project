import { useState } from 'react';
import { ChevronDown, ChevronUp, HelpCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

export function DemoPanel() {
  const [isOpen, setIsOpen] = useState(false);

  const demoScenarios = [
    {
      title: 'FAQ 문의',
      query: '운영시간 알려줘',
      description: 'FAQ Specialist가 매뉴얼/FAQ 기반 답변을 제공합니다.'
    },
    {
      title: '상담원 연결 요청',
      query: '상담원 연결해줘',
      description: '이름과 전화번호를 순서대로 받아 콜백 요청을 등록합니다.'
    },
    {
      title: '사진 확인 필요',
      query: '이거 이상해요',
      description: '시각 정보가 필요하다고 판단되면 사진 업로드를 요청합니다.'
    },
    {
      title: '지원 불가 문의',
      query: '내일 삼성전자 주가 알려줘',
      description: '현재 시스템 범위를 벗어난 문의는 정중히 안내 불가로 응답합니다.'
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
              <h3 className="font-semibold text-white text-sm">데모 가이드</h3>
              <p className="text-xs text-blue-100 mt-0.5">
                멀티에이전트 상담 흐름을 직접 테스트해보세요
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
                💡 위 문장을 직접 입력해서 FAQ / Callback / Vision / Unsupported 흐름을 확인해보세요.
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
        <span>데모 가이드</span>
        {isOpen ? (
          <ChevronDown className="w-4 h-4" />
        ) : (
          <ChevronUp className="w-4 h-4" />
        )}
      </button>
    </div>
  );
}
