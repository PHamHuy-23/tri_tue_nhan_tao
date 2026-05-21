import { useCallback, useEffect, useState } from "react";
import { searchPuzzle } from "../api/client";
import type { AlgorithmId, SearchResult, SearchStepDto } from "../types";
import { colors } from "../theme/colors";
import { PixelButton } from "./PixelButton";

const GOAL = [1, 2, 3, 4, 5, 6, 7, 8, 0];
const TILE = 100;
const GAP = 8;

function shuffleBoard(): number[] {
  const board = [...GOAL];
  let empty = 8;
  let previous: number | null = null;
  for (let i = 0; i < 8; i++) {
    const neighbors = neighborIndexes(board, empty).filter(
      (n) => n !== previous || neighborIndexes(board, empty).length === 1,
    );
    const next = neighbors[Math.floor(Math.random() * neighbors.length)];
    [board[empty], board[next]] = [board[next], board[empty]];
    previous = empty;
    empty = next;
  }
  return board;
}

function neighborIndexes(board: number[], index: number): number[] {
  const row = Math.floor(index / 3);
  const col = index % 3;
  const result: number[] = [];
  if (row > 0) result.push(index - 3);
  if (row < 2) result.push(index + 3);
  if (col > 0) result.push(index - 1);
  if (col < 2) result.push(index + 1);
  return result;
}

interface Props {
  algorithm: AlgorithmId;
  applyToken: number;
  onSearchDone: (result: SearchResult) => void;
  onMessage: (msg: string) => void;
  onLoading: (v: boolean) => void;
}

export function EightPuzzle({
  algorithm,
  applyToken,
  onSearchDone,
  onMessage,
  onLoading,
}: Props) {
  const [board, setBoard] = useState(shuffleBoard);
  const [moves, setMoves] = useState(0);
  const [steps, setSteps] = useState<SearchStepDto[]>([]);
  const [stepIndex, setStepIndex] = useState(0);
  const [solutionPath, setSolutionPath] = useState<number[][]>([]);
  const [solutionIndex, setSolutionIndex] = useState(0);
  const [startBeforeSearch, setStartBeforeSearch] = useState<number[]>([]);

  const shuffle = useCallback(() => {
    setBoard(shuffleBoard());
    setMoves(0);
    setSteps([]);
    setStepIndex(0);
    setSolutionPath([]);
    onMessage("Đã trộn puzzle. Đưa về 1..8.");
  }, [onMessage]);

  const moveTile = (index: number) => {
    const empty = board.indexOf(0);
    if (!neighborIndexes(board, empty).includes(index)) {
      onMessage("Ô này không sát ô trống.");
      return;
    }
    const next = [...board];
    [next[empty], next[index]] = [next[index], next[empty]];
    setBoard(next);
    setMoves((m) => m + 1);
    if (JSON.stringify(next) === JSON.stringify(GOAL)) {
      onMessage("Hoàn thành puzzle!");
    } else {
      onMessage("Tốt. Tiếp tục nào.");
    }
  };

  useEffect(() => {
    if (!applyToken) return;
    let cancelled = false;
    (async () => {
      onLoading(true);
      onMessage(`Đang chạy ${algorithm.toUpperCase()}...`);
      setStartBeforeSearch([...board]);
      try {
        const result = await searchPuzzle(algorithm, board);
        if (cancelled) return;
        onSearchDone(result);
        if (!result.found || !result.path) {
          onMessage(`${algorithm.toUpperCase()} chưa tìm thấy. ${result.message}`);
          setSteps(result.steps);
          setStepIndex(0);
          return;
        }
        setSteps(result.steps);
        setStepIndex(0);
        setSolutionPath(result.path as number[][]);
        setSolutionIndex(0);
        onMessage(`${algorithm.toUpperCase()} đang hiển thị quá trình tìm...`);
      } catch (e) {
        onMessage(e instanceof Error ? e.message : "Lỗi API");
      } finally {
        onLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [applyToken]);

  useEffect(() => {
    if (!steps.length) return;
    const id = window.setInterval(() => {
      setStepIndex((i) => {
        const next = i + 1;
        if (next < steps.length) {
          const st = steps[next];
          if (st.current_state && Array.isArray(st.current_state) && st.current_state.length === 9) {
            setBoard([...(st.current_state as number[])]);
          }
          return next;
        }
        const last = steps[steps.length - 1];
        if (last?.found && solutionPath.length) {
          setBoard([...startBeforeSearch]);
          setSteps([]);
          setStepIndex(0);
        } else {
          setSteps([]);
        }
        return i;
      });
    }, 160);
    return () => clearInterval(id);
  }, [steps, solutionPath.length, startBeforeSearch]);

  useEffect(() => {
    if (steps.length || !solutionPath.length) return;
    const id = window.setInterval(() => {
      setSolutionIndex((idx) => {
        if (idx >= solutionPath.length) {
          setSolutionPath([]);
          onMessage("Đã áp dụng xong lời giải.");
          return 0;
        }
        setBoard([...solutionPath[idx]]);
        return idx + 1;
      });
    }, 280);
    return () => clearInterval(id);
  }, [steps.length, solutionPath, onMessage]);

  return (
    <section>
      <h1 style={{ fontSize: 18, margin: "0 0 8px" }}>8-PUZZLE</h1>
      <p className="muted" style={{ marginBottom: 20 }}>
        Click ô sát ô trống. APPLY gọi BFS/DFS qua API.
      </p>
      <div
        style={{
          display: "inline-grid",
          gridTemplateColumns: `repeat(3, ${TILE}px)`,
          gap: GAP,
          padding: 20,
          background: colors.panelDark,
          border: `4px solid ${colors.line}`,
        }}
      >
        {board.map((value, index) => (
          <button
            key={index}
            type="button"
            onClick={() => value !== 0 && moveTile(index)}
            style={{
              width: TILE,
              height: TILE,
              border: value ? `4px solid ${colors.accentGlow}` : `3px solid ${colors.line}`,
              background: value ? colors.accent : colors.bg,
              color: colors.bg,
              fontSize: value ? 36 : 12,
              boxShadow: value ? "5px 5px 0 #c44d32" : "none",
              cursor: value ? "pointer" : "default",
            }}
          >
            {value || ""}
          </button>
        ))}
      </div>
      <div style={{ marginTop: 20, display: "flex", gap: 16, alignItems: "center" }}>
        <span style={{ color: colors.accent, fontSize: 9 }}>Bước chơi: {moves}</span>
        <span className="muted">Goal: 123/456/78_</span>
        <PixelButton label="SHUFFLE" onClick={shuffle} small />
      </div>
    </section>
  );
}
