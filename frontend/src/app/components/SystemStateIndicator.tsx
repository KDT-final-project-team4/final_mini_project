import { SystemState } from '../App';
import { Loader2, CheckCircle2, Image, Phone, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

type Props = {
  state: SystemState;
};

const stateConfig = {
  idle: { icon: null, text: '', color: '' },
  analyzing: { 
    icon: Loader2, 
    text: 'Analyzing request...', 
    color: 'text-blue-600',
    animate: true 
  },
  processing: { 
    icon: Loader2, 
    text: 'Processing request...', 
    color: 'text-blue-600',
    animate: true 
  },
  'collecting-info': { 
    icon: Phone, 
    text: 'Collecting user information...', 
    color: 'text-indigo-600',
    animate: false 
  },
  'waiting-image': { 
    icon: Image, 
    text: 'Waiting for image upload...', 
    color: 'text-purple-600',
    animate: false 
  },
  'callback-flow': { 
    icon: Phone, 
    text: 'Callback request in progress...', 
    color: 'text-indigo-600',
    animate: false 
  },
  completing: { 
    icon: CheckCircle2, 
    text: 'Completing request...', 
    color: 'text-green-600',
    animate: false 
  },
};

export function SystemStateIndicator({ state }: Props) {
  const config = stateConfig[state];
  const Icon = config.icon;

  return (
    <AnimatePresence mode="wait">
      {state !== 'idle' && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.2 }}
          className="bg-blue-50 border-b border-blue-100 px-4 py-2.5"
        >
          <div className="flex items-center justify-center gap-2 max-w-4xl mx-auto">
            {Icon && (
              <Icon 
                className={`w-4 h-4 ${config.color} ${config.animate ? 'animate-spin' : ''}`} 
              />
            )}
            <span className={`text-sm font-medium ${config.color}`}>
              {config.text}
            </span>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
