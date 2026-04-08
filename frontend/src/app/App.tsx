import { useState, useRef, useEffect } from "react";
import { MessageList } from "./components/MessageList";
import { InputArea } from "./components/InputArea";
import { SystemStateIndicator } from "./components/SystemStateIndicator";
import { VisionUploadModal } from "./components/VisionUploadModal";
import { Header } from "./components/Header";
import { DemoPanel } from "./components/DemoPanel";

export type MessageType = {
  id: string;
  type: "user" | "ai" | "system";
  content: string;
  timestamp: Date;
  structuredData?: {
    type: "faq" | "callback" | "vision" | "verification" | "structured";
    data?: any;
  };
};

export type SystemState =
  | "idle"
  | "analyzing"
  | "processing"
  | "collecting-info"
  | "waiting-image"
  | "callback-flow"
  | "completing";

type SessionState = {
  collected_name: string | null;
  collected_phone: string | null;
  active_flow: string | null;
};

type ChatApiResponse = {
  response: string;
  intent?: string | null;
  next_action?: string | null;
  session_state: SessionState;
};

const API_BASE_URL = "http://127.0.0.1:8000";

export default function App() {
  const [messages, setMessages] = useState<MessageType[]>([
    {
      id: "1",
      type: "ai",
      content: "Welcome to CallFlow AI Support. How can I assist you today?",
      timestamp: new Date(),
      structuredData: {
        type: "structured",
        data: {
          greeting: true,
        },
      },
    },
  ]);

  const [systemState, setSystemState] = useState<SystemState>("idle");
  const [isVisionModalOpen, setIsVisionModalOpen] = useState(false);
  const [isVoiceActive, setIsVoiceActive] = useState(false);

  const [sessionState, setSessionState] = useState<SessionState>({
    collected_name: null,
    collected_phone: null,
    active_flow: null,
  });

  const [lastNextAction, setLastNextAction] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  async function sendMessageToBackend(
    message: string,
    currentSessionState: SessionState
  ): Promise<ChatApiResponse> {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        session_state: currentSessionState,
      }),
    });

    if (!response.ok) {
      throw new Error("서버 요청 실패");
    }

    return response.json();
  }

  const handleSendMessage = async (message: string) => {
    const userMessage: MessageType = {
      id: Date.now().toString(),
      type: "user",
      content: message,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setSystemState("analyzing");

    try {
      // 이전 턴 상태를 기반으로 이름/전화번호를 sessionState에 반영
      const updatedSessionState: SessionState = { ...sessionState };

      if (lastNextAction === "ask_name") {
        updatedSessionState.collected_name = message;
      }

      if (lastNextAction === "ask_phone") {
        updatedSessionState.collected_phone = message;
      }

      const data = await sendMessageToBackend(message, updatedSessionState);

      setSessionState(data.session_state);
      setLastNextAction(data.next_action ?? null);

      const aiMessage: MessageType = {
        id: (Date.now() + 1).toString(),
        type: "ai",
        content: data.response,
        timestamp: new Date(),
        structuredData: {
          type:
            data.intent === "faq"
              ? "faq"
              : data.intent === "callback"
              ? "callback"
              : data.next_action === "trigger_vision"
              ? "vision"
              : "structured",
        },
      };

      setMessages((prev) => [...prev, aiMessage]);

      // UI 상태 반영
      if (data.next_action === "trigger_vision") {
        setSystemState("waiting-image");
        setIsVisionModalOpen(true);
      } else if (
        data.next_action === "ask_name" ||
        data.next_action === "ask_phone"
      ) {
        setSystemState("collecting-info");
      } else {
        setSystemState("idle");
      }
    } catch (error) {
      console.error(error);

      const errorMessage: MessageType = {
        id: (Date.now() + 1).toString(),
        type: "ai",
        content: "서버와 통신 중 문제가 발생했습니다.",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
      setSystemState("idle");
    }
  };

  const handleVoiceInput = () => {
    setIsVoiceActive(true);

    // 현재는 음성 입력 mock
    setTimeout(() => {
      setIsVoiceActive(false);
      const voiceMessage = "I need help with a refund";
      handleSendMessage(voiceMessage);
    }, 2000);
  };

  const handleImageUpload = (file: File) => {
    setIsVisionModalOpen(false);
    setSystemState("processing");

    const systemMessage: MessageType = {
      id: Date.now().toString(),
      type: "system",
      content: `Image uploaded: ${file.name}`,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, systemMessage]);

    // 현재는 업로드 후 분석 mock
    setTimeout(() => {
      const aiResponse: MessageType = {
        id: Date.now().toString(),
        type: "ai",
        content:
          "Thank you for uploading the image. This is currently a mock vision flow. In the full version, the backend will analyze the image and return a structured result.",
        timestamp: new Date(),
        structuredData: {
          type: "vision",
          data: {
            mock: true,
            filename: file.name,
          },
        },
      };
      setMessages((prev) => [...prev, aiResponse]);
      setSystemState("idle");
    }, 1500);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <Header />

      <SystemStateIndicator state={systemState} />

      <div className="flex-1 overflow-hidden">
        <MessageList messages={messages} messagesEndRef={messagesEndRef} />
      </div>

      <InputArea
        onSendMessage={handleSendMessage}
        onVoiceInput={handleVoiceInput}
        isVoiceActive={isVoiceActive}
        disabled={systemState === "processing" || systemState === "analyzing" || systemState === "completing"}
      />

      <VisionUploadModal
        isOpen={isVisionModalOpen}
        onClose={() => {
          setIsVisionModalOpen(false);
          setSystemState("idle");
        }}
        onUpload={handleImageUpload}
      />

      <DemoPanel />
    </div>
  );
}