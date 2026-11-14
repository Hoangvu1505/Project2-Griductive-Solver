import React from 'react';
import Avatar from './Avatar';
import { X, ShieldAlert, CheckCircle2, Edit3 } from 'lucide-react';

export default function ActionModal({
  isOpen,
  cardData,
  onClose,
  onSubmitVerdict,
  onSetPencil
}) {
  if (!isOpen || !cardData) return null;

  const { coord, name, profession } = cardData;

  return (
    <div className="fixed inset-0 z-50 bg-black/30 backdrop-blur-md flex items-center justify-center p-4 animate-in fade-in duration-150">
      <div
        onClick={(e) => e.stopPropagation()}
        className="bg-white/90 backdrop-blur-2xl border border-slate-200/60 rounded-3xl w-full max-w-sm p-5 shadow-2xl text-slate-800 flex flex-col items-center relative"
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-3 right-3 p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Character Header */}
        <div className="mb-2">
          <Avatar name={name} coord={coord} size={68} />
        </div>
        <div className="text-xs font-mono font-bold text-slate-400 mb-0.5">
          [{coord}]
        </div>
        <h3 className="font-bold text-lg text-slate-800">{name}</h3>
        <p className="text-xs text-slate-500 mb-5">{profession}</p>

        {/* Primary Verdict Call Buttons */}
        <div className="w-full space-y-2 mb-4">
          <button
            onClick={() => {
              onSubmitVerdict(coord, 'CRIMINAL');
              onClose();
            }}
            className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-rose-500 to-pink-500 hover:from-rose-400 hover:to-pink-400 text-white font-semibold py-2.5 px-4 rounded-2xl text-sm transition-all shadow-lg shadow-rose-200/50 active:scale-[0.98] cursor-pointer"
          >
            <ShieldAlert className="w-4 h-4" />
            <span>Call CRIMINAL</span>
          </button>

          <button
            onClick={() => {
              onSubmitVerdict(coord, 'INNOCENT');
              onClose();
            }}
            className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-white font-semibold py-2.5 px-4 rounded-2xl text-sm transition-all shadow-lg shadow-emerald-200/50 active:scale-[0.98] cursor-pointer"
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>Call INNOCENT</span>
          </button>
        </div>

        {/* Pencil Notes Section */}
        <div className="w-full border-t border-slate-200 pt-3 flex items-center justify-between text-xs text-slate-400">
          <span className="flex items-center gap-1">
            <Edit3 className="w-3.5 h-3.5" />
            Pencil Note:
          </span>
          <div className="flex gap-1.5">
            <button
              onClick={() => {
                onSetPencil(coord, 'CRIMINAL');
                onClose();
              }}
              className="px-2 py-1 rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-500 font-medium text-[11px] transition-colors"
            >
              Crim
            </button>
            <button
              onClick={() => {
                onSetPencil(coord, 'INNOCENT');
                onClose();
              }}
              className="px-2 py-1 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-500 font-medium text-[11px] transition-colors"
            >
              Inno
            </button>
            <button
              onClick={() => {
                onSetPencil(coord, null);
                onClose();
              }}
              className="px-2 py-1 rounded-lg bg-slate-50 hover:bg-slate-100 text-slate-400 text-[11px] transition-colors"
            >
              Clear
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
