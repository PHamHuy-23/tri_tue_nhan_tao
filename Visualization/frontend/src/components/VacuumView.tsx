import { useCallback, useEffect, useRef, useState } from "react";
import { searchVacuum } from "../api/client";
import type { AlgorithmId, DirtSpot, SearchResult, SearchStepDto } from "../types";
import { colors } from "../theme/colors";
import { PixelButton } from "./PixelButton";

const ROOM_W = 412;
const ROOM_H = 412;
const CELL = 34;
const ROBOT_R = 27;

function makeDirt(roomX: number, roomY: number): DirtSpot[] {
  const spots: DirtSpot[] = [];
  for (let i = 0; i < 72; i++) {
    spots.push({
      x: roomX + 30 + Math.random() * (ROOM_W - 60),
      y: roomY + 30 + Math.random() * (ROOM_H - 60),
      size: [5, 6, 7, 8][Math.floor(Math.random() * 4)],
      clean: false,
    });
  }
  return spots;
}

interface Props {
  algorithm: AlgorithmId;
  applyToken: number;
  continueToken: number;
  roomOffset: { x: number; y: number };
  onSearchDone: (result: SearchResult) => void;
  onMessage: (msg: string) => void;
  onLoading: (v: boolean) => void;
}

export function VacuumView({
  algorithm,
  applyToken,
  continueToken,
  roomOffset,
  onSearchDone,
  onMessage,
  onLoading,
}: Props) {
  const roomX = roomOffset.x;
  const roomY = roomOffset.y;

  const [robot, setRobot] = useState({
    x: roomX + ROOM_W / 2,
    y: roomY + ROOM_H / 2,
  });
  const [dirt, setDirt] = useState(() => makeDirt(roomX, roomY));
  const [keys, setKeys] = useState<Set<string>>(new Set());
  const [target, setTarget] = useState<{ x: number; y: number } | null>(null);
  const [autoPath, setAutoPath] = useState<[number, number][]>([]);
  const [pathIndex, setPathIndex] = useState(0);
  const [steps, setSteps] = useState<SearchStepDto[]>([]);
  const [stepIndex, setStepIndex] = useState(0);
  const [autoClean, setAutoClean] = useState(false);
  const [timedOut, setTimedOut] = useState(false);
  const [noLimit, setNoLimit] = useState(false);
  const [elapsedMs, setElapsedMs] = useState(0);
  const pendingPlan = useRef(false);

  const reset = useCallback(() => {
    setRobot({ x: roomX + ROOM_W / 2, y: roomY + ROOM_H / 2 });
    setTarget(null);
    setAutoPath([]);
    setPathIndex(0);
    setSteps([]);
    setStepIndex(0);
    setAutoClean(false);
    setTimedOut(false);
    setNoLimit(false);
    setElapsedMs(0);
    setDirt(makeDirt(roomX, roomY));
    onMessage("Chọn thuật toán rồi APPLY để robot dọn sạch phòng.");
  }, [roomX, roomY, onMessage]);

  const cleanNear = useCallback(
    (rx: number, ry: number) => {
      setDirt((prev) =>
        prev.map((s) => {
          if (s.clean) return s;
          const d = Math.hypot(rx - s.x, ry - s.y);
          return d < ROBOT_R + s.size ? { ...s, clean: true } : s;
        }),
      );
    },
    [],
  );

  const planSearch = useCallback(
    async (timeout: number | null) => {
      onLoading(true);
      onMessage(`${algorithm.toUpperCase()} đang tìm đường...`);
      try {
        const result = await searchVacuum({
          algorithm,
          robot_x: robot.x,
          robot_y: robot.y,
          dirt,
          room_x: roomX,
          room_y: roomY,
          room_w: ROOM_W,
          room_h: ROOM_H,
          cell_size: CELL,
          timeout_sec: timeout,
        });
        onSearchDone(result);
        setElapsedMs(result.elapsed_ms);
        setSteps(result.steps);
        setStepIndex(0);

        if (result.timed_out) {
          setTimedOut(true);
          setAutoClean(false);
          onMessage(`Quá ${Math.round(result.elapsed_ms / 1000)}s! Bấm TIẾP TỤC để chạy không giới hạn.`);
          return;
        }

        if (!result.found || !result.path_points?.length) {
          setAutoClean(false);
          onMessage(result.message);
          return;
        }

        const points = result.path_points.slice(1) as [number, number][];
        if (!points.length) {
          onMessage("Đã ở trên bui hoặc hoàn tất.");
          if (dirt.some((d) => !d.clean)) pendingPlan.current = true;
          return;
        }
        setAutoPath(points);
        setPathIndex(0);
        setTarget(null);
        onMessage(`Tìm xong (${result.elapsed_ms}ms). Robot đi ${points.length} bước.`);
      } catch (e) {
        onMessage(e instanceof Error ? e.message : "Lỗi API");
        setAutoClean(false);
      } finally {
        onLoading(false);
      }
    },
    [algorithm, robot, dirt, roomX, roomY, onSearchDone, onMessage, onLoading],
  );

  useEffect(() => {
    if (!applyToken) return;
    setAutoClean(true);
    setTimedOut(false);
    setNoLimit(false);
    void planSearch(60);
  }, [applyToken]);

  useEffect(() => {
    if (!continueToken) return;
    setNoLimit(true);
    setTimedOut(false);
    setAutoClean(true);
    void planSearch(null);
  }, [continueToken]);

  useEffect(() => {
    if (!steps.length) return;
    const id = setInterval(() => {
      setStepIndex((i) => {
        if (i + 1 < steps.length) return i + 1;
        setSteps([]);
        return 0;
      });
    }, 160);
    return () => clearInterval(id);
  }, [steps]);

  useEffect(() => {
    const speed = 4.4;
    const id = setInterval(() => {
      setRobot((r) => {
        let { x, y } = r;
        let tx = target?.x;
        let ty = target?.y;

        if (!keys.size && autoPath.length && pathIndex < autoPath.length) {
          [tx, ty] = autoPath[pathIndex];
        }

        let dx = 0;
        let dy = 0;
        if (keys.has("w") || keys.has("arrowup")) dy -= speed;
        if (keys.has("s") || keys.has("arrowdown")) dy += speed;
        if (keys.has("a") || keys.has("arrowleft")) dx -= speed;
        if (keys.has("d") || keys.has("arrowright")) dx += speed;

        if (!dx && !dy && tx != null && ty != null) {
          const diffX = tx - x;
          const diffY = ty - y;
          const dist = Math.hypot(diffX, diffY);
          if (dist <= speed) {
            x = tx;
            y = ty;
            if (autoPath.length && pathIndex < autoPath.length) {
              setPathIndex((pi) => pi + 1);
              if (pathIndex + 1 >= autoPath.length) {
                setAutoPath([]);
                setPathIndex(0);
                if (autoClean) pendingPlan.current = true;
              }
            } else {
              setTarget(null);
            }
          } else {
            dx = (speed * diffX) / dist;
            dy = (speed * diffY) / dist;
          }
        }

        x = Math.max(roomX + ROBOT_R, Math.min(roomX + ROOM_W - ROBOT_R, x + dx));
        y = Math.max(roomY + ROBOT_R, Math.min(roomY + ROOM_H - ROBOT_R, y + dy));
        cleanNear(x, y);
        return { x, y };
      });
    }, 16);
    return () => clearInterval(id);
  }, [keys, target, autoPath, pathIndex, autoClean, roomX, roomY, cleanNear]);

  useEffect(() => {
    if (!pendingPlan.current) return;
    pendingPlan.current = false;
    if (dirt.every((d) => d.clean)) {
      setAutoClean(false);
      onMessage(`Đã dọn sạch phòng! (${elapsedMs}ms)`);
      return;
    }
    if (autoClean) void planSearch(noLimit ? null : 60);
  }, [dirt, autoClean, noLimit, elapsedMs, planSearch, onMessage]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent, down: boolean) => {
      const k = e.key.toLowerCase();
      if (!["w", "a", "s", "d", "arrowup", "arrowdown", "arrowleft", "arrowright"].includes(k))
        return;
      e.preventDefault();
      setKeys((prev) => {
        const next = new Set(prev);
        if (down) next.add(k);
        else next.delete(k);
        return next;
      });
      if (down) {
        setTarget(null);
        setAutoPath([]);
        setAutoClean(false);
      }
    };
    window.addEventListener("keydown", (e) => onKey(e, true));
    window.addEventListener("keyup", (e) => onKey(e, false));
    return () => {
      window.removeEventListener("keydown", (e) => onKey(e, true));
      window.removeEventListener("keyup", (e) => onKey(e, false));
    };
  }, []);

  const cleaned = dirt.filter((d) => d.clean).length;
  const currentStep = steps[Math.min(stepIndex, steps.length - 1)] ?? null;

  const gridOverlay = (cells: [number, number][], color: string) =>
    cells.slice(-30).map((c, i) => (
      <div
        key={`${color}-${i}`}
        style={{
          position: "absolute",
          left: roomX + c[0] * CELL + CELL / 2 - 6,
          top: roomY + c[1] * CELL + CELL / 2 - 6,
          width: 12,
          height: 12,
          background: color,
          opacity: 0.7,
        }}
      />
    ));

  return (
    <section>
      <h1 style={{ fontSize: 18, margin: "0 0 8px" }}>MÁY HÚT BỤI</h1>
      <p className="muted">WASD / click phòng. Vacuum dùng goal = ô bụi gần nhất.</p>
      <div
        style={{
          position: "relative",
          width: ROOM_W + 32,
          height: ROOM_H + 32,
          marginTop: 16,
          border: `6px solid ${colors.wallLight}`,
          background: colors.wall,
        }}
        onClick={(e) => {
          const rect = e.currentTarget.getBoundingClientRect();
          const x = e.clientX - rect.left - 16;
          const y = e.clientY - rect.top - 16;
          if (x >= 0 && x <= ROOM_W && y >= 0 && y <= ROOM_H) {
            setTarget({ x: roomX + x, y: roomY + y });
            setAutoPath([]);
            setAutoClean(false);
          }
        }}
      >
        <div
          style={{
            position: "absolute",
            left: 16,
            top: 16,
            width: ROOM_W,
            height: ROOM_H,
            backgroundImage: `repeating-conic-gradient(${colors.floorA} 0% 25%, ${colors.floorB} 0% 50%)`,
            backgroundSize: "38px 38px",
          }}
        />
        {dirt.map((s, i) =>
          !s.clean ? (
            <div
              key={i}
              style={{
                position: "absolute",
                left: s.x - roomX + 16 - s.size,
                top: s.y - roomY + 16 - s.size,
                width: s.size * 2,
                height: s.size * 2,
                background: colors.dirt,
              }}
            />
          ) : null,
        )}
        {currentStep &&
          gridOverlay(
            (currentStep.visited ?? []).filter(
              (v): v is [number, number] => Array.isArray(v) && v.length === 2,
            ),
            "#3d5a80",
          )}
        {currentStep &&
          gridOverlay(
            (currentStep.frontier ?? []).filter(
              (v): v is [number, number] => Array.isArray(v) && v.length === 2,
            ),
            colors.accent,
          )}
        <div
          style={{
            position: "absolute",
            left: robot.x - roomX + 16 - ROBOT_R,
            top: robot.y - roomY + 16 - ROBOT_R,
            width: ROBOT_R * 2,
            height: ROBOT_R * 2,
            borderRadius: "50%",
            background: colors.blue,
            border: `4px solid #d7f6ff`,
            boxShadow: "5px 5px 0 #0a0f1a",
          }}
        />
        {autoPath.slice(pathIndex).map(([px, py], i) => (
          <div
            key={i}
            style={{
              position: "absolute",
              left: px - roomX + 16 - 4,
              top: py - roomY + 16 - 4,
              width: 8,
              height: 8,
              background: colors.green,
            }}
          />
        ))}
      </div>
      <div style={{ marginTop: 16, display: "flex", gap: 12, flexWrap: "wrap" }}>
        <span style={{ color: colors.accent, fontSize: 9 }}>
          Đã dọn: {cleaned}/{dirt.length}
        </span>
        {elapsedMs > 0 && (
          <span className="muted">Thời gian: {elapsedMs}ms</span>
        )}
        <PixelButton label="RESET" onClick={reset} small />
        {timedOut && (
          <span className="muted">Dùng nút TIẾP TỤC trên thanh công cụ</span>
        )}
      </div>
    </section>
  );
}
