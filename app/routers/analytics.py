from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models.database import get_db, Procedure as ProcedureModel, Operator as OperatorModel

router = APIRouter()

@router.get("/summary")
def get_analytics_summary(db: Session = Depends(get_db)):
    total_procedures = db.query(func.count(ProcedureModel.id)).scalar()
    total_operators = db.query(func.count(OperatorModel.id)).filter(OperatorModel.is_active == True).scalar()
    
    avg_dap = db.query(func.avg(ProcedureModel.total_dap)).scalar() or 0
    avg_fluoro_time = db.query(func.avg(ProcedureModel.fluoroscopy_time_seconds)).scalar() or 0
    
    return {
        "total_procedures": total_procedures,
        "total_operators": total_operators,
        "avg_dap": float(avg_dap),
        "avg_fluoroscopy_time": float(avg_fluoro_time)
    }

@router.get("/procedures-by-category")
def get_procedures_by_category(db: Session = Depends(get_db)):
    results = db.query(
        ProcedureModel.category,
        func.count(ProcedureModel.id).label("count")
    ).group_by(ProcedureModel.category).all()
    
    return [{"category": cat, "count": count} for cat, count in results]

@router.get("/procedures-by-month")
def get_procedures_by_month(db: Session = Depends(get_db)):
    results = db.query(
        extract('year', ProcedureModel.procedure_date).label("year"),
        extract('month', ProcedureModel.procedure_date).label("month"),
        func.count(ProcedureModel.id).label("count")
    ).group_by("year", "month").order_by("year", "month").all()
    
    return [{"year": int(year), "month": int(month), "count": count} for year, month, count in results]

@router.get("/dose-trends")
def get_dose_trends(db: Session = Depends(get_db)):
    results = db.query(
        extract('year', ProcedureModel.procedure_date).label("year"),
        extract('month', ProcedureModel.procedure_date).label("month"),
        func.avg(ProcedureModel.total_dap).label("avg_dap"),
        func.avg(ProcedureModel.total_air_kerma).label("avg_kerma")
    ).group_by("year", "month").order_by("year", "month").all()
    
    return [{
        "year": int(year),
        "month": int(month),
        "avg_dap": float(avg_dap or 0),
        "avg_kerma": float(avg_kerma or 0)
    } for year, month, avg_dap, avg_kerma in results]

@router.get("/room-utilization")
def get_room_utilization(db: Session = Depends(get_db)):
    results = db.query(
        ProcedureModel.room_number,
        func.count(ProcedureModel.id).label("count")
    ).group_by(ProcedureModel.room_number).all()
    
    return [{"room": room, "count": count} for room, count in results]

@router.get("/operator-comparison")
def get_operator_comparison(db: Session = Depends(get_db)):
    results = db.query(
        OperatorModel.name,
        func.count(ProcedureModel.id).label("procedure_count"),
        func.avg(ProcedureModel.total_dap).label("avg_dap"),
        func.avg(ProcedureModel.fluoroscopy_time_seconds).label("avg_fluoro_time")
    ).join(ProcedureModel, ProcedureModel.primary_operator_id == OperatorModel.id)\
     .group_by(OperatorModel.name).all()
    
    return [{
        "operator": name,
        "procedure_count": count,
        "avg_dap": float(avg_dap or 0),
        "avg_fluoro_time": float(avg_fluoro or 0)
    } for name, count, avg_dap, avg_fluoro in results]
