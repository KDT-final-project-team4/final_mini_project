import { useState, useRef, useEffect } from "react";
import { MessageList } from "./components/MessageList";
import { InputArea } from "./components/InputArea";
import { SystemStateIndicator } from "./components/SystemStateIndicator";
import { VisionUploadModal } from "./components/VisionUploadModal";
import { CallbackFlow } from "./components/CallbackFlow";
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

export default function App() {
    const [messages, setMessages] = useState<MessageType[]>([
        {
            id: "1",
            type: "ai",
            content:
                "Welcome to CallFlow AI Support. How can I assist you today?",
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
    const [isCallbackFlowOpen, setIsCallbackFlowOpen] = useState(false);
    const [isVoiceActive, setIsVoiceActive] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const simulateAIResponse = (userMessage: string) => {
        const lowerMessage = userMessage.toLowerCase();

        // Simulate processing
        setSystemState("analyzing");

        setTimeout(() => {
            let aiResponse: MessageType;

            // FAQ Response
            if (
                lowerMessage.includes("refund") ||
                lowerMessage.includes("return")
            ) {
                setSystemState("processing");
                setTimeout(() => {
                    aiResponse = {
                        id: Date.now().toString(),
                        type: "ai",
                        content: "I can help you with refund requests.",
                        timestamp: new Date(),
                        structuredData: {
                            type: "faq",
                            data: {
                                title: "Refund Policy",
                                steps: [
                                    "Refunds are processed within 5-7 business days",
                                    "Original payment method will be credited",
                                    "Items must be returned in original condition",
                                ],
                            },
                        },
                    };
                    setMessages((prev) => [...prev, aiResponse]);
                    setSystemState("idle");
                }, 1500);
            }
            // Callback Flow
            else if (
                lowerMessage.includes("call") ||
                lowerMessage.includes("speak") ||
                lowerMessage.includes("talk")
            ) {
                setSystemState("collecting-info");
                setTimeout(() => {
                    aiResponse = {
                        id: Date.now().toString(),
                        type: "ai",
                        content:
                            "I understand you would like to speak with a representative. Let me collect your information for a callback.",
                        timestamp: new Date(),
                        structuredData: {
                            type: "callback",
                        },
                    };
                    setMessages((prev) => [...prev, aiResponse]);
                    setSystemState("callback-flow");
                    setIsCallbackFlowOpen(true);
                }, 1500);
            }
            // Vision Trigger
            else if (
                lowerMessage.includes("damaged") ||
                lowerMessage.includes("broken") ||
                lowerMessage.includes("defect")
            ) {
                setSystemState("waiting-image");
                setTimeout(() => {
                    aiResponse = {
                        id: Date.now().toString(),
                        type: "ai",
                        content:
                            "I need to assess the issue visually. Please upload an image of the damaged item.",
                        timestamp: new Date(),
                        structuredData: {
                            type: "vision",
                        },
                    };
                    setMessages((prev) => [...prev, aiResponse]);
                    setIsVisionModalOpen(true);
                }, 1500);
            }
            // Generic Response
            else {
                setSystemState("processing");
                setTimeout(() => {
                    aiResponse = {
                        id: Date.now().toString(),
                        type: "ai",
                        content:
                            "I'm analyzing your request. Our support system is designed to provide structured assistance.",
                        timestamp: new Date(),
                        structuredData: {
                            type: "structured",
                            data: {
                                suggestions: [
                                    "Request a callback",
                                    "Check refund status",
                                    "Report damaged item",
                                ],
                            },
                        },
                    };
                    setMessages((prev) => [...prev, aiResponse]);
                    setSystemState("idle");
                }, 1500);
            }
        }, 800);
    };

    const handleSendMessage = async (message: string) => {
        const userMessage: MessageType = {
            id: Date.now().toString(),
            type: "user",
            content: message,
            timestamp: new Date(),
        };
        setMessages((prev) => [...prev, userMessage]);

        // 백엔드로 바로 전달
        try {
            const response = await fetch("http://localhost:8000/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message }),
            });
            const data = await response.json();
            // 백엔드 응답을 메시지로 추가
            const aiMessage: MessageType = {
                id: Date.now().toString(),
                type: "ai",
                content: data.response || "",
                timestamp: new Date(),
                // 필요시 structuredData 등 추가
            };
            setMessages((prev) => [...prev, aiMessage]);
        } catch (error) {
            setMessages((prev) => [
                ...prev,
                {
                    id: Date.now().toString(),
                    type: "system",
                    content: "서버와 통신에 실패했습니다.",
                    timestamp: new Date(),
                },
            ]);
        }
    };
    const handleVoiceInput = () => {
        setIsVoiceActive(true);

        // Simulate voice recognition
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

        setTimeout(() => {
            const aiResponse: MessageType = {
                id: Date.now().toString(),
                type: "ai",
                content:
                    "Thank you for uploading the image. I can see the damage to the item. Based on our analysis, you are eligible for a full refund or replacement.",
                timestamp: new Date(),
                structuredData: {
                    type: "structured",
                    data: {
                        analysis: "Item damage confirmed",
                        actions: [
                            "Full refund available",
                            "Replacement option available",
                            "No return shipping fee",
                        ],
                    },
                },
            };
            setMessages((prev) => [...prev, aiResponse]);
            setSystemState("idle");
        }, 2000);
    };

    const handleCallbackComplete = (data: { name: string; phone: string }) => {
        setIsCallbackFlowOpen(false);
        setSystemState("completing");

        const systemMessage: MessageType = {
            id: Date.now().toString(),
            type: "system",
            content: `Callback request submitted for ${data.name}`,
            timestamp: new Date(),
        };
        setMessages((prev) => [...prev, systemMessage]);

        setTimeout(() => {
            const aiResponse: MessageType = {
                id: Date.now().toString(),
                type: "ai",
                content: `Your callback request has been confirmed. A representative will contact you at ${data.phone} within 24 hours.`,
                timestamp: new Date(),
                structuredData: {
                    type: "structured",
                    data: {
                        confirmation: true,
                        reference: `CB-${Date.now().toString().slice(-6)}`,
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
                <MessageList
                    messages={messages}
                    messagesEndRef={messagesEndRef}
                />
            </div>

            <InputArea
                onSendMessage={handleSendMessage}
                onVoiceInput={handleVoiceInput}
                isVoiceActive={isVoiceActive}
                disabled={
                    systemState !== "idle" && systemState !== "waiting-image"
                }
            />

            <VisionUploadModal
                isOpen={isVisionModalOpen}
                onClose={() => {
                    setIsVisionModalOpen(false);
                    setSystemState("idle");
                }}
                onUpload={handleImageUpload}
            />

            <CallbackFlow
                isOpen={isCallbackFlowOpen}
                onClose={() => {
                    setIsCallbackFlowOpen(false);
                    setSystemState("idle");
                }}
                onComplete={handleCallbackComplete}
            />

            <DemoPanel />
        </div>
    );
}
