import React from 'react';
import { Lightbulb, FastForward, PlayCircle, RotateCcw, Shield, CheckCircle } from 'lucide-react';

export default function Sidebar({
  gameState,
  onHint,
  onAutoStep,
  onAutoSolveAll,
  onRestart,
  onBackToMenu,
  isAutoSolving = false
}) {
  const { current_puzzle, size = 3, proved_count = 0, total_cells = 9, stats = {}, is_won = false } = gameState || {};
  const primaryVars = stats.num_primary_vars || size * size;
  const auxVars = stats.num_aux_vars || 0;
  const numClauses = stats.num_clauses || 0;

  return (
    <aside className="w-full lg:w-84 xl:w-92 flex flex-col justify-between text-[#d6cec6] select-none p-2 md:p-3">
      {/* Title & Brand Section */}
      <div>
        <div className="flex items-center gap-3.5 mb-2.5">
          {/* Detective Silhouette Icon */}
          <div className="w-11 h-11 rounded-xl bg-[#26211d] border border-[#3b342e] flex items-center justify-center text-2xl shadow-inner">
            🕵️
          </div>
          <div>
            <h1 className="font-serif text-2xl md:text-3xl font-bold tracking-tight text-[#f2ece6] leading-none">
              Griductive
            </h1>
            <p className="text-xs md:text-sm text-[#a39689] tracking-wide mt-1">
              A daily grid-deduction puzzle.
            </p>
          </div>
        </div>

        {/* Level & Return to Menu Badges */}
        <div className="flex items-center justify-between mb-4 text-xs font-bold text-[#9c8f82] uppercase tracking-wider">
          <div className="flex items-center gap-2">
            <span className="bg-[#26211d] border border-[#383029] px-2.5 py-1 rounded-md text-[#d6cec6]">
              SIZE {size}x{size}
            </span>
            <span className="bg-[#26211d] border border-[#383029] px-2.5 py-1 rounded-md text-amber-300">
              LEVEL {size === 3 ? 'EASY' : size === 4 ? 'DAILY' : 'HARD'}
            </span>
          </div>

          <button
            onClick={onBackToMenu}
            title="Return to Main Menu"
            className="flex items-center gap-1.5 px-3 py-1 rounded-md bg-[#2a231d] hover:bg-[#382f27] text-[#ded6cf] border border-[#42372e] transition-all cursor-pointer font-sans font-semibold text-xs shadow-xs"
          >
            <span>← Menu</span>
          </button>
        </div>

        {/* How to Play Box (Clean & Readable) */}
        <div className="bg-[#1e1916] border border-[#382f28] rounded-xl p-3.5 md:p-4 text-xs md:text-[13px] leading-relaxed text-[#c4b8ab] mb-4 shadow-sm">
          <div className="text-xs uppercase font-bold text-[#f5efe9] tracking-wider mb-2.5 flex items-center gap-1.5 border-b border-[#312923] pb-1.5">
            <span>HOW TO PLAY</span>
          </div>
          <p className="mb-2.5 text-[#ded6cf] font-medium leading-normal">
            Every person is criminal or innocent, and every clue is true.
          </p>
          <ul className="space-y-2 text-xs md:text-[12.5px] leading-relaxed">
            <li className="flex items-start gap-2">
              <span className="text-amber-500 font-bold text-sm leading-none mt-0.5">❖</span>
              <span>Tap a suspect to call them <strong className="text-red-400 font-semibold">criminal</strong> or <strong className="text-emerald-400 font-semibold">innocent</strong>.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-amber-500 font-bold text-sm leading-none mt-0.5">❖</span>
              <span>A right call flips the card and reveals its clue.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-amber-500 font-bold text-sm leading-none mt-0.5">❖</span>
              <span className="font-semibold text-[#f5efe9]">Only call what the clues prove. NO guessing!</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-amber-500 font-bold text-sm leading-none mt-0.5">❖</span>
              <span>Hint spotlights the next provable step.</span>
            </li>
          </ul>
        </div>

        {/* Action Controls */}
        <div className="space-y-2.5 mb-4">
          {/* Hint Button */}
          <button
            onClick={onHint}
            className="w-full flex items-center justify-center gap-2 bg-[#1f2d37] hover:bg-[#283b49] text-cyan-300 border border-cyan-800/60 rounded-xl py-2.5 px-4 text-xs md:text-sm font-semibold shadow-sm transition-all active:scale-[0.98] cursor-pointer"
          >
            <Lightbulb className="w-4.5 h-4.5 text-cyan-400" />
            <span>Hint: Spotlight Next Step</span>
          </button>

          {/* Auto Step */}
          <button
            onClick={onAutoStep}
            className="w-full flex items-center justify-center gap-2 bg-[#1b3328] hover:bg-[#244234] text-emerald-300 border border-emerald-800/60 rounded-xl py-2.5 px-4 text-xs md:text-sm font-semibold shadow-sm transition-all active:scale-[0.98] cursor-pointer"
          >
            <FastForward className="w-4.5 h-4.5 text-emerald-400" />
            <span>Auto Step (Logic Agent)</span>
          </button>

          {/* Auto Solve All */}
          <button
            onClick={onAutoSolveAll}
            className={`w-full flex items-center justify-center gap-2 border rounded-xl py-2.5 px-4 text-xs md:text-sm font-semibold shadow-sm transition-all active:scale-[0.98] cursor-pointer ${
              isAutoSolving
                ? 'bg-[#4a1d24] text-red-300 border-red-700/60'
                : 'bg-[#3b2319] hover:bg-[#4a2e21] text-amber-300 border-amber-800/60'
            }`}
          >
            <PlayCircle className="w-4.5 h-4.5" />
            <span>{isAutoSolving ? 'Pause Auto Solve' : 'Auto Solve (All)'}</span>
          </button>

          {/* Restart */}
          <button
            onClick={onRestart}
            className="w-full flex items-center justify-center gap-2 bg-[#25201c] hover:bg-[#302a24] text-[#bdae9f] border border-[#3d342d] rounded-xl py-2 px-3 text-xs md:text-sm font-medium transition-all cursor-pointer"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Restart Puzzle</span>
          </button>
        </div>
      </div>

      {/* Live SAT Knowledge Base State Tracker */}
      <div className="bg-[#1c1815] border border-[#332a22] rounded-xl p-3.5 text-xs text-[#a39689]">
        <div className="flex items-center justify-between font-semibold text-[#ded5cc] mb-2 text-xs md:text-sm">
          <span>Public Knowledge Base</span>
          {is_won ? (
            <span className="text-emerald-400 font-bold flex items-center gap-1.5 text-xs">
              <CheckCircle className="w-3.5 h-3.5" /> SOLVED
            </span>
          ) : (
            <span className="text-amber-400 text-xs font-mono font-bold">
              {proved_count} / {total_cells} Cards
            </span>
          )}
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-[#2a241f] rounded-full h-2 mb-2.5 overflow-hidden">
          <div
            className="bg-emerald-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${(proved_count / (total_cells || 1)) * 100}%` }}
          />
        </div>

        <div className="grid grid-cols-2 gap-1.5 text-xs text-[#9c8f82]">
          <div>Primary Vars: <span className="text-[#f2ece6] font-mono font-bold">{primaryVars}</span></div>
          <div>Aux Vars: <span className="text-[#f2ece6] font-mono font-bold">{auxVars}</span></div>
          <div className="col-span-2 pt-0.5">Active Clauses in KB: <span className="text-amber-300 font-mono font-bold">{numClauses}</span></div>
        </div>
      </div>
    </aside>
  );
}

