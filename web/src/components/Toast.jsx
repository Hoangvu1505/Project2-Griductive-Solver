import React, { useEffect } from 'react';
import { CheckCircle2, AlertTriangle, XCircle, Lightbulb, X } from 'lucide-react';

export default function Toast({ toast, onClose }) {
  const duration = toast?.duration ?? 4000;

  useEffect(() => {
    if (toast && duration > 0) {
      const timer = setTimeout(onClose, duration);
      return () => clearTimeout(timer);
    }
  }, [toast, onClose, duration]);

  if (!toast) return null;

  const { type, message } = toast;

  let bgClass = 'bg-white/90 backdrop-blur-xl border-slate-200 text-slate-700 shadow-lg';
  let icon = <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0" />;

  if (type === 'ACCEPTED') {
    bgClass = 'bg-emerald-50/90 backdrop-blur-xl border-emerald-300 text-emerald-800 shadow-lg shadow-emerald-100/50';
    icon = <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0" />;
  } else if (type === 'NOT_PROVABLE') {
    bgClass = 'bg-amber-50/90 backdrop-blur-xl border-amber-300 text-amber-800 shadow-lg shadow-amber-100/50';
    icon = <AlertTriangle className="w-5 h-5 text-amber-500 shrink-0" />;
  } else if (type === 'CONTRADICTED') {
    bgClass = 'bg-rose-50/90 backdrop-blur-xl border-rose-300 text-rose-800 shadow-lg shadow-rose-100/50';
    icon = <XCircle className="w-5 h-5 text-rose-500 shrink-0" />;
  } else if (type === 'HINT') {
    bgClass = 'bg-cyan-50/90 backdrop-blur-xl border-cyan-300 text-cyan-800 shadow-lg shadow-cyan-100/50';
    icon = <Lightbulb className="w-5 h-5 text-cyan-500 shrink-0" />;
  }

  return (
    <div className="fixed bottom-6 left-1/2 transform -translate-x-1/2 z-50 max-w-lg w-[90%] md:w-auto animate-in slide-in-from-bottom-5 duration-200">
      <div className={`border rounded-2xl p-3.5 shadow-2xl flex items-center justify-between gap-3 text-xs md:text-sm font-medium ${bgClass}`}>
        <div className="flex items-center gap-2.5">
          {icon}
          <span>{message}</span>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded-lg hover:bg-black/5 text-current transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
