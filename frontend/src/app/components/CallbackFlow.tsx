import { useState } from 'react';
import { X, Phone, User, CheckCircle, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

type Props = {
  isOpen: boolean;
  onClose: () => void;
  onComplete: (data: { name: string; phone: string }) => void;
};

export function CallbackFlow({ isOpen, onClose, onComplete }: Props) {
  const [step, setStep] = useState(1);
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [errors, setErrors] = useState({ name: '', phone: '' });

  const validateName = (value: string) => {
    if (!value.trim()) {
      return 'Name is required';
    }
    if (value.trim().length < 2) {
      return 'Name must be at least 2 characters';
    }
    return '';
  };

  const validatePhone = (value: string) => {
    if (!value.trim()) {
      return 'Phone number is required';
    }
    const phoneRegex = /^[\d\s\-\+\(\)]+$/;
    if (!phoneRegex.test(value)) {
      return 'Please enter a valid phone number';
    }
    if (value.replace(/\D/g, '').length < 10) {
      return 'Phone number must be at least 10 digits';
    }
    return '';
  };

  const handleNameNext = () => {
    const error = validateName(name);
    if (error) {
      setErrors({ ...errors, name: error });
      return;
    }
    setErrors({ ...errors, name: '' });
    setStep(2);
  };

  const handlePhoneNext = () => {
    const error = validatePhone(phone);
    if (error) {
      setErrors({ ...errors, phone: error });
      return;
    }
    setErrors({ ...errors, phone: '' });
    setStep(3);
  };

  const handleComplete = () => {
    onComplete({ name, phone });
    // Reset form
    setStep(1);
    setName('');
    setPhone('');
    setErrors({ name: '', phone: '' });
  };

  const handleCancel = () => {
    setStep(1);
    setName('');
    setPhone('');
    setErrors({ name: '', phone: '' });
    onClose();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleCancel}
            className="fixed inset-0 bg-black/50 z-40"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-x-4 top-1/2 -translate-y-1/2 md:inset-x-auto md:left-1/2 md:-translate-x-1/2 md:w-full md:max-w-md bg-white rounded-2xl shadow-2xl z-50 overflow-hidden"
          >
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Callback Request</h3>
                <p className="text-sm text-gray-500 mt-0.5">
                  Step {step} of 3
                </p>
              </div>
              <button
                onClick={handleCancel}
                className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            {/* Progress Bar */}
            <div className="h-1 bg-gray-100">
              <motion.div
                className="h-full bg-blue-600"
                initial={{ width: '0%' }}
                animate={{ width: `${(step / 3) * 100}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>

            {/* Content */}
            <div className="p-6">
              <AnimatePresence mode="wait">
                {/* Step 1: Name */}
                {step === 1 && (
                  <motion.div
                    key="step1"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    className="space-y-4"
                  >
                    <div className="w-14 h-14 bg-blue-100 rounded-full flex items-center justify-center mb-2">
                      <User className="w-7 h-7 text-blue-600" />
                    </div>
                    
                    <div>
                      <h4 className="text-base font-semibold text-gray-900 mb-1">
                        What's your name?
                      </h4>
                      <p className="text-sm text-gray-600">
                        Please provide your full name for our records.
                      </p>
                    </div>

                    <div>
                      <input
                        type="text"
                        value={name}
                        onChange={(e) => {
                          setName(e.target.value);
                          if (errors.name) {
                            setErrors({ ...errors, name: '' });
                          }
                        }}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            handleNameNext();
                          }
                        }}
                        placeholder="Enter your full name"
                        autoFocus
                        className={`w-full px-4 py-3 border rounded-lg text-sm focus:outline-none focus:ring-2 transition-colors ${
                          errors.name
                            ? 'border-red-300 focus:ring-red-500'
                            : 'border-gray-300 focus:ring-blue-500'
                        }`}
                      />
                      {errors.name && (
                        <div className="flex items-center gap-2 mt-2 text-red-600">
                          <AlertCircle className="w-4 h-4" />
                          <span className="text-xs">{errors.name}</span>
                        </div>
                      )}
                    </div>
                  </motion.div>
                )}

                {/* Step 2: Phone */}
                {step === 2 && (
                  <motion.div
                    key="step2"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    className="space-y-4"
                  >
                    <div className="w-14 h-14 bg-blue-100 rounded-full flex items-center justify-center mb-2">
                      <Phone className="w-7 h-7 text-blue-600" />
                    </div>
                    
                    <div>
                      <h4 className="text-base font-semibold text-gray-900 mb-1">
                        What's your phone number?
                      </h4>
                      <p className="text-sm text-gray-600">
                        We'll call you at this number within 24 hours.
                      </p>
                    </div>

                    <div>
                      <input
                        type="tel"
                        value={phone}
                        onChange={(e) => {
                          setPhone(e.target.value);
                          if (errors.phone) {
                            setErrors({ ...errors, phone: '' });
                          }
                        }}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            handlePhoneNext();
                          }
                        }}
                        placeholder="+1 (555) 123-4567"
                        autoFocus
                        className={`w-full px-4 py-3 border rounded-lg text-sm focus:outline-none focus:ring-2 transition-colors ${
                          errors.phone
                            ? 'border-red-300 focus:ring-red-500'
                            : 'border-gray-300 focus:ring-blue-500'
                        }`}
                      />
                      {errors.phone && (
                        <div className="flex items-center gap-2 mt-2 text-red-600">
                          <AlertCircle className="w-4 h-4" />
                          <span className="text-xs">{errors.phone}</span>
                        </div>
                      )}
                    </div>
                  </motion.div>
                )}

                {/* Step 3: Confirmation */}
                {step === 3 && (
                  <motion.div
                    key="step3"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    className="space-y-4"
                  >
                    <div className="w-14 h-14 bg-green-100 rounded-full flex items-center justify-center mb-2">
                      <CheckCircle className="w-7 h-7 text-green-600" />
                    </div>
                    
                    <div>
                      <h4 className="text-base font-semibold text-gray-900 mb-1">
                        Confirm your details
                      </h4>
                      <p className="text-sm text-gray-600">
                        Please verify the information below.
                      </p>
                    </div>

                    <div className="space-y-3 bg-gray-50 rounded-lg p-4 border border-gray-200">
                      <div>
                        <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                          Name
                        </label>
                        <p className="text-sm font-medium text-gray-900 mt-1">{name}</p>
                      </div>
                      <div className="border-t border-gray-200 pt-3">
                        <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                          Phone Number
                        </label>
                        <p className="text-sm font-medium text-gray-900 mt-1">{phone}</p>
                      </div>
                    </div>

                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                      <p className="text-xs text-blue-800">
                        A representative will contact you within 24 hours during business hours (9 AM - 6 PM).
                      </p>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Footer */}
            <div className="flex gap-3 px-6 py-4 bg-gray-50 border-t border-gray-200">
              {step > 1 && step < 3 && (
                <button
                  onClick={() => setStep(step - 1)}
                  className="px-4 py-2.5 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 rounded-lg font-medium transition-colors"
                >
                  Back
                </button>
              )}
              
              <button
                onClick={handleCancel}
                className="flex-1 px-4 py-2.5 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 rounded-lg font-medium transition-colors"
              >
                Cancel
              </button>

              {step === 1 && (
                <button
                  onClick={handleNameNext}
                  className="flex-1 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
                >
                  Next
                </button>
              )}

              {step === 2 && (
                <button
                  onClick={handlePhoneNext}
                  className="flex-1 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
                >
                  Next
                </button>
              )}

              {step === 3 && (
                <button
                  onClick={handleComplete}
                  className="flex-1 px-4 py-2.5 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                >
                  <CheckCircle className="w-4 h-4" />
                  Confirm Request
                </button>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
