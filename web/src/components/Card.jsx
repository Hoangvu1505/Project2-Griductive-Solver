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
  let borderClass = 'border-[#3a332d] hover:border-[#524940]';
  let bgClass = 'bg-[#27221e]';

  if (is_revealed) {
    if (status === 'CRIMINAL') {
      borderClass = 'border-red-500/80 shadow-[0_0_12px_rgba(239,68,68,0.2)]';
      bgClass = 'bg-[#221616]';
    } else {
      borderClass = 'border-emerald-500/80 shadow-[0_0_12px_rgba(34,197,94,0.2)]';
      bgClass = 'bg-[#18241d]';
    }
  }

  if (isHighlightedRef) {
    borderClass = 'border-amber-400 ring-2 ring-amber-400/50 shadow-[0_0_16px_rgba(251,191,36,0.35)]';
  }

  if (isHighlightedHint) {
    borderClass = 'border-cyan-400 ring-4 ring-cyan-400/60 shadow-[0_0_20px_rgba(6,182,212,0.5)] animate-pulse';
  }

  if (isSelectedClue) {
    borderClass = 'border-purple-500 ring-2 ring-purple-500/60';
  }

  return (
    <div
      onClick={() => onClick(coord)}
      className={`relative select-none cursor-pointer rounded-xl border p-2 flex flex-col justify-between transition-all duration-200 transform active:scale-95 min-h-[140px] md:min-h-[155px] ${bgClass} ${borderClass}`}
    >
      {/* Top Bar: Coordinate and Status/Badge Icon */}
      <div className="flex items-center justify-between w-full mb-1">
        <span className="text-[10px] md:text-xs font-semibold tracking-wider text-[#8a7f74]">
          {coord}
        </span>

        {is_revealed ? (
          <div className="flex items-center gap-1">
            {status === 'CRIMINAL' ? (
              <span className="text-[10px] uppercase font-bold text-red-400 flex items-center gap-0.5">
                <ShieldAlert className="w-3 h-3 text-red-400 inline" />
              </span>
            ) : (
              <span className="text-[10px] uppercase font-bold text-emerald-400 flex items-center gap-0.5">
                <Star className="w-3 h-3 text-emerald-400 inline fill-emerald-400/20" />
              </span>
            )}
          </div>
        ) : pencilNote ? (
          <span className={`text-[9px] font-bold px-1 py-0.2 rounded ${pencilNote === 'CRIMINAL' ? 'bg-red-900/60 text-red-300' : 'bg-emerald-900/60 text-emerald-300'}`}>
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
            <div className="text-center font-semibold text-[#f0ebe5] text-xs md:text-sm tracking-tight leading-tight mt-0.5">
              {name}
            </div>
            <div className="text-center text-[10px] md:text-[11px] text-[#9c8f82] leading-tight mb-1">
              {profession}
            </div>
          </div>

          {/* Clue Text Box */}
          <div className="w-full bg-[#1b1714]/80 border border-[#3b342e] rounded-lg p-2 text-center my-auto">
            <p className="text-[11px] md:text-xs text-[#eae3db] leading-snug font-medium line-clamp-4">
              {clue ? (clue.text || clue.id) : 'No clue available.'}
            </p>
          </div>
        </div>
      ) : (
        // Face-Down Suspect Card View
        <div className="flex flex-col items-center justify-center flex-1 my-0.5">
          <Avatar name={name} coord={coord} size={50} />
          <div className="text-center font-semibold text-[#f0ebe5] text-xs md:text-sm tracking-tight mt-1">
            {name}
          </div>
          <div className="text-center text-[10px] md:text-[11px] text-[#9c8f82] leading-tight">
            {profession}
          </div>
        </div>
      )}
    </div>
  );
}

