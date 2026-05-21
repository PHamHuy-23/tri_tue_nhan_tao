from fastapi import APIRouter, HTTPException

from ..models import PuzzleSearchRequest, VacuumSearchRequest
from ..services.search_service import run_puzzle, run_vacuum
from ..services.supabase_service import supabase_service

router = APIRouter(prefix="/api/search", tags=["search"])


@router.post("/puzzle")
def search_puzzle(body: PuzzleSearchRequest):
    try:
        result = run_puzzle(body.algorithm, body.board)
    except KeyError:
        raise HTTPException(status_code=400, detail="Thuật toán không hợp lệ") from None
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    saved = supabase_service.save_search_run(result)
    result["saved"] = saved is not None
    result["record_id"] = saved.get("id") if saved else None
    return result


@router.post("/vacuum")
def search_vacuum(body: VacuumSearchRequest):
    try:
        dirt = [d.model_dump() for d in body.dirt]
        result = run_vacuum(
            body.algorithm,
            body.robot_x,
            body.robot_y,
            dirt,
            body.room_x,
            body.room_y,
            body.room_w,
            body.room_h,
            body.cell_size,
            body.timeout_sec,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if body.save:
        saved = supabase_service.save_search_run(result)
        result["saved"] = saved is not None
        result["record_id"] = saved.get("id") if saved else None
    else:
        result["saved"] = False
        result["record_id"] = None

    return result


@router.get("/history")
def search_history(limit: int = 20):
    return {
        "enabled": supabase_service.enabled,
        "items": supabase_service.list_recent(limit=min(limit, 50)),
    }
