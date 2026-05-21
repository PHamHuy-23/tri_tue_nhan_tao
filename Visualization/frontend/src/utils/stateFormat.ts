export function compactState(state: unknown): string {
  if (!state) return "-";
  if (Array.isArray(state) && state.length === 9) {
    const rows = [state.slice(0, 3), state.slice(3, 6), state.slice(6, 9)];
    return rows
      .map((r) => r.map((v) => (v === 0 ? "_" : String(v))).join(""))
      .join("/");
  }
  if (Array.isArray(state) && state.length === 2) {
    return `(${state[0]},${state[1]})`;
  }
  return String(state);
}
