import { useState, useRef, useEffect } from 'react';
import { MessageList } from './components/MessageList';
import { InputArea } from './components/InputArea';
import { SystemStateIndicator } from './components/SystemStateIndicator';
import { VisionUploadModal } from './components/VisionUploadModal';
import { CallbackFlow } from './components/CallbackFlow';
import { Header } from './components/Header';
import { DemoPanel } from './components/DemoPanel';

export type MessageType = {
  id: string;
  type: 'user' | 'ai' | 'system';
  content: string;
  timestamp: Date;
  structuredData?: {
    type: 'faq' | 'callback' | 'vision' | 'verification' | 'structured';
    data?: any;
  };
};

export type SystemState = 
  | 'idle' 
  | 'analyzing' 
  | 'processing' 
  | 'collecting-info' 
  | 'waiting-image' 
  | 'callback-flow'
  | 'completing';

export default function App() {
  const [messages, setMessages] = useState<MessageType[]>([
    {
      id: '1',
      type: 'ai',
      content: 'CallFlow AI 상담원입니다. 무엇을 도와드릴까요?',
      timestamp: new Date(),
      structuredData: {
        type: 'structured',
        data: {
          greeting: true
        }
      }
    }
  ]);
  
  const [systemState, setSystemState] = useState<SystemState>('idle');
  const [isVisionModalOpen, setIsVisionModalOpen] = useState(false);
  const [isCallbackFlowOpen, setIsCallbackFlowOpen] = useState(false);
  const [isVoiceActive, setIsVoiceActive] = useState(false);
  
  // 🌟 [추가] 백엔드의 상태(기억)를 저장할 변수
  const [langGraphState, setLangGraphState] = useState<any>({});
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 🌟 [핵심] 실제 백엔드 API와 통신하는 함수
  const handleSendMessage = async (message: string) => {
    // 1. 사용자 메시지를 화면에 추가
    const userMessage: MessageType = {
      id: Date.now().toString(),
      type: 'user',
      content: message,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setSystemState('analyzing'); // 로딩 상태 켜기

    try {
      // 2. 백엔드 API 호출 (메시지와 함께 프론트의 '기억'을 전달)
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ 
          message: message,
          state: langGraphState // 프론트가 보관하던 이전 상태
        })
      });

      const data = await response.json();
      
      // 3. 백엔드가 준 새로운 기억으로 업데이트
      setLangGraphState(data.state);

      // 4. 백엔드 응답 메시지를 화면에 추가
      const aiResponse: MessageType = {
        id: Date.now().toString(),
        type: 'ai',
        content: data.response,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, aiResponse]);
      
    } catch (error) {
      console.error("API 호출 에러:", error);
      const errorMsg: MessageType = {
        id: Date.now().toString(),
        type: 'system',
        content: "서버와 연결할 수 없습니다. 백엔드 서버(FastAPI)가 켜져 있는지 확인해주세요.",
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setSystemState('idle'); // 통신 끝나면 로딩 상태 끄기
    }
  };

  // 기존 모의(Mock) 기능들은 통신 에러를 막기 위해 껍데기만 남겨둡니다.
  // (과제 핵심인 텍스트 채팅 로직은 위의 handleSendMessage에서 모두 처리됩니다.)
  const handleVoiceInput = () => {
    setIsVoiceActive(true);
    setTimeout(() => {
      setIsVoiceActive(false);
      handleSendMessage("운영시간 알려줘"); // 음성 테스트용 더미 텍스트
    }, 2000);
  };

  const handleImageUpload = (file: File) => {
    setIsVisionModalOpen(false);
    const systemMessage: MessageType = {
      id: Date.now().toString(),
      type: 'system',
      content: `이미지 업로드됨: ${file.name}`,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, systemMessage]);
  };

  const handleCallbackComplete = (data: { name: string; phone: string }) => {
    setIsCallbackFlowOpen(false);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <Header />
      
      <SystemStateIndicator state={systemState} />
      
      <div className="flex-1 overflow-hidden">
        <MessageList 
          messages={messages} 
          messagesEndRef={messagesEndRef}
        />
      </div>
      
      <InputArea 
        onSendMessage={handleSendMessage}
        onVoiceInput={handleVoiceInput}
        isVoiceActive={isVoiceActive}
        disabled={systemState !== 'idle' && systemState !== 'waiting-image'}
      />
      
      {/* 팝업 모달들은 백엔드 연동 전용으로 껍데기만 유지 */}
      <VisionUploadModal
        isOpen={isVisionModalOpen}
        onClose={() => setIsVisionModalOpen(false)}
        onUpload={handleImageUpload}
      />
      
      <CallbackFlow
        isOpen={isCallbackFlowOpen}
        onClose={() => setIsCallbackFlowOpen(false)}
        onComplete={handleCallbackComplete}
      />
      
      <DemoPanel />
    </div>
  );
}