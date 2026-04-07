import { MessageType } from '../App';
import { MessageBubble } from './MessageBubble';
import { motion } from 'motion/react';

type Props = {
  messages: MessageType[];
  messagesEndRef: React.RefObject<HTMLDivElement>;
};

export function MessageList({ messages, messagesEndRef }: Props) {
  return (
    <div className="h-full overflow-y-auto px-4 py-6 md:px-6">
      <div className="max-w-4xl mx-auto space-y-4">
        {messages.map((message, index) => (
          <motion.div
            key={message.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
          >
            <MessageBubble message={message} />
          </motion.div>
        ))}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}
