import React from 'react';
import { Lightbulb, FastForward, PlayCircle, RotateCcw, Shield, CheckCircle } from 'lucide-react';

export default function Sidebar({
  gameState,
  onHint,
  onAutoStep,
  onAutoSolveAll,
  onRestart,
  isAutoSolving = false
}) {
  const { current_puzzle, size = 3, proved_count = 0, total_cells = 9, stats = {}, is_won = false } = gameState || {};
  const primaryVars = stats.num_primary_vars || size * size;
  const auxVars = stats.num_aux_vars || 0;
  const numClauses = stats.num_clauses || 0;

  return (
    <aside className="w-full lg:w-72 flex flex-col justify-between text-[#d6cec6] select-none p-1 md:p-3">
      {/* Title & Brand Section */}
      <div>
        <div className="flex items-center gap-3 mb-2">
          {/* Detective Silhouette Icon */}
          <div className="w-10 h-10 rounded-xl bg-[#26211d] border border-[#3b342e] flex items-center justify-center text-xl shadow-inner">
            🕵️
          </div>
          <div>
            <h1 className="font-serif text-2xl md:text-3xl font-bold tracking-tight text-[#f2ece6] leading-none">
              Griductive
            </h1>
            <p className="text-[11px] text-[#8f8378] tracking-wide mt-0.5">
              A daily grid-deduction puzzle.
            </p>
          </div>
        </div>

        {/* Level & Date Badges */}
        <div className="flex items-center gap-2 mb-4 text-[10px] font-semibold text-[#8f8378] uppercase tracking-wider">
          <span className="bg-[#26211d] border border-[#383029] px-2 py-0.5 rounded">
            SIZE {size}x{size}
          </span>
          <span className="bg-[#26211d] border border-[#383029] px-2 py-0.5 rounded">
            LEVEL ●●●○○○○
          </span>
        </div>

        {/* How to Play Box (matching the original text) */}
        <div className="bg-[#1e1916] border border-[#332b24] rounded-xl p-3 text-[11px] leading-relaxed text-[#b5a99d] mb-4">
          <div className="text-[10px] uppercase font-bold text-[#e6ded6] tracking-wider mb-2 flex items-center gap-1">
            HOW TO PLAY
          </div>
          <p className="mb-2 text-[#d1c7bc]">
            Every person is criminal or innocent, and every clue is true.
          </p>
          <ul className="space-y-1.5 text-[10.5px]">
            <li className="flex items-start gap-1.5">
              <span className="text-amber-500 font-bold">❖</span>
              <span>Tap a suspect to call them criminal or innocent.</span>
            </li>
            <li className="flex items-start gap-1.5">
              <span className="text-amber-500 font-bold">❖</span>
              <span>A right call flips the card and reveals its clue.</span>
            </li>
            <li className="flex items-start gap-1.5">
              <span className="text-amber-500 font-bold">❖</span>
              <span className="font-semibold text-[#eae3db]">Only call what the clues prove. NO guessing!</span>
            </li>
            <li className="flex items-start gap-1.5">
              <span className="text-amber-500 font-bold">❖</span>
              <span>Hint spotlights the next provable step.</span>
            </li>
          </ul>
        </div>

        {/* Action Controls */}
        <div className="space-y-2 mb-4">
          {/* Hint Button */}
          <button
            onClick={onHint}
            className="w-full flex items-center justify-center gap-2 bg-[#1f2d37] hover:bg-[#283b49] text-cyan-300 border border-cyan-800/60 rounded-xl py-2 px-3 text-xs font-semibold shadow-sm transition-all active:scale-[0.98]"
          >
            <Lightbulb className="w-4 h-4 text-cyan-400" />
            <span>Hint: Spotlight Next Step</span>
          </button>

          {/* Auto Step */}
          <button
            onClick={onAutoStep}
            className="w-full flex items-center justify-center gap-2 bg-[#1b3328] hover:bg-[#244234] text-emerald-300 border border-emerald-800/60 rounded-xl py-2 px-3 text-xs font-semibold shadow-sm transition-all active:scale-[0.98]"
          >
            <FastForward className="w-4 h-4 text-emerald-400" />
            <span>Auto Step (Logic Agent)</span>
          </button>

          {/* Auto Solve All */}
          <button
            onClick={onAutoSolveAll}
            className={`w-full flex items-center justify-center gap-2 border rounded-xl py-2 px-3 text-xs font-semibold shadow-sm transition-all active:scale-[0.98] ${
              isAutoSolving
                ? 'bg-[#4a1d24] text-red-300 border-red-700/60'
                : 'bg-[#3b2319] hover:bg-[#4a2e21] text-amber-300 border-amber-800/60'
            }`}
          >
            <PlayCircle className="w-4 h-4" />
            <span>{isAutoSolving ? 'Pause Auto Solve' : 'Auto Solve (All)'}</span>
          </button>

          {/* Restart */}
          <button
            onClick={onRestart}
            className="w-full flex items-center justify-center gap-2 bg-[#25201c] hover:bg-[#302a24] text-[#a89c90] border border-[#3d342d] rounded-xl py-1.5 px-3 text-xs font-medium transition-all"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Restart Puzzle</span>
          </button>
        </div>
      </div>

      {/* Live SAT Knowledge Base State Tracker */}
      <div className="bg-[#1c1815] border border-[#2d2520] rounded-xl p-3 text-[11px] text-[#9c8f82]">
        <div className="flex items-center justify-between font-semibold text-[#ded5cc] mb-1.5">
          <span>Public Knowledge Base</span>
          {is_won ? (
            <span className="text-emerald-400 font-bold flex items-center gap-1 text-[10px]">
              <CheckCircle className="w-3 h-3" /> SOLVED
            </span>
          ) : (
            <span className="text-amber-400 text-[10px] font-mono">
              {proved_count} / {total_cells} Cards
            </span>
          )}
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-[#2a241f] rounded-full h-1.5 mb-2 overflow-hidden">
          <div
            className="bg-emerald-500 h-1.5 rounded-full transition-all duration-300"
            style={{ width: `${(proved_count / (total_cells || 1)) * 100}%` }}
          />
        </div>

        <div className="grid grid-cols-2 gap-1 text-[10px] text-[#8a7f74]">
          <div>Primary Vars: <span className="text-[#d6cec6] font-mono">{primaryVars}</span></div>
          <div>Aux Vars: <span className="text-[#d6cec6] font-mono">{auxVars}</span></div>
          <div className="col-span-2">Active Clauses in KB: <span className="text-[#d6cec6] font-mono">{numClauses}</span></div>
        </div>
      </div>
    </aside>
  );
}

