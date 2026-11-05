import React, { useState } from 'react';
import Avatar from './Avatar';
import {
  Play,
  HelpCircle,
  BarChart3,
  Users,
  CheckCircle2,
  ShieldAlert,
  ArrowRight,
  BookOpen,
  Award,
  ChevronRight,
  Sparkles,
  Info,
  Clock,
  ExternalLink
} from 'lucide-react';

export default function MainMenu({
  puzzles = [],
  currentPuzzle = 'puzzle_4x4_1.json',
  onSelectCase,
  onStartPlaying
}) {
  const [activeTab, setActiveTab] = useState('cases'); // 'cases' | 'rules' | 'benchmarks' | 'about'

  // Metadata enrichment for case cards
  const getPuzzleMeta = (filename, size) => {
    switch (filename) {
      case 'puzzle_3x3_1.json':
        return {
          badge: 'EASY',
          badgeColor: 'bg-emerald-950/80 text-emerald-400 border-emerald-800/60',
          desc: 'A calm countryside village where simple rumors point directly to the culprit.',
          suspects: 9,
          criminals: 2,
          cluesCount: 1,
          difficulty: '1 / 5'
        };
      case 'puzzle_3x3_2.json':
        return {
          badge: 'NOVICE',
          badgeColor: 'bg-teal-950/80 text-teal-400 border-teal-800/60',
          desc: 'A secret meeting with interwoven parity and comparison clues between neighbors.',
          suspects: 9,
          criminals: 3,
          cluesCount: 1,
          difficulty: '2 / 5'
        };
      case 'puzzle_4x4_1.json':
        return {
          badge: 'DAILY CASE',
          badgeColor: 'bg-amber-950/80 text-amber-300 border-amber-700/60 shadow-xs shadow-amber-900/30',
          desc: 'The canonical 16-suspect investigation with chained neighborhood deductions.',
          suspects: 16,
          criminals: 5,
          cluesCount: 2,
          difficulty: '3 / 5',
          featured: true
        };
      case 'puzzle_4x4_2.json':
        return {
          badge: 'CHALLENGING',
          badgeColor: 'bg-purple-950/80 text-purple-300 border-purple-800/60',
          desc: 'Court intrigue featuring exact row/column counts and parity constraints.',
          suspects: 16,
          criminals: 6,
          cluesCount: 2,
          difficulty: '4 / 5'
        };
      case 'puzzle_5x5_1.json':
        return {
          badge: 'MASTER',
          badgeColor: 'bg-rose-950/80 text-rose-300 border-rose-800/60',
          desc: 'High-stakes metropolis grid requiring 25 deductive steps with multi-region clauses.',
          suspects: 25,
          criminals: 9,
          cluesCount: 2,
          difficulty: '5 / 5'
        };
      default:
        return {
          badge: `${size}x${size}`,
          badgeColor: 'bg-stone-800 text-stone-300 border-stone-700',
          desc: 'Custom puzzle investigation.',
          suspects: size * size,
          criminals: Math.floor((size * size) / 3),
          cluesCount: 1,
          difficulty: '3 / 5'
        };
    }
  };

  // Sample characters for the showcase row
  const showcaseCast = [
    { name: 'Alan', job: 'Mechanic' },
    { name: 'Brian', job: 'Painter' },
    { name: 'Clara', job: 'Painter' },
    { name: 'Dana', job: 'Operator' },
    { name: 'Evan', job: 'Mechanic' },
    { name: 'Hannah', job: 'Operator' },
    { name: 'June', job: 'Tester' },
    { name: 'Ruby', job: 'Cleaner' },
    { name: 'Quentin', job: 'Cleaner' },
    { name: 'Tess', job: 'Clerk' }
  ];

  return (
    <div className="min-h-screen bg-[#14110f] text-[#ded6cf] flex flex-col justify-between selection:bg-amber-900/50">
      {/* Top Banner Navigation */}
      <header className="border-b border-[#2b2520] bg-[#191512]/90 backdrop-blur-md sticky top-0 z-20 px-4 md:px-8 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-600 to-amber-900 flex items-center justify-center shadow-md shadow-amber-950/50 border border-amber-500/30">
            <Sparkles className="w-4 h-4 text-amber-200" />
          </div>
          <div>
            <h1 className="font-serif font-black text-lg md:text-xl tracking-wider text-[#f5efe9]">
              GRIDUCTIVE
            </h1>
            <p className="text-[10px] uppercase font-semibold tracking-widest text-[#8c8074]">
              Propositional SAT Deduction
            </p>
          </div>
        </div>

        {/* Menu Navigation Tabs */}
        <nav className="flex items-center gap-1 md:gap-2 bg-[#211c18] p-1 rounded-xl border border-[#383029] text-xs">
          <button
            onClick={() => setActiveTab('cases')}
            className={`px-3 py-1.5 rounded-lg font-medium transition-all flex items-center gap-1.5 ${
              activeTab === 'cases'
                ? 'bg-[#3b342e] text-[#f5efe9] shadow-xs border border-[#524940]'
                : 'text-[#9c8f82] hover:text-[#ded6cf]'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Select Case</span>
          </button>

          <button
            onClick={() => setActiveTab('rules')}
            className={`px-3 py-1.5 rounded-lg font-medium transition-all flex items-center gap-1.5 ${
              activeTab === 'rules'
                ? 'bg-[#3b342e] text-[#f5efe9] shadow-xs border border-[#524940]'
                : 'text-[#9c8f82] hover:text-[#ded6cf]'
            }`}
          >
            <HelpCircle className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">How to Play</span>
          </button>

          <button
            onClick={() => setActiveTab('benchmarks')}
            className={`px-3 py-1.5 rounded-lg font-medium transition-all flex items-center gap-1.5 ${
              activeTab === 'benchmarks'
                ? 'bg-[#3b342e] text-[#f5efe9] shadow-xs border border-[#524940]'
                : 'text-[#9c8f82] hover:text-[#ded6cf]'
            }`}
          >
            <BarChart3 className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Benchmarks</span>
          </button>

          <button
            onClick={() => setActiveTab('about')}
            className={`px-3 py-1.5 rounded-lg font-medium transition-all flex items-center gap-1.5 ${
              activeTab === 'about'
                ? 'bg-[#3b342e] text-[#f5efe9] shadow-xs border border-[#524940]'
                : 'text-[#9c8f82] hover:text-[#ded6cf]'
            }`}
          >
            <Users className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Project Info</span>
          </button>
        </nav>
      </header>

      {/* Main Content View Container */}
      <main className="max-w-6xl w-full mx-auto px-4 py-6 md:py-10 flex-1 flex flex-col justify-center">
        {/* --- TAB 1: CASES / PUZZLE SELECTION --- */}
        {activeTab === 'cases' && (
          <div className="space-y-8 animate-fadeIn">
            {/* Hero Card */}
            <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-[#211a15] via-[#2a221b] to-[#1c1612] border border-[#42372e] p-6 md:p-8 shadow-2xl">
              <div className="relative z-10 max-w-2xl">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-950/70 border border-amber-700/50 text-amber-300 text-xs font-semibold mb-3">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>CSC14003 - Artificial Intelligence Project</span>
                </div>
                <h2 className="text-2xl md:text-4xl font-serif font-black text-[#f7f2ed] tracking-tight leading-tight mb-2">
                  Solve cases purely through logic.
                </h2>
                <p className="text-sm md:text-base text-[#ab9e91] leading-relaxed mb-6 font-normal">
                  Every suspect is either a <span className="text-red-400 font-semibold">Criminal</span> or <span className="text-emerald-400 font-semibold">Innocent</span>.
                  Every revealed clue is true. A verdict is accepted only when strictly proved by propositional SAT entailment.
                  <strong className="text-amber-200"> Zero guessing allowed.</strong>
                </p>

                <div className="flex flex-wrap items-center gap-3">
                  <button
                    onClick={() => {
                      onSelectCase(currentPuzzle);
                      onStartPlaying();
                    }}
                    className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-amber-600 to-amber-700 hover:from-amber-500 hover:to-amber-600 text-white font-semibold text-sm shadow-lg shadow-amber-950/60 border border-amber-400/40 transition-all transform active:scale-95 cursor-pointer"
                  >
                    <Play className="w-4 h-4 fill-white" />
                    <span>Investigate Daily Case (4x4)</span>
                  </button>

                  <button
                    onClick={() => setActiveTab('rules')}
                    className="inline-flex items-center gap-2 px-4 py-3 rounded-xl bg-[#2b241e] hover:bg-[#382f27] text-[#ded6cf] text-sm font-medium border border-[#473c32] transition-all cursor-pointer"
                  >
                    <span>Read Detective Rules</span>
                    <ChevronRight className="w-4 h-4 text-[#8c8074]" />
                  </button>
                </div>
              </div>

              {/* Decorative Background Badge */}
              <div className="absolute right-4 md:right-8 -bottom-10 opacity-10 pointer-events-none select-none text-[#f5efe9]">
                <ShieldAlert className="w-64 h-64" />
              </div>
            </div>

            {/* Suspect Cast Showcase Preview */}
            <div className="bg-[#1b1613] border border-[#2e2620] rounded-xl p-4">
              <div className="flex items-center justify-between mb-3 px-1">
                <span className="text-xs uppercase font-bold tracking-wider text-[#8c8074]">
                  Featured Suspects & Procedural Avatars
                </span>
                <span className="text-[11px] text-[#71655a]">
                  100% Vector SVG • 12 Hairstyles • 10 Colors
                </span>
              </div>
              <div className="flex items-center justify-between gap-2 overflow-x-auto py-1 scrollbar-none">
                {showcaseCast.map((c) => (
                  <div key={c.name} className="flex flex-col items-center flex-shrink-0 min-w-[70px]">
                    <div className="p-1 rounded-full bg-[#241d18] border border-[#382e26] hover:scale-105 transition-transform">
                      <Avatar name={c.name} size={44} />
                    </div>
                    <span className="text-xs font-semibold text-[#eae3dc] mt-1">{c.name}</span>
                    <span className="text-[10px] text-[#8c8074]">{c.job}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Case Selection Cards Grid */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-serif font-bold text-lg text-[#f0ebe5] flex items-center gap-2">
                  <span>Available Mystery Cases</span>
                  <span className="text-xs font-sans font-semibold px-2 py-0.5 rounded-full bg-[#28221c] text-[#a19487] border border-[#3a3129]">
                    {puzzles.length} Cases
                  </span>
                </h3>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {puzzles.map((p) => {
                  const meta = getPuzzleMeta(p.filename, p.size);
                  const isCurrent = p.filename === currentPuzzle;

                  return (
                    <div
                      key={p.filename}
                      onClick={() => {
                        onSelectCase(p.filename);
                        onStartPlaying();
                      }}
                      className={`group relative rounded-xl border p-5 flex flex-col justify-between cursor-pointer transition-all duration-200 hover:-translate-y-1 ${
                        isCurrent
                          ? 'bg-[#261e18] border-amber-600/70 shadow-lg shadow-amber-950/40 ring-1 ring-amber-500/30'
                          : 'bg-[#1e1915] border-[#362e27] hover:border-[#574a3f] hover:bg-[#241e19]'
                      }`}
                    >
                      <div>
                        {/* Top Meta Header */}
                        <div className="flex items-center justify-between mb-2">
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md border uppercase tracking-wider ${meta.badgeColor}`}>
                            {meta.badge}
                          </span>
                          <span className="text-xs font-mono font-semibold text-[#8c8074]">
                            {p.size} × {p.size} Grid
                          </span>
                        </div>

                        {/* Title & Desc */}
                        <h4 className="font-serif font-bold text-base text-[#f2ece6] group-hover:text-amber-200 transition-colors">
                          {p.name}
                        </h4>
                        <p className="text-xs text-[#9c8f82] leading-relaxed mt-1 mb-4">
                          {meta.desc}
                        </p>
                      </div>

                      {/* Card Footer Details */}
                      <div>
                        <div className="flex items-center justify-between text-[11px] text-[#807469] border-t border-[#312923] pt-3 mb-3">
                          <span>{meta.suspects} Suspects</span>
                          <span>•</span>
                          <span>{meta.criminals} Criminals</span>
                          <span>•</span>
                          <span>Diff: {meta.difficulty}</span>
                        </div>

                        <button className="w-full py-2 rounded-lg bg-[#2e2620] group-hover:bg-amber-600 group-hover:text-white text-[#d6cec6] text-xs font-semibold flex items-center justify-center gap-1.5 transition-all">
                          <span>Investigate Case</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* --- TAB 2: RULES / HOW TO PLAY --- */}
        {activeTab === 'rules' && (
          <div className="space-y-6 animate-fadeIn max-w-4xl mx-auto">
            <div className="text-center max-w-xl mx-auto mb-8">
              <h2 className="text-2xl md:text-3xl font-serif font-bold text-[#f5efe9]">
                How to Play Griductive
              </h2>
              <p className="text-sm text-[#9c8f82] mt-1">
                A logic deduction puzzle based on pure propositional satisfiability.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Rule 1 */}
              <div className="bg-[#1f1915] border border-[#382f28] rounded-xl p-5">
                <div className="w-8 h-8 rounded-lg bg-amber-900/40 border border-amber-700/50 flex items-center justify-center text-amber-300 font-bold mb-3">
                  1
                </div>
                <h4 className="font-semibold text-sm text-[#f0ebe5] mb-1">
                  Hidden Truth & Public Clues
                </h4>
                <p className="text-xs text-[#a39689] leading-relaxed">
                  Every person on the grid is secretly either <strong className="text-red-400">Criminal</strong> or <strong className="text-emerald-400">Innocent</strong>. All clues shown on cards are always 100% true, regardless of whether their owner is criminal or innocent.
                </p>
              </div>

              {/* Rule 2 */}
              <div className="bg-[#1f1915] border border-[#382f28] rounded-xl p-5">
                <div className="w-8 h-8 rounded-lg bg-red-900/40 border border-red-700/50 flex items-center justify-center text-red-300 font-bold mb-3">
                  2
                </div>
                <h4 className="font-semibold text-sm text-[#f0ebe5] mb-1">
                  Strict Rule: NO GUESSING
                </h4>
                <p className="text-xs text-[#a39689] leading-relaxed">
                  You cannot guess or flip cards blindly. When you call a verdict on a suspect, the Game Engine evaluates propositional entailment: <code className="text-amber-300 font-mono">KB |= C_i</code> or <code className="text-amber-300 font-mono">KB |= ¬C_i</code>. If it cannot be proven yet, it is rejected with <strong className="text-amber-400">NOT_PROVABLE</strong>!
                </p>
              </div>

              {/* Rule 3 */}
              <div className="bg-[#1f1915] border border-[#382f28] rounded-xl p-5">
                <div className="w-8 h-8 rounded-lg bg-emerald-900/40 border border-emerald-700/50 flex items-center justify-center text-emerald-300 font-bold mb-3">
                  3
                </div>
                <h4 className="font-semibold text-sm text-[#f0ebe5] mb-1">
                  Flipping Cards Reveals New Clues
                </h4>
                <p className="text-xs text-[#a39689] leading-relaxed">
                  Once a suspect's status is correctly proved and accepted, their card flips face-up, revealing their personal clue. This new clue is immediately added into the knowledge base, unlocking subsequent deductions.
                </p>
              </div>

              {/* Rule 4 */}
              <div className="bg-[#1f1915] border border-[#382f28] rounded-xl p-5">
                <div className="w-8 h-8 rounded-lg bg-cyan-900/40 border border-cyan-700/50 flex items-center justify-center text-cyan-300 font-bold mb-3">
                  4
                </div>
                <h4 className="font-semibold text-sm text-[#f0ebe5] mb-1">
                  Interactive Hint & Deduction Trace
                </h4>
                <p className="text-xs text-[#a39689] leading-relaxed">
                  Stuck? Tap <strong className="text-cyan-300">Hint</strong> to highlight which suspect is currently forced by logic, along with the relevant clues. You can also view the full step-by-step SAT deduction trace in the <strong className="text-purple-300">Trace Drawer</strong>.
                </p>
              </div>
            </div>

            {/* Clue Types Table */}
            <div className="bg-[#1b1613] border border-[#332a23] rounded-xl p-5 mt-6">
              <h4 className="font-serif font-bold text-sm text-[#f0ebe5] mb-3">
                Supported Clue Types & CNF Encodings
              </h4>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                <div className="p-2.5 rounded-lg bg-[#241e19] border border-[#3a3129]">
                  <span className="font-mono font-bold text-amber-300">FACT</span>
                  <p className="text-[11px] text-[#9c8f82] mt-0.5">Direct criminal or innocent status.</p>
                </div>
                <div className="p-2.5 rounded-lg bg-[#241e19] border border-[#3a3129]">
                  <span className="font-mono font-bold text-amber-300">SAME / DIFF</span>
                  <p className="text-[11px] text-[#9c8f82] mt-0.5">Bi-conditional or XOR relationships.</p>
                </div>
                <div className="p-2.5 rounded-lg bg-[#241e19] border border-[#3a3129]">
                  <span className="font-mono font-bold text-amber-300">EXACTLY (k)</span>
                  <p className="text-[11px] text-[#9c8f82] mt-0.5">Combinatorial cardinality constraints.</p>
                </div>
                <div className="p-2.5 rounded-lg bg-[#241e19] border border-[#3a3129]">
                  <span className="font-mono font-bold text-amber-300">PARITY / CMP</span>
                  <p className="text-[11px] text-[#9c8f82] mt-0.5">Even/Odd and relative region counts.</p>
                </div>
              </div>
            </div>

            <div className="text-center pt-4">
              <button
                onClick={() => {
                  onSelectCase(currentPuzzle);
                  onStartPlaying();
                }}
                className="px-6 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-semibold text-xs transition-all cursor-pointer"
              >
                Back to Case Investigation
              </button>
            </div>
          </div>
        )}

        {/* --- TAB 3: BENCHMARKS & DPLL PERFORMANCE --- */}
        {activeTab === 'benchmarks' && (
          <div className="space-y-6 animate-fadeIn max-w-4xl mx-auto">
            <div className="text-center max-w-xl mx-auto mb-6">
              <h2 className="text-2xl md:text-3xl font-serif font-bold text-[#f5efe9]">
                DPLL SAT Solver Benchmarks
              </h2>
              <p className="text-sm text-[#9c8f82] mt-1">
                Empirical evaluation across 3x3, 4x4, and 5x5 Griductive puzzle instances.
              </p>
            </div>

            {/* Benchmark Table */}
            <div className="bg-[#1b1613] border border-[#332a23] rounded-xl overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#241d18] text-[#9c8f82] uppercase text-[10px] tracking-wider border-b border-[#382f28]">
                    <tr>
                      <th className="p-3">Puzzle Case</th>
                      <th className="p-3">Grid Size</th>
                      <th className="p-3">Total Steps</th>
                      <th className="p-3">SAT Queries</th>
                      <th className="p-3">Unit Props</th>
                      <th className="p-3">Solve Time</th>
                      <th className="p-3">Result</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#2d251f] text-[#ded6cf]">
                    <tr className="hover:bg-[#241e19]">
                      <td className="p-3 font-semibold text-[#f0ebe5]">The Village Mystery</td>
                      <td className="p-3 font-mono">3 × 3</td>
                      <td className="p-3 font-mono">8</td>
                      <td className="p-3 font-mono">16</td>
                      <td className="p-3 font-mono">18</td>
                      <td className="p-3 font-mono text-emerald-400">0.003s</td>
                      <td className="p-3"><span className="text-[10px] font-bold text-emerald-400 bg-emerald-950/70 border border-emerald-800/60 px-2 py-0.5 rounded">SOLVED</span></td>
                    </tr>
                    <tr className="hover:bg-[#241e19]">
                      <td className="p-3 font-semibold text-[#f0ebe5]">The Secret Circle</td>
                      <td className="p-3 font-mono">3 × 3</td>
                      <td className="p-3 font-mono">8</td>
                      <td className="p-3 font-mono">16</td>
                      <td className="p-3 font-mono">22</td>
                      <td className="p-3 font-mono text-emerald-400">0.003s</td>
                      <td className="p-3"><span className="text-[10px] font-bold text-emerald-400 bg-emerald-950/70 border border-emerald-800/60 px-2 py-0.5 rounded">SOLVED</span></td>
                    </tr>
                    <tr className="hover:bg-[#241e19] bg-amber-950/20">
                      <td className="p-3 font-semibold text-amber-200">Knotwise Daily Case</td>
                      <td className="p-3 font-mono">4 × 4</td>
                      <td className="p-3 font-mono">14</td>
                      <td className="p-3 font-mono">76</td>
                      <td className="p-3 font-mono">84</td>
                      <td className="p-3 font-mono text-emerald-400">0.015s</td>
                      <td className="p-3"><span className="text-[10px] font-bold text-emerald-400 bg-emerald-950/70 border border-emerald-800/60 px-2 py-0.5 rounded">SOLVED</span></td>
                    </tr>
                    <tr className="hover:bg-[#241e19]">
                      <td className="p-3 font-semibold text-[#f0ebe5]">Royal Castle Intrigue</td>
                      <td className="p-3 font-mono">4 × 4</td>
                      <td className="p-3 font-mono">14</td>
                      <td className="p-3 font-mono">68</td>
                      <td className="p-3 font-mono">75</td>
                      <td className="p-3 font-mono text-emerald-400">0.014s</td>
                      <td className="p-3"><span className="text-[10px] font-bold text-emerald-400 bg-emerald-950/70 border border-emerald-800/60 px-2 py-0.5 rounded">SOLVED</span></td>
                    </tr>
                    <tr className="hover:bg-[#241e19]">
                      <td className="p-3 font-semibold text-[#f0ebe5]">Metropolis Conspiracy</td>
                      <td className="p-3 font-mono">5 × 5</td>
                      <td className="p-3 font-mono">23</td>
                      <td className="p-3 font-mono">142</td>
                      <td className="p-3 font-mono">160</td>
                      <td className="p-3 font-mono text-emerald-400">0.038s</td>
                      <td className="p-3"><span className="text-[10px] font-bold text-emerald-400 bg-emerald-950/70 border border-emerald-800/60 px-2 py-0.5 rounded">SOLVED</span></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* Performance Highlights */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="p-4 rounded-xl bg-[#1e1814] border border-[#382f28] text-center">
                <span className="text-[10px] uppercase font-bold text-[#8c8074]">100% Solvability</span>
                <p className="text-xl font-bold text-emerald-400 mt-1">0 Failures</p>
                <p className="text-[11px] text-[#9c8f82] mt-0.5">All 5 cases uniquely solvable with no guessing.</p>
              </div>

              <div className="p-4 rounded-xl bg-[#1e1814] border border-[#382f28] text-center">
                <span className="text-[10px] uppercase font-bold text-[#8c8074]">Average Runtime</span>
                <p className="text-xl font-bold text-amber-300 mt-1">&lt; 40 ms</p>
                <p className="text-[11px] text-[#9c8f82] mt-0.5">Near instantaneous SAT solving per deduction step.</p>
              </div>

              <div className="p-4 rounded-xl bg-[#1e1814] border border-[#382f28] text-center">
                <span className="text-[10px] uppercase font-bold text-[#8c8074]">SAT Model Verification</span>
                <p className="text-xl font-bold text-cyan-300 mt-1">Unique (1)</p>
                <p className="text-[11px] text-[#9c8f82] mt-0.5">Blocking clauses confirm no alternative solutions exist.</p>
              </div>
            </div>
          </div>
        )}

        {/* --- TAB 4: ABOUT & TEAM DISTRIBUTION --- */}
        {activeTab === 'about' && (
          <div className="space-y-6 animate-fadeIn max-w-4xl mx-auto">
            <div className="text-center max-w-xl mx-auto mb-6">
              <h2 className="text-2xl md:text-3xl font-serif font-bold text-[#f5efe9]">
                Project Information & Credits
              </h2>
              <p className="text-sm text-[#9c8f82] mt-1">
                CSC14003 - Nhập môn Trí tuệ Nhân tạo • ĐHKHTN (VNU-HCM)
              </p>
            </div>

            <div className="bg-[#1b1613] border border-[#332a23] rounded-xl p-5 space-y-4">
              <h4 className="font-serif font-bold text-sm text-[#f0ebe5] border-b border-[#312923] pb-2">
                Team Member Task Allocation
              </h4>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                <div className="p-3 rounded-lg bg-[#231d18] border border-[#382f28]">
                  <strong className="text-amber-300 block mb-1">Trưởng nhóm / Thành viên A</strong>
                  <p className="text-[11px] text-[#a39689]">
                    Logic Agent, tích hợp hệ thống, kiểm tra entailment KB |= C_i và KB |= ¬C_i, deduction loop, deduction trace, uniqueness check, Hint, CLI & git management.
                  </p>
                </div>

                <div className="p-3 rounded-lg bg-[#231d18] border border-[#382f28]">
                  <strong className="text-emerald-300 block mb-1">Thành viên B</strong>
                  <p className="text-[11px] text-[#a39689]">
                    Bộ giải SAT (DPLL): unit propagation, conflict detection, đệ quy & quay lui, assumptions, thống kê decisions/props, unit test và script benchmark.
                  </p>
                </div>

                <div className="p-3 rounded-lg bg-[#231d18] border border-[#382f28]">
                  <strong className="text-cyan-300 block mb-1">Thành viên C</strong>
                  <p className="text-[11px] text-[#a39689]">
                    CNF Encoder: ánh xạ biến xác định, mã hóa 6 dạng clue (FACT, SAME, DIFF, EXACTLY, AT_LEAST, AT_MOST) + 2 extension (PARITY, COMPARE), build_kb(t).
                  </p>
                </div>

                <div className="p-3 rounded-lg bg-[#231d18] border border-[#382f28]">
                  <strong className="text-purple-300 block mb-1">Thành viên D</strong>
                  <p className="text-[11px] text-[#a39689]">
                    Game Engine, Clue model & Region (row, col, neighbors, corners, between), semantic evaluator, PublicState, bộ puzzle 3x3, 4x4, 5x5 nghiệm duy nhất.
                  </p>
                </div>

                <div className="p-3 rounded-lg bg-[#231d18] border border-[#382f28] md:col-span-2">
                  <strong className="text-rose-300 block mb-1">Thành viên E</strong>
                  <p className="text-[11px] text-[#a39689]">
                    Modern GUI (React + Tailwind v4 + SVG procedural avatars), Main Menu, highlight clue ô liên quan, các nút Load / Restart / Hint / Auto Solve, kịch bản quay video demo 5-10 phút.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-[#26201b] bg-[#14110f] px-4 py-3 text-center text-xs text-[#73685e]">
        <span>Griductive Solver • Project 2 CSC14003 Artificial Intelligence • VNU-HCM University of Science</span>
      </footer>
    </div>
  );
}

