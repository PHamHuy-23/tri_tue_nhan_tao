import { useState } from "react";
import type { AlgorithmId } from "../types";
import { PixelButton } from "./PixelButton";
import { colors } from "../theme/colors";

const OPTIONS: AlgorithmId[] = ["bfs1", "bfs2", "dfs1", "dfs2"];

interface Props {
  selected: AlgorithmId;
  onSelect: (id: AlgorithmId) => void;
  onApply: () => void;
  loading?: boolean;
}

export function AlgorithmPanel({ selected, onSelect, onApply, loading }: Props) {
  const [expanded, setExpanded] = useState(false);

  return (
    <aside className="panel" style={{ minHeight: 420 }}>
      <h2 className="panel-title">THUẬT TOÁN</h2>
      <button
        type="button"
        onClick={() => setExpanded((e) => !e)}
        className="pixel-border"
        style={{
          width: "100%",
          background: colors.panelDark,
          color: colors.accent,
          padding: "10px 12px",
          fontSize: 9,
          textAlign: "left",
          marginBottom: 8,
        }}
      >
        {selected.toUpperCase()} {expanded ? "^" : "v"}
      </button>
      {expanded &&
        OPTIONS.map((opt) => (
          <button
            key={opt}
            type="button"
            onClick={() => {
              onSelect(opt);
              setExpanded(false);
            }}
            style={{
              display: "block",
              width: "100%",
              marginBottom: 6,
              padding: "8px 10px",
              fontSize: 8,
              background: opt === selected ? colors.accent : colors.panelDark,
              color: opt === selected ? colors.bg : colors.text,
              border: `2px solid ${colors.line}`,
            }}
          >
            {opt.toUpperCase()}
          </button>
        ))}
      <div style={{ marginTop: 24 }}>
        <PixelButton
          label={loading ? "..." : "APPLY"}
          onClick={onApply}
          active
        />
      </div>
      <p className="muted" style={{ marginTop: 16 }}>
        BFS1/DFS1: lấy goal khi dequeue/pop
        <br />
        BFS2/DFS2: goal khi sinh state
      </p>
    </aside>
  );
}
