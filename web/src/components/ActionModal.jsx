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
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in duration-150">
      <div
        onClick={(e) => e.stopPropagation()}
        className="bg-[#241f1b] border border-[#3d342d] rounded-2xl w-full max-w-sm p-5 shadow-2xl text-[#f2ece6] flex flex-col items-center relative"
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-3 right-3 p-1 rounded-lg text-[#8a7f74] hover:text-[#f2ece6] hover:bg-[#332b24] transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Character Header */}
        <div className="mb-2">
          <Avatar name={name} coord={coord} size={68} />
        </div>
        <div className="text-xs font-mono font-bold text-[#8a7f74] mb-0.5">
          [{coord}]
        </div>
        <h3 className="font-bold text-lg text-[#f2ece6]">{name}</h3>
        <p className="text-xs text-[#9c8f82] mb-5">{profession}</p>

        {/* Primary Verdict Call Buttons */}
        <div className="w-full space-y-2 mb-4">
          <button
            onClick={() => {
              onSubmitVerdict(coord, 'CRIMINAL');
              onClose();
            }}
            className="w-full flex items-center justify-center gap-2 bg-[#8c1d28] hover:bg-[#a62532] text-white font-semibold py-2.5 px-4 rounded-xl text-sm transition-all shadow-md active:scale-[0.98]"
          >
            <ShieldAlert className="w-4 h-4" />
            <span>Call CRIMINAL</span>
          </button>

          <button
            onClick={() => {
              onSubmitVerdict(coord, 'INNOCENT');
              onClose();
            }}
            className="w-full flex items-center justify-center gap-2 bg-[#20633f] hover:bg-[#287d4f] text-white font-semibold py-2.5 px-4 rounded-xl text-sm transition-all shadow-md active:scale-[0.98]"
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>Call INNOCENT</span>
          </button>
        </div>

        {/* Pencil Notes Section */}
        <div className="w-full border-t border-[#383029] pt-3 flex items-center justify-between text-xs text-[#8a7f74]">
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
              className="px-2 py-1 rounded bg-[#332a24] hover:bg-[#42372f] text-red-400 font-medium text-[11px]"
            >
              Crim
            </button>
            <button
              onClick={() => {
                onSetPencil(coord, 'INNOCENT');
                onClose();
              }}
              className="px-2 py-1 rounded bg-[#332a24] hover:bg-[#42372f] text-emerald-400 font-medium text-[11px]"
            >
              Inno
            </button>
            <button
              onClick={() => {
                onSetPencil(coord, null);
                onClose();
              }}
              className="px-2 py-1 rounded bg-[#332a24] hover:bg-[#42372f] text-[#8a7f74] text-[11px]"
            >
              Clear
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

