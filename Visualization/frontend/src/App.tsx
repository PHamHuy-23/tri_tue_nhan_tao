import { useCallback, useEffect, useState } from "react";
import { checkHealth, getConfiguredApiBase } from "./api/client";
import { AlgorithmPanel } from "./components/AlgorithmPanel";
import { EightPuzzle } from "./components/EightPuzzle";
import { TracePanel } from "./components/TracePanel";
import { TreePanel } from "./components/TreePanel";
import { VacuumView } from "./components/VacuumView";
import { PixelButton } from "./components/PixelButton";
import type { AlgorithmId, ScreenId, SearchResult, SearchStepDto } from "./types";
import { colors } from "./theme/colors";

export default function App() {
  const [screen, setScreen] = useState<ScreenId>("puzzle");
  const [algorithm, setAlgorithm] = useState<AlgorithmId>("bfs1");
  const [applyToken, setApplyToken] = useState(0);
  const [continueToken, setContinueToken] = useState(0);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("Chọn thuật toán và bấm APPLY.");
  const [steps, setSteps] = useState<SearchStepDto[]>([]);
  const [stepIndex, setStepIndex] = useState(0);
  const [lastTree, setLastTree] = useState<SearchResult["tree"] | null>(null);
  const [treeOpen, setTreeOpen] = useState(false);
  const [timedOut, setTimedOut] = useState(false);
  const [apiStatus, setApiStatus] = useState<{ ok: boolean; message: string } | null>(
    null,
  );

  useEffect(() => {
    checkHealth().then(setApiStatus);
  }, []);

  const handleApply = () => setApplyToken((t) => t + 1);
  const handleContinue = () => setContinueToken((t) => t + 1);

  const onSearchDone = useCallback((result: SearchResult) => {
    setLastTree(result.tree);
    setSteps(result.steps);
    setStepIndex(0);
    setTimedOut(!!result.timed_out);
    if (result.steps.length) {
      const id = window.setInterval(() => {
        setStepIndex((i) => {
          if (i + 1 < result.steps.length) return i + 1;
          clearInterval(id);
          return i;
        });
      }, 160);
    }
  }, []);

  const currentStep = steps[Math.min(stepIndex, Math.max(0, steps.length - 1))] ?? null;

  return (
    <div className="app-shell">
      {apiStatus && !apiStatus.ok && (
        <div
          style={{
            background: colors.red,
            color: colors.text,
            padding: "10px 20px",
            fontSize: 8,
            lineHeight: 1.6,
          }}
        >
          API: {apiStatus.message}
          {!getConfiguredApiBase() && (
            <>
              <br />
              Netlify → Environment variables → VITE_API_URL = URL Render → Trigger deploy.
            </>
          )}
        </div>
      )}

      <header className="top-bar">
        <span style={{ fontSize: 12, color: colors.text }}>AI AGENT</span>
        <PixelButton
          label="8-PUZZLE"
          onClick={() => setScreen("puzzle")}
          active={screen === "puzzle"}
          small
        />
        <PixelButton
          label="VACUUM"
          onClick={() => setScreen("vacuum")}
          active={screen === "vacuum"}
          small
        />
        {screen === "vacuum" && timedOut && (
          <PixelButton label="TIẾP TỤC" onClick={handleContinue} active small />
        )}
      </header>

      <div className="main-layout">
        <AlgorithmPanel
          selected={algorithm}
          onSelect={setAlgorithm}
          onApply={handleApply}
          loading={loading}
        />

        <div>
          {screen === "puzzle" ? (
            <EightPuzzle
              algorithm={algorithm}
              applyToken={applyToken}
              onSearchDone={onSearchDone}
              onMessage={setMessage}
              onLoading={setLoading}
            />
          ) : (
            <VacuumView
              algorithm={algorithm}
              applyToken={applyToken}
              continueToken={continueToken}
              roomOffset={{ x: 0, y: 0 }}
              onSearchDone={onSearchDone}
              onMessage={setMessage}
              onLoading={setLoading}
            />
          )}
        </div>

        <TracePanel
          step={currentStep}
          stepIndex={steps.length ? Math.min(stepIndex + 1, steps.length) : 0}
          totalSteps={steps.length}
          message={message}
          onOpenTree={() => setTreeOpen(true)}
        />
      </div>

      <TreePanel tree={lastTree} open={treeOpen} onClose={() => setTreeOpen(false)} />
    </div>
  );
}
