export type AlgorithmId = "bfs1" | "bfs2" | "dfs1" | "dfs2";
export type ScreenId = "puzzle" | "vacuum";

export interface SearchStepDto {
  action: string;
  current_state: number[] | [number, number] | null;
  generated_states: (number[] | [number, number])[];
  frontier: (number[] | [number, number])[];
  visited: (number[] | [number, number])[];
  found: boolean;
  path: (number[] | [number, number])[] | null;
  message: string;
  timed_out?: boolean;
}

export interface TreeEdge {
  from: string;
  to: string;
}

export interface TreeNode {
  id: string;
  label: string;
  depth?: number;
}

export interface SearchTree {
  nodes: TreeNode[];
  edges: TreeEdge[];
}

export interface SearchResult {
  mode: string;
  algorithm: string;
  found: boolean;
  message: string;
  elapsed_ms: number;
  steps_count: number;
  steps: SearchStepDto[];
  path: number[][] | [number, number][] | null;
  tree: SearchTree;
  timed_out?: boolean;
  path_points?: [number, number][];
  saved?: boolean;
  record_id?: string | null;
}

export interface DirtSpot {
  x: number;
  y: number;
  size: number;
  clean: boolean;
}
