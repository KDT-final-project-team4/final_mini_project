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

type BackendChatResponse = {
  session_id: string;
  final_response: string;
  intent: 'faq' | 'callback' | 'vision' | 'unknown' | null;
  next_action:
    | 'run_faq'
    | 'ask_name'
    | 'ask_phone'
    | 'run_callback'
    | 'run_vision'
    | 'finish'
    | null;
  system_state?: SystemState;
  open_callback_flow?: boolean;
  open_vision_modal?: boolean;
  message?: {
    type?: 'ai' | 'system';
    content?: string;
    structuredData?: MessageType['structuredData'];
  };
  error?: string | null;
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
const CHAT_API_URL = `${API_BASE_URL}/chat`;

export default function App() {
  const [messages, setMessages] = useState<MessageType[]>([
    {
      id: '1',
      type: 'ai',
      content: 'Welcome to CallFlow AI Support. How can I assist you today?',
      timestamp: new Date(),
      structuredData: {
        type: 'structured',
        data: {
          greeting: true,
        },
      },
    },
  ]);

  const [systemState, setSystemState] = useState<SystemState>('idle');
  const [isVisionModalOpen, setIsVisionModalOpen] = useState(false);
  const [isCallbackFlowOpen, setIsCallbackFlowOpen] = useState(false);
  const [isVoiceActive, setIsVoiceActive] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(() => sessionStorage.getItem('chat_session_id'));
  const sessionIdRef = useRef<string | null>(sessionStorage.getItem('chat_session_id'));
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const saveSessionId = (newSessionId: string) => {
    sessionIdRef.current = newSessionId;
    setSessionId(newSessionId);
    sessionStorage.setItem('chat_session_id', newSessionId);
  };

  const clearSessionId = () => {
    sessionIdRef.current = null;
    setSessionId(null);
    sessionStorage.removeItem('chat_session_id');
  };

  const createUserMessage = (content: string): MessageType => ({
    id: `${Date.now()}-${Math.random()}`,
    type: 'user',
    content,
    timestamp: new Date(),
  });

  const createSystemMessage = (content: string): MessageType => ({
    id: `${Date.now()}-${Math.random()}`,
    type: 'system',
    content,
    timestamp: new Date(),
  });

  const createAiMessageFromResponse = (response: BackendChatResponse): MessageType | null => {
    const content = response.message?.content || response.final_response;
    if (!content) {
      return null;
    }

    return {
      id: `${Date.now()}-${Math.random()}`,
      type: response.message?.type === 'system' ? 'system' : 'ai',
      content,
      timestamp: new Date(),
      structuredData: response.message?.structuredData,
    };
  };

  const applyBackendUi = (response: BackendChatResponse, allowModalOpen: boolean) => {
    setSystemState(response.system_state || 'idle');

    if (!allowModalOpen) {
      return;
    }

    if (response.open_callback_flow) {
      setIsCallbackFlowOpen(true);
    }

    if (response.open_vision_modal) {
      setIsVisionModalOpen(true);
    }
  };

  const sendChatRequest = async (
    message: string,
    options?: {
      appendUserMessage?: boolean;
      appendAiMessage?: boolean;
      allowModalOpen?: boolean;
      loadingState?: SystemState | null;
    }
  ) => {
    const appendUserMessage = options?.appendUserMessage ?? true;
    const appendAiMessage = options?.appendAiMessage ?? true;
    const allowModalOpen = options?.allowModalOpen ?? true;
    const loadingState = options?.loadingState ?? 'analyzing';

    if (appendUserMessage) {
      setMessages((prev) => [...prev, createUserMessage(message)]);
    }

    if (loadingState) {
      setSystemState(loadingState);
    }

    const response = await fetch(CHAT_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        session_id: sessionIdRef.current,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data: BackendChatResponse = await response.json();

    if (data.session_id) {
      saveSessionId(data.session_id);
    }

    if (appendAiMessage) {
      const aiMessage = createAiMessageFromResponse(data);
      if (aiMessage) {
        setMessages((prev) => [...prev, aiMessage]);
      }
    }

    applyBackendUi(data, allowModalOpen);

    return data;
  };

  const handleSendMessage = async (message: string) => {
    try {
      await sendChatRequest(message, {
        appendUserMessage: true,
        appendAiMessage: true,
        allowModalOpen: true,
        loadingState: 'analyzing',
      });
    } catch (error) {
      setSystemState('idle');
      setMessages((prev) => [
        ...prev,
        createSystemMessage('서버 연결 중 오류가 발생했어요. 잠시 후 다시 시도해주세요.'),
      ]);
    }
  };

  const handleVoiceInput = () => {
    setIsVoiceActive(true);

    setTimeout(() => {
      setIsVoiceActive(false);
      const voiceMessage = '운영시간 알려줘';
      void handleSendMessage(voiceMessage);
    }, 1500);
  };

  const handleImageUpload = (file: File) => {
    // 현재 백엔드는 이미지 업로드 API가 없으므로,
    // 기존 프론트 UX를 유지하는 로컬 처리 방식으로 둔다.
    setIsVisionModalOpen(false);
    setSystemState('processing');

    const systemMessage: MessageType = {
      id: `${Date.now()}-${Math.random()}`,
      type: 'system',
      content: `이미지 업로드 완료: ${file.name}`,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, systemMessage]);

    setTimeout(() => {
      const aiResponse: MessageType = {
        id: `${Date.now()}-${Math.random()}`,
        type: 'ai',
        content: '이미지를 확인했어요. 현재 업로드 기능은 프론트 데모 방식으로 유지되고 있습니다.',
        timestamp: new Date(),
        structuredData: {
          type: 'structured',
          data: {
            actions: ['이미지 업로드 확인 완료', '후속 비전 API 연동 가능', '현재는 데모 결과 표시'],
          },
        },
      };
      setMessages((prev) => [...prev, aiResponse]);
      setSystemState('idle');
    }, 1200);
  };

  const handleCallbackComplete = async (data: { name: string; phone: string }) => {
    setIsCallbackFlowOpen(false);
    setSystemState('completing');

    try {
      // 현재 프론트 modal UX를 유지하기 위해
      // 이름/전화번호를 백엔드에 순차적으로 전송한다.
      await sendChatRequest(data.name, {
        appendUserMessage: false,
        appendAiMessage: false,
        allowModalOpen: false,
        loadingState: null,
      });

      await sendChatRequest(data.phone, {
        appendUserMessage: false,
        appendAiMessage: true,
        allowModalOpen: true,
        loadingState: 'completing',
      });
    } catch (error) {
      setSystemState('idle');
      setMessages((prev) => [
        ...prev,
        createSystemMessage('콜백 요청 처리 중 오류가 발생했어요. 다시 시도해주세요.'),
      ]);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <Header />

      <SystemStateIndicator state={systemState} />

      <div className="flex-1 overflow-hidden">
        <MessageList messages={messages} messagesEndRef={messagesEndRef} />
      </div>

      <InputArea
        onSendMessage={(message) => {
          void handleSendMessage(message);
        }}
        onVoiceInput={handleVoiceInput}
        isVoiceActive={isVoiceActive}
        disabled={systemState !== 'idle' && systemState !== 'waiting-image'}
      />

      <VisionUploadModal
        isOpen={isVisionModalOpen}
        onClose={() => {
          setIsVisionModalOpen(false);
          setSystemState('idle');
        }}
        onUpload={handleImageUpload}
      />

      <CallbackFlow
        isOpen={isCallbackFlowOpen}
        onClose={() => {
          setIsCallbackFlowOpen(false);
          setSystemState('idle');
          // 현재 백엔드에는 별도 취소 API가 없으므로,
          // modal 취소 시 세션을 비워 다음 요청이 새 세션으로 시작되게 처리
          clearSessionId();
        }}
        onComplete={(data) => {
          void handleCallbackComplete(data);
        }}
      />

      <DemoPanel />
    </div>
  );
}