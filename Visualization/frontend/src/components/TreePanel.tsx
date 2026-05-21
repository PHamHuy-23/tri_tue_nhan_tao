import { useMemo } from "react";
import type { SearchTree } from "../types";
import { colors } from "../theme/colors";

interface Props {
  tree: SearchTree | null;
  open: boolean;
  onClose: () => void;
}

interface LayoutNode {
  id: string;
  label: string;
  x: number;
  y: number;
}

export function TreePanel({ tree, open, onClose }: Props) {
  const layout = useMemo(() => {
    if (!tree?.nodes.length) return { nodes: [] as LayoutNode[], edges: [] };

    const children: Record<string, string[]> = {};
    const parents: Record<string, string | null> = {};
    for (const n of tree.nodes) {
      parents[n.id] = null;
      children[n.id] = [];
    }
    for (const e of tree.edges) {
      if (children[e.from]) children[e.from].push(e.to);
      if (parents[e.to] === null || parents[e.to] === undefined) {
        parents[e.to] = e.from;
      }
    }

    const roots = tree.nodes
      .map((n) => n.id)
      .filter((id) => !tree.edges.some((e) => e.to === id));
    const rootId = roots[0] ?? tree.nodes[0].id;

    const positions: Record<string, { x: number; y: number }> = {};
    const levels: Record<string, number> = {};

    function assign(id: string, depth: number, offset: number): number {
      levels[id] = depth;
      const kids = children[id] ?? [];
      if (!kids.length) {
        positions[id] = { x: offset, y: depth };
        return offset + 1;
      }
      let cursor = offset;
      const childXs: number[] = [];
      for (const kid of kids) {
        const end = assign(kid, depth + 1, cursor);
        childXs.push((cursor + end - 1) / 2);
        cursor = end;
      }
      const x = childXs.reduce((a, b) => a + b, 0) / childXs.length;
      positions[id] = { x, y: depth };
      return cursor;
    }

    assign(rootId, 0, 0);

    const nodeW = 140;
    const nodeH = 48;
    const gapX = 24;
    const gapY = 70;

    const nodes: LayoutNode[] = tree.nodes.map((n) => {
      const p = positions[n.id] ?? { x: 0, y: 0 };
      return {
        id: n.id,
        label: n.label,
        x: 40 + p.x * (nodeW + gapX),
        y: 40 + p.y * (nodeH + gapY),
      };
    });

    const idToPos = Object.fromEntries(nodes.map((n) => [n.id, n]));
    const edges = tree.edges
      .filter((e) => idToPos[e.from] && idToPos[e.to])
      .map((e) => ({
        from: idToPos[e.from],
        to: idToPos[e.to],
      }));

    const width = Math.max(400, ...nodes.map((n) => n.x + 160));
    const height = Math.max(300, ...nodes.map((n) => n.y + 80));

    return { nodes, edges, width, height };
  }, [tree]);

  if (!open) return null;

  return (
    <div className="tree-overlay" onClick={onClose} role="presentation">
      <div
        className="tree-modal"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-labelledby="tree-title"
      >
        <div className="tree-modal-header">
          <h2 id="tree-title" style={{ margin: 0, fontSize: 10, color: colors.blue }}>
            BIỂU ĐỒ CÂY TÌM KIẾM
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="pixel-border"
            style={{
              background: colors.red,
              color: colors.text,
              fontSize: 8,
              padding: "8px 12px",
            }}
          >
            ĐÓNG
          </button>
        </div>
        <div className="tree-canvas-wrap">
          {!tree?.nodes.length ? (
            <p className="muted">Chưa có dữ liệu cây. Chạy APPLY trước.</p>
          ) : (
            <svg
              width={layout.width ?? 600}
              height={layout.height ?? 400}
              viewBox={`0 0 ${layout.width ?? 600} ${layout.height ?? 400}`}
            >
              {layout.edges?.map((e, i) => (
                <line
                  key={i}
                  x1={e.from.x + 60}
                  y1={e.from.y + 40}
                  x2={e.to.x + 60}
                  y2={e.to.y}
                  stroke={colors.line}
                  strokeWidth={2}
                />
              ))}
              {layout.nodes.map((n) => (
                <g key={n.id}>
                  <rect
                    x={n.x}
                    y={n.y}
                    width={120}
                    height={40}
                    fill={colors.panelDark}
                    stroke={colors.accent}
                    strokeWidth={2}
                  />
                  <text
                    x={n.x + 8}
                    y={n.y + 24}
                    fill={colors.text}
                    fontSize={7}
                    fontFamily="Consolas, monospace"
                  >
                    {n.label.length > 14 ? `${n.label.slice(0, 12)}…` : n.label}
                  </text>
                </g>
              ))}
            </svg>
          )}
        </div>
        <p className="muted" style={{ padding: "0 20px 16px" }}>
          Cạnh = sinh state con từ state cha (expand). Giới hạn ~80 nút để hiển thị mượt.
        </p>
      </div>
    </div>
  );
}
