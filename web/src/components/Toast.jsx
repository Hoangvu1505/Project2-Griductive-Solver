import React, { useEffect } from 'react';
import { CheckCircle2, AlertTriangle, XCircle, Lightbulb, X } from 'lucide-react';

export default function Toast({ toast, onClose }) {
  if (!toast) return null;

  const { type, message, duration = 4000 } = toast;

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(onClose, duration);
      return () => clearTimeout(timer);
    }
  }, [toast, onClose, duration]);

  let bgClass = 'bg-[#241f1b] border-[#473b32] text-[#f2ece6]';
  let icon = <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />;

  if (type === 'ACCEPTED') {
    bgClass = 'bg-[#1b2b20] border-emerald-600/60 text-[#d8f3dc] shadow-emerald-950/40';
    icon = <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />;
  } else if (type === 'NOT_PROVABLE') {
    bgClass = 'bg-[#3b2b1a] border-amber-600/60 text-[#ffeedd] shadow-amber-950/40';
    icon = <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0" />;
  } else if (type === 'CONTRADICTED') {
    bgClass = 'bg-[#3b191c] border-red-600/60 text-[#ffd8dc] shadow-red-950/40';
    icon = <XCircle className="w-5 h-5 text-red-400 shrink-0" />;
  } else if (type === 'HINT') {
    bgClass = 'bg-[#182e3b] border-cyan-600/60 text-[#e0f7ff] shadow-cyan-950/40';
    icon = <Lightbulb className="w-5 h-5 text-cyan-400 shrink-0" />;
  }

  return (
    <div className="fixed bottom-6 left-1/2 transform -translate-x-1/2 z-50 max-w-lg w-[90%] md:w-auto animate-in slide-in-from-bottom-5 duration-200">
      <div className={`border rounded-xl p-3.5 shadow-2xl flex items-center justify-between gap-3 text-xs md:text-sm font-medium ${bgClass}`}>
        <div className="flex items-center gap-2.5">
          {icon}
          <span>{message}</span>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded-md hover:bg-black/20 text-current transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

