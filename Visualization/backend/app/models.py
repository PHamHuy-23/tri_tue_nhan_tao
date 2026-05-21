from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field


class PuzzleSearchRequest(BaseModel):
    algorithm: Literal["bfs1", "bfs2", "dfs1", "dfs2"]
    board: List[int] = Field(..., min_length=9, max_length=9)


class DirtSpot(BaseModel):
    x: float
    y: float
    size: float = 6
    clean: bool = False


class VacuumSearchRequest(BaseModel):
    algorithm: Literal["bfs1", "bfs2", "dfs1", "dfs2"]
    robot_x: float
    robot_y: float
    dirt: List[DirtSpot]
    room_x: float
    room_y: float
    room_w: float
    room_h: float
    cell_size: float = 34
    timeout_sec: Optional[int] = 60
    save: bool = True
