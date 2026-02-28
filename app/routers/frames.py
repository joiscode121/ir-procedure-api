from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.database import get_db, VideoFrame as VideoFrameModel
from app.schemas.schemas import VideoFrame

router = APIRouter()

@router.get("/procedure/{procedure_id}", response_model=List[VideoFrame])
def get_frames_by_procedure(
    procedure_id: int,
    grid: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(VideoFrameModel).filter(VideoFrameModel.procedure_id == procedure_id)
    
    if grid:
        query = query.filter(VideoFrameModel.anatomic_grid == grid)
    
    frames = query.order_by(VideoFrameModel.frame_number).all()
    return frames

@router.get("/grid/{grid_number}", response_model=List[VideoFrame])
def get_frames_by_grid(grid_number: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    frames = db.query(VideoFrameModel).filter(
        VideoFrameModel.anatomic_grid == grid_number
    ).offset(skip).limit(limit).all()
    return frames
