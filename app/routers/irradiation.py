from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.models.database import get_db, IrradiationEvent as IrradiationEventModel, Procedure as ProcedureModel
from app.schemas.schemas import IrradiationEvent

router = APIRouter()

@router.get("/procedure/{procedure_id}", response_model=List[IrradiationEvent])
def get_irradiation_events(procedure_id: int, db: Session = Depends(get_db)):
    events = db.query(IrradiationEventModel).filter(
        IrradiationEventModel.procedure_id == procedure_id
    ).order_by(IrradiationEventModel.event_number).all()
    return events

@router.get("/dose-summary/{procedure_id}")
def get_dose_summary(procedure_id: int, db: Session = Depends(get_db)):
    procedure = db.query(ProcedureModel).filter(ProcedureModel.id == procedure_id).first()
    if not procedure:
        raise HTTPException(status_code=404, detail="Procedure not found")
    
    events = db.query(IrradiationEventModel).filter(
        IrradiationEventModel.procedure_id == procedure_id
    ).all()
    
    total_events = len(events)
    total_dap = sum(e.dap or 0 for e in events)
    total_kerma = sum(e.air_kerma or 0 for e in events)
    
    return {
        "procedure_id": procedure_id,
        "total_events": total_events,
        "total_dap": total_dap,
        "total_air_kerma": total_kerma,
        "fluoroscopy_time_seconds": procedure.fluoroscopy_time_seconds,
        "total_frames": procedure.total_frames
    }

@router.get("/analytics/dose-distribution")
def get_dose_distribution(db: Session = Depends(get_db)):
    result = db.query(
        func.avg(IrradiationEventModel.dap).label("avg_dap"),
        func.avg(IrradiationEventModel.air_kerma).label("avg_kerma"),
        func.max(IrradiationEventModel.dap).label("max_dap"),
        func.min(IrradiationEventModel.dap).label("min_dap")
    ).first()
    
    return {
        "avg_dap": float(result.avg_dap or 0),
        "avg_kerma": float(result.avg_kerma or 0),
        "max_dap": float(result.max_dap or 0),
        "min_dap": float(result.min_dap or 0)
    }
