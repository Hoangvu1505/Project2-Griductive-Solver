import React, { useState } from 'react';
import Avatar from './Avatar';
import {
  Play,
  HelpCircle,
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
  const [activeTab, setActiveTab] = useState('cases'); // 'cases' | 'rules' | 'about'

  // Metadata enrichment for case cards
  const getPuzzleMeta = (filename, size) => {
    switch (filename) {
      case 'puzzle_3x3_1.json':
        return {
          badge: 'EASY',
          badgeColor: 'bg-emerald-100 text-emerald-700 border-emerald-200',
          desc: 'A calm countryside village where simple rumors point directly to the culprit.',
          suspects: 9,
          criminals: 2,
          difficulty: '1 / 5'
        };
      case 'puzzle_3x3_2.json':
        return {
          badge: 'NOVICE',
          badgeColor: 'bg-teal-100 text-teal-700 border-teal-200',
          desc: 'A secret meeting with interwoven parity and comparison clues between neighbors.',
          suspects: 9,
          criminals: 3,
          difficulty: '1 / 5'
        };
      case 'puzzle_3x3_3.json':
        return {
          badge: 'CASUAL',
          badgeColor: 'bg-cyan-100 text-cyan-700 border-cyan-200',
          desc: 'The busy docklands harboring stolen cargo and interconnected sailors.',
          suspects: 9,
          criminals: 4,
          difficulty: '2 / 5'
        };
      case 'puzzle_4x4_1.json':
        return {
          badge: 'DAILY CASE',
          badgeColor: 'bg-amber-100 text-amber-700 border-amber-300 shadow-sm shadow-amber-100',
          desc: 'The canonical 16-suspect investigation with chained neighborhood deductions.',
          suspects: 16,
          criminals: 5,
          difficulty: '3 / 5',
          featured: true
        };
      case 'puzzle_4x4_2.json':
        return {
          badge: 'CHALLENGING',
          badgeColor: 'bg-purple-100 text-purple-700 border-purple-200',
          desc: 'Royal castle intrigue featuring exact row/column counts and parity constraints.',
          suspects: 16,
          criminals: 6,
          difficulty: '3 / 5'
        };
      case 'puzzle_4x4_3.json':
        return {
          badge: 'DETECTIVE',
          badgeColor: 'bg-indigo-100 text-indigo-700 border-indigo-200',
          desc: 'A luxury passenger train rolling through the night with a cascade of clues.',
          suspects: 16,
          criminals: 7,
          difficulty: '4 / 5'
        };
      case 'puzzle_4x4_4.json':
        return {
          badge: 'HARD',
          badgeColor: 'bg-orange-100 text-orange-700 border-orange-200',
          desc: 'A grand ballroom diamond heist with alternating checkerboard logic.',
          suspects: 16,
          criminals: 8,
          difficulty: '4 / 5'
        };
      case 'puzzle_5x5_1.json':
        return {
          badge: 'EXPERT',
          badgeColor: 'bg-rose-100 text-rose-700 border-rose-200',
          desc: 'High-stakes metropolis grid requiring 25 deductive steps with multi-region clauses.',
          suspects: 25,
          criminals: 9,
          difficulty: '5 / 5'
        };
      case 'puzzle_5x5_2.json':
        return {
          badge: 'MASTER',
          badgeColor: 'bg-fuchsia-100 text-fuchsia-700 border-fuchsia-200',
          desc: 'Campus conspiracy cascading row-by-row through professors and deans.',
          suspects: 25,
          criminals: 10,
          difficulty: '5 / 5'
        };
      case 'puzzle_5x5_3.json':
        return {
          badge: 'GRANDMASTER',
          badgeColor: 'bg-red-100 text-red-700 border-red-200',
          desc: 'Futuristic underworld with cyberpunk fixers and a staircase ribbon pattern.',
          suspects: 25,
          criminals: 10,
          difficulty: '5 / 5'
        };
      default:
        return {
          badge: `${size}x${size}`,
          badgeColor: 'bg-slate-100 text-slate-600 border-slate-200',
          desc: 'Custom puzzle investigation.',
          suspects: size * size,
          criminals: Math.floor((size * size) / 3),
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
    <div className="min-h-screen bg-[#F2F0FB] text-slate-700 flex flex-col justify-between selection:bg-violet-200/50 relative">
      {/* Animated Aura Mesh Background */}
      <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
        <div className="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] rounded-full bg-pink-200/40 blur-[120px] animate-pulse" style={{animationDuration: '8s'}} />
        <div className="absolute top-[30%] right-[-5%] w-[500px] h-[500px] rounded-full bg-violet-200/30 blur-[120px] animate-pulse" style={{animationDuration: '12s', animationDelay: '2s'}} />
        <div className="absolute bottom-[-10%] left-[20%] w-[550px] h-[550px] rounded-full bg-emerald-200/25 blur-[120px] animate-pulse" style={{animationDuration: '10s', animationDelay: '4s'}} />
      </div>

      {/* Top Banner Navigation */}
      <header className="border-b border-slate-200/60 bg-white/70 backdrop-blur-xl sticky top-0 z-20 px-4 md:px-8 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center shadow-lg shadow-violet-200/50 border border-violet-400/30">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <div>
            <h1 className="font-serif font-black text-lg md:text-xl tracking-wider text-slate-800">
              GRIDUCTIVE
            </h1>
            <p className="text-[10px] uppercase font-semibold tracking-widest text-slate-400">
              Propositional SAT Deduction
            </p>
          </div>
        </div>

        {/* Menu Navigation Tabs */}
        <nav className="flex items-center gap-1 md:gap-2 bg-slate-100/80 p-1 rounded-xl border border-slate-200 text-xs">
          <button
            onClick={() => setActiveTab('cases')}
            className={`px-3 py-1.5 rounded-lg font-medium transition-all flex items-center gap-1.5 ${
              activeTab === 'cases'
                ? 'bg-white text-slate-800 shadow-sm border border-slate-200'
                : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Select Case</span>
          </button>

          <button
            onClick={() => setActiveTab('rules')}
            className={`px-3 py-1.5 rounded-lg font-medium transition-all flex items-center gap-1.5 ${
              activeTab === 'rules'
                ? 'bg-white text-slate-800 shadow-sm border border-slate-200'
                : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            <HelpCircle className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">How to Play</span>
          </button>

          <button
            onClick={() => setActiveTab('about')}
            className={`px-3 py-1.5 rounded-lg font-medium transition-all flex items-center gap-1.5 ${
              activeTab === 'about'
                ? 'bg-white text-slate-800 shadow-sm border border-slate-200'
                : 'text-slate-500 hover:text-slate-700'
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
            <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-violet-500 via-pink-500 to-rose-400 p-6 md:p-8 shadow-2xl shadow-violet-200/50">
              <div className="relative z-10 max-w-2xl">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/20 backdrop-blur-sm border border-white/30 text-white text-xs font-semibold mb-3">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>CSC14003 - Artificial Intelligence Project</span>
                </div>
                <h2 className="text-2xl md:text-4xl font-serif font-black text-white tracking-tight leading-tight mb-2">
                  Solve cases purely through logic.
                </h2>
                <p className="text-sm md:text-base text-white/80 leading-relaxed mb-6 font-normal">
                  Every suspect is either a <span className="text-rose-200 font-semibold">Criminal</span> or <span className="text-emerald-200 font-semibold">Innocent</span>.
                  Every revealed clue is true. A verdict is accepted only when strictly proved by propositional SAT entailment.
                  <strong className="text-yellow-200"> Zero guessing allowed.</strong>
                </p>

                <div className="flex flex-wrap items-center gap-3">
                  <button
                    onClick={() => {
                      onSelectCase(currentPuzzle);
                      onStartPlaying();
                    }}
                    className="inline-flex items-center gap-2 px-6 py-3 rounded-2xl bg-white text-violet-700 font-semibold text-sm shadow-lg shadow-violet-600/30 hover:shadow-xl hover:shadow-violet-600/40 transition-all transform active:scale-95 cursor-pointer"
                  >
                    <Play className="w-4 h-4 fill-violet-700" />
                    <span>Investigate Daily Case</span>
                  </button>

                  <button
                    onClick={() => setActiveTab('rules')}
                    className="inline-flex items-center gap-2 px-4 py-3 rounded-2xl bg-white/15 backdrop-blur-sm hover:bg-white/25 text-white text-sm font-medium border border-white/30 transition-all cursor-pointer"
                  >
                    <span>Read Detective Rules</span>
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Decorative Background Badge */}
              <div className="absolute right-4 md:right-8 -bottom-10 opacity-10 pointer-events-none select-none text-white">
                <ShieldAlert className="w-64 h-64" />
              </div>
            </div>

            {/* Suspect Cast Showcase Preview */}
            <div className="bg-white/60 backdrop-blur-sm border border-slate-200/60 rounded-2xl p-4">
              <div className="flex items-center justify-between mb-3 px-1">
                <span className="text-xs uppercase font-bold tracking-wider text-slate-500">
                  Featured Suspects & Procedural Avatars
                </span>
                <span className="text-[11px] text-slate-400">
                  100% Vector SVG • 12 Hairstyles • 10 Colors
                </span>
              </div>
              <div className="flex items-center justify-between gap-2 overflow-x-auto py-1 scrollbar-none">
                {showcaseCast.map((c) => (
                  <div key={c.name} className="flex flex-col items-center flex-shrink-0 min-w-[70px]">
                    <div className="p-1 rounded-full bg-white border border-slate-200 hover:scale-105 hover:shadow-md transition-all">
                      <Avatar name={c.name} size={44} />
                    </div>
                    <span className="text-xs font-semibold text-slate-700 mt-1">{c.name}</span>
                    <span className="text-[10px] text-slate-400">{c.job}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Case Selection Cards Grid */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-serif font-bold text-lg text-slate-800 flex items-center gap-2">
                  <span>Available Mystery Cases</span>
                  <span className="text-xs font-sans font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-500 border border-slate-200">
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
                      className={`group relative rounded-2xl border p-5 flex flex-col justify-between cursor-pointer transition-all duration-300 hover:-translate-y-1.5 hover:shadow-xl ${
                        isCurrent
                          ? 'bg-white/90 backdrop-blur-xl border-violet-300 shadow-lg shadow-violet-100/50 ring-1 ring-violet-300/50'
                          : 'bg-white/70 backdrop-blur-sm border-slate-200/60 hover:border-violet-300 hover:bg-white/90 shadow-sm'
                      }`}
                    >
                      <div>
                        {/* Top Meta Header */}
                        <div className="flex items-center justify-between mb-2">
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-lg border uppercase tracking-wider ${meta.badgeColor}`}>
                            {meta.badge}
                          </span>
                          <span className="text-xs font-mono font-semibold text-slate-400">
                            {p.size} × {p.size} Grid
                          </span>
                        </div>

                        {/* Title & Desc */}
                        <h4 className="font-serif font-bold text-base text-slate-800 group-hover:text-violet-600 transition-colors">
                          {p.name}
                        </h4>
                        <p className="text-xs text-slate-500 leading-relaxed mt-1 mb-4">
                          {meta.desc}
                        </p>
                      </div>

                      {/* Card Footer Details */}
                      <div>
                        <div className="flex items-center justify-between text-[11px] text-slate-400 border-t border-slate-200/60 pt-3 mb-3">
                          <span>{meta.suspects} Suspects</span>
                          <span>•</span>
                          <span>{meta.criminals} Criminals</span>
                          <span>•</span>
                          <span>Diff: {meta.difficulty}</span>
                        </div>

                        <button className="w-full py-2 rounded-xl bg-slate-100 group-hover:bg-gradient-to-r group-hover:from-violet-500 group-hover:to-pink-500 group-hover:text-white text-slate-600 text-xs font-semibold flex items-center justify-center gap-1.5 transition-all">
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
              <h2 className="text-2xl md:text-3xl font-serif font-bold text-slate-800">
                How to Play Griductive
              </h2>
              <p className="text-sm text-slate-500 mt-1">
                A logic deduction puzzle based on pure propositional satisfiability.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Rule 1 */}
              <div className="bg-white/70 backdrop-blur-sm border border-slate-200/60 rounded-2xl p-5">
                <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-amber-400 to-orange-400 flex items-center justify-center text-white font-bold mb-3 shadow-md shadow-amber-100">
                  1
                </div>
                <h4 className="font-semibold text-sm text-slate-800 mb-1">
                  Hidden Truth & Public Clues
                </h4>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Every person on the grid is secretly either <strong className="text-rose-500">Criminal</strong> or <strong className="text-emerald-500">Innocent</strong>. All clues shown on cards are always 100% true, regardless of whether their owner is criminal or innocent.
                </p>
              </div>

              {/* Rule 2 */}
              <div className="bg-white/70 backdrop-blur-sm border border-slate-200/60 rounded-2xl p-5">
                <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-rose-400 to-pink-500 flex items-center justify-center text-white font-bold mb-3 shadow-md shadow-rose-100">
                  2
                </div>
                <h4 className="font-semibold text-sm text-slate-800 mb-1">
                  Strict Rule: NO GUESSING
                </h4>
                <p className="text-xs text-slate-500 leading-relaxed">
                  You cannot guess or flip cards blindly. When you call a verdict on a suspect, the Game Engine evaluates propositional entailment: <code className="text-violet-600 font-mono bg-violet-50 px-1 rounded">KB |= C_i</code> or <code className="text-violet-600 font-mono bg-violet-50 px-1 rounded">KB |= ¬C_i</code>. If it cannot be proven yet, it is rejected with <strong className="text-amber-600">NOT_PROVABLE</strong>!
                </p>
              </div>

              {/* Rule 3 */}
              <div className="bg-white/70 backdrop-blur-sm border border-slate-200/60 rounded-2xl p-5">
                <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white font-bold mb-3 shadow-md shadow-emerald-100">
                  3
                </div>
                <h4 className="font-semibold text-sm text-slate-800 mb-1">
                  Flipping Cards Reveals New Clues
                </h4>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Once a suspect's status is correctly proved and accepted, their card flips face-up, revealing their personal clue. This new clue is immediately added into the knowledge base, unlocking subsequent deductions.
                </p>
              </div>

              {/* Rule 4 */}
              <div className="bg-white/70 backdrop-blur-sm border border-slate-200/60 rounded-2xl p-5">
                <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-cyan-400 to-blue-500 flex items-center justify-center text-white font-bold mb-3 shadow-md shadow-cyan-100">
                  4
                </div>
                <h4 className="font-semibold text-sm text-slate-800 mb-1">
                  Interactive Hint & Deduction Trace
                </h4>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Stuck? Tap <strong className="text-cyan-600">Hint</strong> to highlight which suspect is currently forced by logic, along with the relevant clues. You can also view the full step-by-step SAT deduction trace in the <strong className="text-violet-600">Trace Drawer</strong>.
                </p>
              </div>
            </div>

            {/* Clue Types Table */}
            <div className="bg-white/70 backdrop-blur-sm border border-slate-200/60 rounded-2xl p-5 mt-6">
              <h4 className="font-serif font-bold text-sm text-slate-800 mb-3">
                Supported Clue Types & CNF Encodings
              </h4>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200/60">
                  <span className="font-mono font-bold text-violet-600">FACT</span>
                  <p className="text-[11px] text-slate-500 mt-0.5">Direct criminal or innocent status.</p>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200/60">
                  <span className="font-mono font-bold text-violet-600">SAME / DIFF</span>
                  <p className="text-[11px] text-slate-500 mt-0.5">Bi-conditional or XOR relationships.</p>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200/60">
                  <span className="font-mono font-bold text-violet-600">EXACTLY (k)</span>
                  <p className="text-[11px] text-slate-500 mt-0.5">Combinatorial cardinality constraints.</p>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200/60">
                  <span className="font-mono font-bold text-violet-600">PARITY / CMP</span>
                  <p className="text-[11px] text-slate-500 mt-0.5">Even/Odd and relative region counts.</p>
                </div>
              </div>
            </div>

            <div className="text-center pt-4">
              <button
                onClick={() => {
                  onSelectCase(currentPuzzle);
                  onStartPlaying();
                }}
                className="px-6 py-2.5 rounded-2xl bg-gradient-to-r from-violet-500 to-pink-500 hover:from-violet-400 hover:to-pink-400 text-white font-semibold text-xs transition-all cursor-pointer shadow-lg shadow-violet-200/50"
              >
                Back to Case Investigation
              </button>
            </div>
          </div>
        )}

        {/* --- TAB 3: ABOUT & TEAM MEMBERS --- */}
        {activeTab === 'about' && (
          <div className="space-y-6 animate-fadeIn max-w-2xl mx-auto">
            <div className="text-center max-w-xl mx-auto mb-6">
              <h2 className="text-2xl md:text-3xl font-serif font-bold text-slate-800">
                Project Information & Credits
              </h2>
              <p className="text-sm text-slate-500 mt-1">
                CSC14003 - Nhập môn Trí tuệ Nhân tạo • ĐHKHTN (VNU-HCM)
              </p>
            </div>

            <div className="bg-white/70 backdrop-blur-sm border border-slate-200/60 rounded-3xl p-6 shadow-xl space-y-5">
              <div className="flex items-center justify-between border-b border-slate-200/60 pb-3">
                <h4 className="font-serif font-bold text-base text-slate-800 flex items-center gap-2">
                  <Users className="w-4 h-4 text-violet-500" />
                  <span>Danh sách thành viên</span>
                </h4>
                <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-violet-100 text-violet-600 border border-violet-200">
                  5 Thành viên
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {/* Thành viên 1 */}
                <div className="p-3.5 rounded-2xl bg-white/80 border border-slate-200/60 flex items-center gap-3.5 hover:border-violet-300 hover:shadow-md transition-all">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-amber-400 to-orange-400 flex items-center justify-center font-bold text-white text-sm shadow-md">
                    1
                  </div>
                  <div>
                    <span className="font-semibold text-slate-800 text-sm block">Lương Nguyễn Hoàng Vũ</span>
                    <span className="text-xs text-amber-600 font-medium">24120493</span>
                  </div>
                </div>

                {/* Thành viên 2 */}
                <div className="p-3.5 rounded-2xl bg-white/80 border border-slate-200/60 flex items-center gap-3.5 hover:border-emerald-300 hover:shadow-md transition-all">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center font-bold text-white text-sm shadow-md">
                    2
                  </div>
                  <div>
                    <span className="font-semibold text-slate-800 text-sm block">Huỳnh Chí Thoại</span>
                    <span className="text-xs text-slate-500">24120457</span>
                  </div>
                </div>

                {/* Thành viên 3 */}
                <div className="p-3.5 rounded-2xl bg-white/80 border border-slate-200/60 flex items-center gap-3.5 hover:border-cyan-300 hover:shadow-md transition-all">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-400 to-blue-500 flex items-center justify-center font-bold text-white text-sm shadow-md">
                    3
                  </div>
                  <div>
                    <span className="font-semibold text-slate-800 text-sm block">Trần Minh Tiến</span>
                    <span className="text-xs text-slate-500">24120465</span>
                  </div>
                </div>

                {/* Thành viên 4 */}
                <div className="p-3.5 rounded-2xl bg-white/80 border border-slate-200/60 flex items-center gap-3.5 hover:border-purple-300 hover:shadow-md transition-all">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-violet-400 to-purple-500 flex items-center justify-center font-bold text-white text-sm shadow-md">
                    4
                  </div>
                  <div>
                    <span className="font-semibold text-slate-800 text-sm block">Đỗ Trung Kiên</span>
                    <span className="text-xs text-slate-500">24120350</span>
                  </div>
                </div>

                {/* Thành viên 5 */}
                <div className="p-3.5 rounded-2xl bg-white/80 border border-slate-200/60 flex items-center gap-3.5 hover:border-rose-300 hover:shadow-md transition-all sm:col-span-2 sm:max-w-xs sm:mx-auto sm:w-full">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-rose-400 to-pink-500 flex items-center justify-center font-bold text-white text-sm shadow-md">
                    5
                  </div>
                  <div>
                    <span className="font-semibold text-slate-800 text-sm block">Lê Phạm Đăng Khiêm</span>
                    <span className="text-xs text-slate-500">24120341</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200/60 bg-white/50 backdrop-blur-sm px-4 py-3 text-center text-xs text-slate-400">
        <span>Griductive Solver • Project 2 CSC14003 Artificial Intelligence • VNU-HCM University of Science</span>
      </footer>
    </div>
  );
}
