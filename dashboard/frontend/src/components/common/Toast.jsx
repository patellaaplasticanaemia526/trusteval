import { useState, useEffect, createContext, useContext, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, AlertTriangle, XCircle, Info, X } from 'lucide-react';

const ToastContext = createContext(null);

const toastIcons = {
  success: { icon: CheckCircle, color: 'text-emerald-400', border: 'border-emerald-500/30' },
  warning: { icon: AlertTriangle, color: 'text-amber-400', border: 'border-amber-500/30' },
  error: { icon: XCircle, color: 'text-red-400', border: 'border-red-500/30' },
  info: { icon: Info, color: 'text-indigo-400', border: 'border-indigo-500/30' },
};

function ToastItem({ toast, onDismiss }) {
  const config = toastIcons[toast.type] || toastIcons.info;
  const Icon = config.icon;

  useEffect(() => {
    const timer = setTimeout(() => onDismiss(toast.id), toast.duration || 4000);
    return () => clearTimeout(timer);
  }, [toast.id, toast.duration, onDismiss]);

  return (
    <motion.div
      initial={{ x: 400, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: 400, opacity: 0 }}
      transition={{ type: 'spring', damping: 25, stiffness: 200 }}
      className={`flex items-start gap-3 p-4 bg-slate-800 border ${config.border} rounded-xl shadow-xl max-w-sm`}
    >
      <Icon className={`w-5 h-5 shrink-0 mt-0.5 ${config.color}`} />
      <div className="flex-1 min-w-0">
        {toast.title && (
          <p className="text-sm font-semibold text-white">{toast.title}</p>
        )}
        <p className="text-sm text-slate-300">{toast.message}</p>
      </div>
      <button
        onClick={() => onDismiss(toast.id)}
        className="text-slate-500 hover:text-white shrink-0"
      >
        <X className="w-4 h-4" />
      </button>
    </motion.div>
  );
}

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((toast) => {
    const id = Date.now() + Math.random();
    setToasts((prev) => [...prev, { ...toast, id }]);
    return id;
  }, []);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ addToast, removeToast }}>
      {children}
      <div className="fixed top-4 right-4 z-[100] flex flex-col gap-2">
        <AnimatePresence>
          {toasts.map((toast) => (
            <ToastItem key={toast.id} toast={toast} onDismiss={removeToast} />
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) {
    return {
      addToast: () => {},
      removeToast: () => {},
      success: () => {},
      error: () => {},
      warning: () => {},
      info: () => {},
    };
  }
  return {
    ...ctx,
    success: (message, title) => ctx.addToast({ type: 'success', message, title }),
    error: (message, title) => ctx.addToast({ type: 'error', message, title }),
    warning: (message, title) => ctx.addToast({ type: 'warning', message, title }),
    info: (message, title) => ctx.addToast({ type: 'info', message, title }),
  };
}

export default ToastItem;
