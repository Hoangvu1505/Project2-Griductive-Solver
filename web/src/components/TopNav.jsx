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
    <header className="w-full bg-white/70 backdrop-blur-xl border-b border-slate-200/60 px-3 md:px-6 py-2.5 flex items-center justify-between text-slate-700 text-xs md:text-sm select-none">
      {/* Left: Brand & Return to Menu */}
      <button
        onClick={onBackToMenu}
        title="Return to Main Menu"
        className="flex items-center gap-2 font-medium hover:text-slate-900 transition-colors group cursor-pointer"
      >
        <div className="p-1 rounded-md bg-slate-50 border border-slate-200 group-hover:border-violet-300">
          <ChevronLeft className="w-3.5 h-3.5 text-slate-400 group-hover:text-violet-500 transition-colors" />
        </div>
        <span className="font-serif font-bold text-base md:text-lg tracking-tight text-slate-800">
          Griductive
        </span>
        <span className="text-[10px] font-sans px-1.5 py-0.5 rounded bg-slate-100 text-slate-500 border border-slate-200 hidden sm:inline">
          Menu
        </span>
      </button>

      {/* Center: Level Selector Tabs (MON EASY 1 2 3 4 5 SUN HARD) */}
      <div className="hidden sm:flex items-center bg-slate-50/80 border border-slate-200 rounded-xl p-1 text-[11px] gap-1">
        <span className="px-2 text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
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
                  ? 'bg-white text-slate-800 border border-slate-300 shadow-sm'
                  : 'text-slate-400 hover:text-slate-600 hover:bg-slate-100'
              }`}
            >
              {num}
            </button>
          );
        })}
        <span className="px-2 text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
          HARD
        </span>
      </div>

      {/* Right: Timer & Utility Controls */}
      <div className="flex items-center gap-2 md:gap-3">
        {/* Timer */}
        <div className="flex items-center gap-1.5 bg-slate-50/80 border border-slate-200 rounded-xl px-2.5 py-1 text-xs font-mono font-bold text-slate-800">
          <span>{formatTime(timerSeconds)}</span>
          <button onClick={onTogglePause} className="hover:text-violet-500 transition-colors">
            {isPaused ? <Play className="w-3.5 h-3.5" /> : <Pause className="w-3.5 h-3.5" />}
          </button>
        </div>

        {/* Check Uniqueness */}
        <button
          onClick={onCheckUniqueness}
          title="Verify Puzzle Uniqueness with DPLL"
          className="flex items-center gap-1 px-2.5 py-1 rounded-xl bg-slate-50/80 border border-slate-200 text-xs font-medium hover:border-violet-300 hover:text-violet-600 transition-all"
        >
          <CheckSquare className="w-3.5 h-3.5 text-violet-500" />
          <span className="hidden md:inline">Unique</span>
        </button>

        {/* SAT Trace Drawer Toggle */}
        <button
          onClick={onOpenTrace}
          title="Inspect SAT Deduction Log"
          className="flex items-center gap-1 px-2.5 py-1 rounded-xl bg-slate-50/80 border border-slate-200 text-xs font-medium hover:border-violet-300 hover:text-violet-600 transition-all"
        >
          <Terminal className="w-3.5 h-3.5 text-cyan-500" />
          <span className="hidden md:inline">Trace</span>
        </button>

        {/* Help */}
        <button
          onClick={onOpenHelp}
          title="How to Play"
          className="p-1.5 rounded-xl hover:bg-slate-100 hover:text-slate-600 transition-colors"
        >
          <HelpCircle className="w-4 h-4 text-slate-400" />
        </button>
      </div>
    </header>
  );
}
