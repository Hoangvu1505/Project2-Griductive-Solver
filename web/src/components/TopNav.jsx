import React from 'react';
import { ChevronLeft, Pause, Play, HelpCircle, Calendar, Layers, CheckSquare, Terminal } from 'lucide-react';

export default function TopNav({
  puzzles = [],
  currentPuzzle = '',
  onSelectPuzzle,
  onBackToMenu,
  timerSeconds = 0,
  isPaused = false,
  onTogglePause,
  onOpenHelp,
  onOpenTrace,
  onCheckUniqueness
}) {
  const formatTime = (secs) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <header className="w-full bg-[#161311] border-b border-[#2b2520] px-3 md:px-6 py-2.5 flex items-center justify-between text-[#d6cec6] text-xs md:text-sm select-none">
      {/* Left: Brand & Return to Menu */}
      <button
        onClick={onBackToMenu}
        title="Return to Main Menu"
        className="flex items-center gap-2 font-medium hover:text-white transition-colors group cursor-pointer"
      >
        <div className="p-1 rounded-md bg-[#231e1a] border border-[#383029] group-hover:border-[#5a4f44]">
          <ChevronLeft className="w-3.5 h-3.5 text-[#8a7f74] group-hover:text-amber-400 transition-colors" />
        </div>
        <span className="font-serif font-bold text-base md:text-lg tracking-tight text-[#f2ece6]">
          Griductive
        </span>
        <span className="text-[10px] font-sans px-1.5 py-0.5 rounded bg-[#251e19] text-[#9c8f82] border border-[#382e26] hidden sm:inline">
          Menu
        </span>
      </button>

      {/* Center: Level Selector Tabs (MON EASY 1 2 3 4 5 SUN HARD) */}
      <div className="hidden sm:flex items-center bg-[#231e1a] border border-[#383029] rounded-lg p-1 text-[11px] gap-1">
        <span className="px-2 text-[10px] font-semibold text-[#8a7f74] uppercase tracking-wider">
          EASY
        </span>
        {puzzles.map((p, idx) => {
          const num = idx + 1;
          const isSelected = p.filename === currentPuzzle;
          return (
            <button
              key={p.filename}
              onClick={() => onSelectPuzzle(p.filename)}
              title={`${p.name} (${p.size}x${p.size})`}
              className={`w-6 h-6 rounded-md flex items-center justify-center font-bold text-xs transition-all ${
                isSelected
                  ? 'bg-[#3b342e] text-[#f2ece6] border border-[#5a4f44] shadow-sm'
                  : 'text-[#8a7f74] hover:text-[#d6cec6] hover:bg-[#2b2520]'
              }`}
            >
              {num}
            </button>
          );
        })}
        <span className="px-2 text-[10px] font-semibold text-[#8a7f74] uppercase tracking-wider">
          HARD
        </span>
      </div>

      {/* Right: Timer & Utility Controls */}
      <div className="flex items-center gap-2 md:gap-3">
        {/* Timer */}
        <div className="flex items-center gap-1.5 bg-[#231e1a] border border-[#383029] rounded-lg px-2.5 py-1 text-xs font-mono font-bold text-[#e6ded6]">
          <span>{formatTime(timerSeconds)}</span>
          <button onClick={onTogglePause} className="hover:text-amber-400 transition-colors">
            {isPaused ? <Play className="w-3.5 h-3.5" /> : <Pause className="w-3.5 h-3.5" />}
          </button>
        </div>

        {/* Check Uniqueness */}
        <button
          onClick={onCheckUniqueness}
          title="Verify Puzzle Uniqueness with DPLL"
          className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-[#231e1a] border border-[#383029] text-xs font-medium hover:border-[#5a4f44] hover:text-white transition-all"
        >
          <CheckSquare className="w-3.5 h-3.5 text-purple-400" />
          <span className="hidden md:inline">Unique</span>
        </button>

        {/* SAT Trace Drawer Toggle */}
        <button
          onClick={onOpenTrace}
          title="Inspect SAT Deduction Log"
          className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-[#231e1a] border border-[#383029] text-xs font-medium hover:border-[#5a4f44] hover:text-white transition-all"
        >
          <Terminal className="w-3.5 h-3.5 text-cyan-400" />
          <span className="hidden md:inline">Trace</span>
        </button>

        {/* Help */}
        <button
          onClick={onOpenHelp}
          title="How to Play"
          className="p-1.5 rounded-lg hover:bg-[#2b2520] hover:text-white transition-colors"
        >
          <HelpCircle className="w-4 h-4 text-[#8a7f74]" />
        </button>
      </div>
    </header>
  );
}

