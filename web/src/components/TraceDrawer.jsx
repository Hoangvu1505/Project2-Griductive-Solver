import React from 'react';
import { X, Terminal, CheckCircle2, ShieldAlert } from 'lucide-react';

export default function TraceDrawer({ isOpen, onClose, traceHistory = [] }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/50 backdrop-blur-xs flex justify-end animate-in fade-in duration-150">
      <div className="w-full max-w-md bg-[#1c1815] border-l border-[#332b25] h-full flex flex-col shadow-2xl text-[#d6cec6]">
        {/* Header */}
        <div className="p-4 border-b border-[#2e2621] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4 text-cyan-400" />
            <h2 className="font-bold text-sm text-[#f2ece6]">Deduction Trace & SAT Log</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-[#8a7f74] hover:text-[#f2ece6] hover:bg-[#2b241e] transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content list */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3 font-mono text-xs">
          {traceHistory.length === 0 ? (
            <div className="text-center text-[#73685e] my-12 italic">
              No deduction steps recorded yet.<br />
              Make a verdict call or use Auto Step to generate proofs.
            </div>
          ) : (
            traceHistory.map((step, idx) => (
              <div key={idx} className="bg-[#241e1a] border border-[#382f28] rounded-xl p-3 shadow-xs">
                <div className="flex items-center justify-between mb-1.5 pb-1 border-b border-[#332a24]">
                  <span className="font-bold text-cyan-300">
                    Step {step.step_number || idx + 1}
                  </span>
                  <span className="text-[10px] text-[#8a7f74]">
                    Active Clues: {step.active_clue_ids ? step.active_clue_ids.length : 0}
                  </span>
                </div>

                {/* Queries */}
                {step.sat_queries && step.sat_queries.length > 0 && (
                  <div className="space-y-1 mb-2 text-[11px] text-[#a89d91]">
                    {step.sat_queries.slice(0, 4).map((q, qIdx) => (
                      <div key={qIdx} className="flex items-center justify-between">
                        <span>
                          KB ∧ {q.tested_status === 'CRIMINAL' ? '¬' : ''}C_{q.target_cell}
                        </span>
                        <span className={q.is_sat ? 'text-[#8a7f74]' : 'text-emerald-400 font-bold'}>
                          {q.is_sat ? 'SAT' : 'UNSAT (Forced!)'}
                        </span>
                      </div>
                    ))}
                    {step.sat_queries.length > 4 && (
                      <div className="text-[10px] text-[#73685e] italic">
                        + {step.sat_queries.length - 4} more queries
                      </div>
                    )}
                  </div>
                )}

                {/* Verdict Result */}
                {step.proved_cell && (
                  <div className="bg-[#1a1512] rounded p-1.5 flex items-center justify-between text-xs">
                    <span className="font-semibold text-[#f2ece6]">
                      {step.proved_cell} ({step.proved_name}):
                    </span>
                    <span className={step.proved_status === 'CRIMINAL' ? 'text-red-400 font-bold' : 'text-emerald-400 font-bold'}>
                      {step.proved_status}
                    </span>
                  </div>
                )}

                {/* Revealed Clue */}
                {step.newly_revealed_clue_id && (
                  <div className="mt-1.5 text-[10px] text-[#9e9083]">
                    <span className="font-semibold text-[#c7bebc]">Revealed: </span>
                    {step.newly_revealed_clue_text}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

