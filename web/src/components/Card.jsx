import React from 'react';
import Avatar from './Avatar';
import { Star, ShieldAlert, CheckCircle2 } from 'lucide-react';

export default function Card({
  cardData,
  isHighlightedRef = false,
  isHighlightedHint = false,
  isSelectedClue = false,
  pencilNote = null, // 'CRIMINAL' | 'INNOCENT' | null
  onClick
}) {
  const { coord, name, profession, is_revealed, status, clue } = cardData;

  // Visual status classes
  let borderClass = 'border-white/60 hover:border-white/80';
  let bgClass = 'bg-white/70 backdrop-blur-xl';
  let shadowClass = 'shadow-[0_8px_32px_rgba(0,0,0,0.06)]';

  if (is_revealed) {
    if (status === 'CRIMINAL') {
      borderClass = 'border-rose-400/70';
      bgClass = 'bg-rose-50/80 backdrop-blur-xl';
      shadowClass = 'shadow-[0_0_20px_rgba(244,63,94,0.15)]';
    } else {
      borderClass = 'border-emerald-400/70';
      bgClass = 'bg-emerald-50/80 backdrop-blur-xl';
      shadowClass = 'shadow-[0_0_20px_rgba(16,185,129,0.15)]';
    }
  }

  if (isHighlightedRef) {
    borderClass = 'border-amber-400 ring-2 ring-amber-300/60';
    shadowClass = 'shadow-[0_0_24px_rgba(245,158,11,0.3)]';
  }

  if (isHighlightedHint) {
    borderClass = isHighlightedRef
      ? 'border-cyan-400 ring-2 ring-amber-300/60 animate-pulse'
      : 'border-cyan-400 ring-4 ring-cyan-300/60 animate-pulse';
    shadowClass = 'shadow-[0_0_28px_rgba(6,182,212,0.4)]';
  }

  if (isSelectedClue) {
    borderClass += ' outline-2 outline-offset-2 outline-violet-400';
  }

  return (
    <div
      onClick={() => onClick(coord)}
      className={`relative select-none cursor-pointer rounded-2xl border p-2 flex flex-col justify-between transition-all duration-300 transform hover:-translate-y-1 hover:shadow-[0_12px_40px_rgba(0,0,0,0.1)] active:scale-[0.97] min-h-[140px] md:min-h-[155px] ${bgClass} ${borderClass} ${shadowClass}`}
    >
      {/* Top Bar: Coordinate and Status/Badge Icon */}
      <div className="flex items-center justify-between w-full mb-1">
        <span className="text-[10px] md:text-xs font-semibold tracking-wider text-slate-400">
          {coord}
        </span>

        {is_revealed ? (
          <div className="flex items-center gap-1">
            {status === 'CRIMINAL' ? (
              <span className="text-[10px] uppercase font-bold text-rose-500 flex items-center gap-0.5">
                <ShieldAlert className="w-3 h-3 text-rose-500 inline" />
              </span>
            ) : (
              <span className="text-[10px] uppercase font-bold text-emerald-500 flex items-center gap-0.5">
                <Star className="w-3 h-3 text-emerald-500 inline fill-emerald-500/20" />
              </span>
            )}
          </div>
        ) : pencilNote ? (
          <span className={`text-[9px] font-bold px-1 py-0.5 rounded ${pencilNote === 'CRIMINAL' ? 'bg-rose-100 text-rose-600' : 'bg-emerald-100 text-emerald-600'}`}>
            {pencilNote === 'CRIMINAL' ? 'Crim' : 'Inno'}
          </span>
        ) : null}
      </div>

      {/* Card Body */}
      {is_revealed ? (
        // Revealed Face-Up View
        <div className="flex flex-col flex-1 justify-between items-center text-center">
          <div className="flex flex-col items-center">
            <Avatar name={name} size={22} />
            <div className="text-center font-semibold text-slate-800 text-xs md:text-sm tracking-tight leading-tight mt-0.5">
              {name}
            </div>
            <div className="text-center text-[10px] md:text-[11px] text-slate-500 leading-tight mb-1">
              {profession}
            </div>
          </div>

          {/* Clue Text Box */}
          <div className="w-full bg-white/50 border border-slate-200/60 rounded-lg p-2 text-center my-auto">
            <p className="text-[11px] md:text-xs text-slate-700 leading-snug font-medium line-clamp-4">
              {clue ? (clue.text || clue.id) : 'No clue available.'}
            </p>
          </div>
        </div>
      ) : (
        // Face-Down Suspect Card View
        <div className="flex flex-col items-center justify-center flex-1 my-0.5">
          <Avatar name={name} coord={coord} size={50} />
          <div className="text-center font-semibold text-slate-800 text-xs md:text-sm tracking-tight mt-1">
            {name}
          </div>
          <div className="text-center text-[10px] md:text-[11px] text-slate-500 leading-tight">
            {profession}
          </div>
        </div>
      )}
    </div>
  );
}
