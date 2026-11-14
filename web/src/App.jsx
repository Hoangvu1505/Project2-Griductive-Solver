import React, { useCallback, useState, useEffect, useRef } from 'react';
import TopNav from './components/TopNav';
import Sidebar from './components/Sidebar';
import Card from './components/Card';
import ActionModal from './components/ActionModal';
import TraceDrawer from './components/TraceDrawer';
import Toast from './components/Toast';
import MainMenu from './components/MainMenu';

export default function App() {
  const [currentView, setCurrentView] = useState('menu'); // 'menu' | 'game'
  const [puzzles, setPuzzles] = useState([]);
  const [currentPuzzle, setCurrentPuzzle] = useState('puzzle_4x4_1.json');
  const [gameState, setGameState] = useState(null);
  const [loading, setLoading] = useState(true);

  // Card interaction & highlights
  const [selectedCardForAction, setSelectedCardForAction] = useState(null);
  const [selectedClueOwner, setSelectedClueOwner] = useState(null);
  const [highlightedHintCell, setHighlightedHintCell] = useState(null);
  const [pencilNotes, setPencilNotes] = useState({});

  // Trace & feedback
  const [traceHistory, setTraceHistory] = useState([]);
  const [isTraceOpen, setIsTraceOpen] = useState(false);
  const [toast, setToast] = useState(null);
  const dismissToast = useCallback(() => setToast(null), []);

  // Timer
  const [timerSeconds, setTimerSeconds] = useState(10);
  const [isPaused, setIsPaused] = useState(false);

  // Auto solver loop
  const [isAutoSolving, setIsAutoSolving] = useState(false);
  const autoSolveRef = useRef(false);

  // 1. Initial Load: Fetch puzzles and default to 4x4 Knotwise daily puzzle
  useEffect(() => {
    fetch('/api/puzzles')
      .then((res) => res.json())
      .then((data) => {
        if (data.puzzles && data.puzzles.length > 0) {
          setPuzzles(data.puzzles);
          const defaultP = data.puzzles.find((p) => p.filename === 'puzzle_4x4_1.json') || data.puzzles[0];
          loadPuzzleState(defaultP.filename);
        }
      })
      .catch((err) => {
        console.error('Failed to load puzzles:', err);
        setLoading(false);
      });
  }, []);

  // Timer interval
  useEffect(() => {
    if (isPaused) return;
    const interval = setInterval(() => {
      setTimerSeconds((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [isPaused]);

  const loadPuzzleState = (filename) => {
    setLoading(true);
    fetch(`/api/state?file=${filename}`)
      .then((res) => res.json())
      .then((data) => {
        setGameState(data);
        setCurrentPuzzle(filename);
        setTraceHistory([]);
        setSelectedClueOwner(null);
        setHighlightedHintCell(null);
        setPencilNotes({});
        setTimerSeconds(0);
        setIsAutoSolving(false);
        autoSolveRef.current = false;
        setLoading(false);
      })
      .catch((err) => {
        console.error('Error loading state:', err);
        setLoading(false);
      });
  };

  // Handle Card Click
  const handleCardClick = (coord) => {
    if (!gameState || !gameState.cards) return;
    const card = gameState.cards[coord];
    if (!card) return;

    if (card.is_revealed) {
      // Clue highlight toggle
      setSelectedClueOwner((owner) => owner === coord ? null : coord);
    } else {
      // Open verdict submission modal
      setSelectedCardForAction(card);
    }
  };

  // Submit verdict to Python Backend
  const handleSubmitVerdict = (coord, status) => {
    fetch('/api/verdict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ coord, status })
    })
      .then((res) => res.json())
      .then((data) => {
        const { code, message, revealed_clue, state } = data;
        if (state) setGameState(state);

        if (code === 'ACCEPTED') {
          setToast({ type: 'ACCEPTED', message: `ACCEPTED: [${coord}] is proved ${status}!` });
          setTraceHistory((prev) => [
            ...prev,
            {
              step_number: prev.length + 1,
              proved_cell: coord,
              proved_name: state?.cards[coord]?.name || coord,
              proved_status: status,
              newly_revealed_clue_id: revealed_clue?.id || '',
              newly_revealed_clue_text: revealed_clue?.text || ''
            }
          ]);
          setHighlightedHintCell(null);
        } else if (code === 'NOT_PROVABLE') {
          setToast({ type: 'NOT_PROVABLE', message: `REJECTED [NOT_PROVABLE]: Neither verdict is forced yet! No guessing allowed.` });
        } else if (code === 'CONTRADICTED') {
          setToast({ type: 'CONTRADICTED', message: `REJECTED [CONTRADICTED]: The opposite verdict is logically forced!` });
        }
      })
      .catch((err) => console.error('Error submitting verdict:', err));
  };

  // Hint
  const handleHint = () => {
    fetch('/api/hint', { method: 'POST' })
      .then((res) => res.json())
      .then((data) => {
        if (data.hint) {
          const { cell, name, forced_status, relevant_clue_ids } = data.hint;
          const relatedCard = Object.values(gameState.cards).find(
            ({ clue }) => clue && relevant_clue_ids.includes(clue.id)
          );
          setHighlightedHintCell(cell);
          const verdictMessage = `HINT: ${name} [${cell}] can be logically proved as ${forced_status}!`;
          setToast({
            type: 'HINT',
            message: relatedCard
              ? `${verdictMessage} Related clue [${relatedCard.coord}] — ${relatedCard.clue.text}`
              : verdictMessage,
            duration: 8000
          });
        } else {
          setToast({ type: 'NOT_PROVABLE', message: 'HINT: No character is currently forced from public clues.' });
        }
      })
      .catch((err) => console.error('Error requesting hint:', err));
  };

  // Auto Step
  const handleAutoStep = () => {
    return fetch('/api/step', { method: 'POST' })
      .then((res) => res.json())
      .then((data) => {
        if (data.state) setGameState(data.state);
        if (data.step && data.step.proved_cell) {
          setTraceHistory((prev) => [...prev, data.step]);
          setToast({
            type: 'ACCEPTED',
            message: `LOGIC AGENT: Proved [${data.step.proved_cell}] as ${data.step.proved_status}`
          });
          setHighlightedHintCell(null);
          return true;
        } else {
          setToast({ type: 'NOT_PROVABLE', message: 'Auto Step: No further forced verdicts available.' });
          return false;
        }
      })
      .catch((err) => {
        console.error('Error auto step:', err);
        return false;
      });
  };

  // Auto Solve All Loop
  const handleToggleAutoSolveAll = () => {
    if (isAutoSolving) {
      setIsAutoSolving(false);
      autoSolveRef.current = false;
    } else {
      setIsAutoSolving(true);
      autoSolveRef.current = true;
      runAutoSolveLoop();
    }
  };

  const runAutoSolveLoop = async () => {
    if (!autoSolveRef.current) return;
    const progressMade = await handleAutoStep();
    if (progressMade && autoSolveRef.current) {
      setTimeout(runAutoSolveLoop, 280);
    } else {
      setIsAutoSolving(false);
      autoSolveRef.current = false;
    }
  };

  // Restart
  const handleRestart = () => {
    fetch('/api/restart', { method: 'POST' })
      .then((res) => res.json())
      .then((data) => {
        setGameState(data);
        setTraceHistory([]);
        setSelectedClueOwner(null);
        setHighlightedHintCell(null);
        setPencilNotes({});
        setIsAutoSolving(false);
        autoSolveRef.current = false;
        setToast({ type: 'ACCEPTED', message: 'Puzzle restarted to initial state.' });
      })
      .catch((err) => console.error('Error restarting:', err));
  };

  // Check Uniqueness
  const handleCheckUniqueness = () => {
    fetch('/api/check_uniqueness', { method: 'POST' })
      .then((res) => res.json())
      .then((data) => {
        if (data.is_unique) {
          alert(`UNIQUENESS VERIFIED:\n${data.message}\nThe puzzle complete clue set has exactly 1 satisfying model!`);
        } else {
          alert(`AMBIGUOUS PUZZLE:\n${data.message}\nFound ${data.model_count} satisfying models.`);
        }
      })
      .catch((err) => console.error('Error checking uniqueness:', err));
  };

  const handleSetPencil = (coord, value) => {
    setPencilNotes((prev) => ({ ...prev, [coord]: value }));
  };

  if (loading || !gameState) {
    return (
      <div className="min-h-screen bg-[#F2F0FB] flex items-center justify-center text-slate-500 font-sans text-lg">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-violet-200 border-t-violet-500 rounded-full animate-spin" />
          <span>Loading Griductive...</span>
        </div>
      </div>
    );
  }

  // --- 1. RENDER MAIN MENU VIEW ---
  if (currentView === 'menu') {
    return (
      <MainMenu
        puzzles={puzzles}
        currentPuzzle={currentPuzzle}
        onSelectCase={(filename) => {
          loadPuzzleState(filename);
        }}
        onStartPlaying={() => {
          setCurrentView('game');
        }}
      />
    );
  }

  // --- 2. RENDER ACTIVE GAME INVESTIGATION VIEW ---
  const { size = 3, cells = [], cards = {} } = gameState;
  const highlightedRefCells = new Set(cards[selectedClueOwner]?.clue?.referenced_cells);

  // Grid styling based on dimensions (3x3, 4x4, 5x5)
  const gridColsClass =
    size === 3 ? 'grid-cols-3 max-w-[500px]' :
    size === 4 ? 'grid-cols-4 max-w-[660px]' :
    'grid-cols-5 max-w-[800px]';

  return (
    <div className="min-h-screen bg-[#F2F0FB] flex flex-col font-sans text-slate-700 relative">
      {/* Animated Aura Mesh Background */}
      <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
        <div className="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] rounded-full bg-pink-200/40 blur-[120px] animate-pulse" style={{animationDuration: '8s'}} />
        <div className="absolute top-[30%] right-[-5%] w-[500px] h-[500px] rounded-full bg-violet-200/30 blur-[120px] animate-pulse" style={{animationDuration: '12s', animationDelay: '2s'}} />
        <div className="absolute bottom-[-10%] left-[20%] w-[550px] h-[550px] rounded-full bg-cyan-200/30 blur-[120px] animate-pulse" style={{animationDuration: '10s', animationDelay: '4s'}} />
      </div>

      {/* Top Header Bar */}
      <TopNav
        puzzles={puzzles}
        currentPuzzle={currentPuzzle}
        onSelectPuzzle={loadPuzzleState}
        onBackToMenu={() => setCurrentView('menu')}
        timerSeconds={timerSeconds}
        isPaused={isPaused}
        onTogglePause={() => setIsPaused(!isPaused)}
        onOpenHelp={() => alert("HOW TO PLAY GRIDUCTIVE:\n\n1. Every person is secretly a Criminal or Innocent.\n2. Visible clues are always true regardless of their owner's status.\n3. Tap a suspect to call Criminal or Innocent.\n4. No Guessing: A call is accepted ONLY if it is logically forced by the knowledge base.\n5. When accepted, the card flips and reveals its clue!\n6. Use Hint to spotlight the next provable card.")}
        onOpenTrace={() => setIsTraceOpen(true)}
        onCheckUniqueness={handleCheckUniqueness}
      />

      {/* Main Body */}
      <main className="flex-1 flex flex-col lg:flex-row items-center lg:items-start justify-center gap-4 lg:gap-8 p-3 md:p-6 max-w-7xl mx-auto w-full">
        {/* Left Sidebar */}
        <Sidebar
          gameState={gameState}
          onHint={handleHint}
          onAutoStep={handleAutoStep}
          onAutoSolveAll={handleToggleAutoSolveAll}
          onRestart={handleRestart}
          onBackToMenu={() => setCurrentView('menu')}
          isAutoSolving={isAutoSolving}
        />

        {/* Center: The Board */}
        <div className="flex-1 flex flex-col items-center justify-center w-full my-auto">
          <div className={`grid ${gridColsClass} gap-2 md:gap-3 w-full`}>
            {cells.map((coord) => {
              const cardData = cards[coord] || { coord, name: coord, profession: 'Citizen' };
              return (
                <Card
                  key={coord}
                  cardData={cardData}
                  isHighlightedRef={highlightedRefCells.has(coord)}
                  isHighlightedHint={highlightedHintCell === coord}
                  isSelectedClue={selectedClueOwner === coord}
                  pencilNote={pencilNotes[coord]}
                  onClick={handleCardClick}
                />
              );
            })}
          </div>
        </div>
      </main>

      {/* Action Verdict Modal */}
      <ActionModal
        isOpen={!!selectedCardForAction}
        cardData={selectedCardForAction}
        onClose={() => setSelectedCardForAction(null)}
        onSubmitVerdict={handleSubmitVerdict}
        onSetPencil={handleSetPencil}
      />

      {/* Trace Drawer */}
      <TraceDrawer
        isOpen={isTraceOpen}
        onClose={() => setIsTraceOpen(false)}
        traceHistory={traceHistory}
      />

      {/* Toast Feedback Banner */}
      <Toast toast={toast} onClose={dismissToast} />
    </div>
  );
}
