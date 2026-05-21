import type { SearchStepDto } from "../types";
import { compactState } from "../utils/stateFormat";
import { colors } from "../theme/colors";

interface Props {
  step: SearchStepDto | null;
  stepIndex: number;
  totalSteps: number;
  message: string;
  onOpenTree?: () => void;
}

function MiniPuzzle({ state }: { state: number[] }) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(3, 22px)",
        gap: 3,
        marginTop: 8,
      }}
    >
      {state.map((v, i) => (
        <div
          key={i}
          style={{
            width: 22,
            height: 22,
            background: v === 0 ? colors.bg : colors.accent,
            border: `2px solid ${colors.line}`,
            fontSize: 8,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: colors.bg,
          }}
        >
          {v || ""}
        </div>
      ))}
    </div>
  );
}

function Column({
  title,
  values,
  current,
}: {
  title: string;
  values: unknown[];
  current?: boolean;
}) {
  return (
    <div
      style={{
        flex: 1,
        background: colors.panelDark,
        border: `3px solid ${colors.line}`,
        padding: 8,
        minHeight: 280,
        fontSize: 7,
      }}
    >
      <div style={{ color: colors.accent, marginBottom: 8, textAlign: "center" }}>
        {title}
      </div>
      {current && Array.isArray(values) && values.length === 9 ? (
        <MiniPuzzle state={values as number[]} />
      ) : current ? (
        <div style={{ fontSize: 9, wordBreak: "break-all" }}>
          {compactState(values)}
        </div>
      ) : (
        <>
          <div className="muted">count: {values.length}</div>
          {values.slice(0, 8).map((s, i) => (
            <div key={i} style={{ marginTop: 6 }}>
              {compactState(s)}
            </div>
          ))}
          {values.length > 8 && <div className="muted">...</div>}
        </>
      )}
    </div>
  );
}

export function TracePanel({
  step,
  stepIndex,
  totalSteps,
  message,
  onOpenTree,
}: Props) {
  const current = step?.current_state ?? null;
  const frontier = step?.frontier ?? [];
  const visited = step?.visited ?? [];

  return (
    <div className="panel">
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 12,
        }}
      >
        <h2 className="panel-title" style={{ margin: 0 }}>
          SEARCH TRACE
        </h2>
        <span style={{ color: colors.accent, fontSize: 8 }}>
          {totalSteps ? `${stepIndex}/${totalSteps}` : "0/0"}
        </span>
      </div>
      <div style={{ display: "flex", gap: 6 }}>
        <Column title="ĐANG XÉT" values={current ?? []} current />
        <Column title="FRONTIER" values={frontier} />
        <Column title="REACHED" values={visited} />
      </div>
      <p className="muted" style={{ marginTop: 12 }}>
        {message}
      </p>
      {onOpenTree && (
        <div style={{ marginTop: 12 }}>
          <button
            type="button"
            onClick={onOpenTree}
            className="pixel-shadow pixel-border"
            style={{
              background: colors.blue,
              color: colors.bg,
              fontSize: 8,
              padding: "10px 14px",
              borderColor: colors.line,
            }}
          >
            BIỂU ĐỒ CÂY
          </button>
        </div>
      )}
    </div>
  );
}
