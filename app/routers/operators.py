from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.models.database import get_db, Operator as OperatorModel, Procedure as ProcedureModel
from app.schemas.schemas import Operator, OperatorCreate

router = APIRouter()

@router.get("/", response_model=List[Operator])
def get_operators(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    operators = db.query(OperatorModel).offset(skip).limit(limit).all()
    return operators

@router.get("/{operator_id}", response_model=Operator)
def get_operator(operator_id: int, db: Session = Depends(get_db)):
    operator = db.query(OperatorModel).filter(OperatorModel.id == operator_id).first()
    if not operator:
        raise HTTPException(status_code=404, detail="Operator not found")
    return operator

@router.post("/", response_model=Operator)
def create_operator(operator: OperatorCreate, db: Session = Depends(get_db)):
    db_operator = OperatorModel(**operator.model_dump())
    db.add(db_operator)
    db.commit()
    db.refresh(db_operator)
    return db_operator

@router.put("/{operator_id}", response_model=Operator)
def update_operator(operator_id: int, operator: OperatorCreate, db: Session = Depends(get_db)):
    db_operator = db.query(OperatorModel).filter(OperatorModel.id == operator_id).first()
    if not db_operator:
        raise HTTPException(status_code=404, detail="Operator not found")
    
    for key, value in operator.model_dump().items():
        setattr(db_operator, key, value)
    
    db.commit()
    db.refresh(db_operator)
    return db_operator

@router.delete("/{operator_id}")
def delete_operator(operator_id: int, db: Session = Depends(get_db)):
    db_operator = db.query(OperatorModel).filter(OperatorModel.id == operator_id).first()
    if not db_operator:
        raise HTTPException(status_code=404, detail="Operator not found")
    
    db.delete(db_operator)
    db.commit()
    return {"message": "Operator deleted successfully"}

@router.get("/{operator_id}/stats")
def get_operator_stats(operator_id: int, db: Session = Depends(get_db)):
    operator = db.query(OperatorModel).filter(OperatorModel.id == operator_id).first()
    if not operator:
        raise HTTPException(status_code=404, detail="Operator not found")
    
    procedures = db.query(ProcedureModel).filter(
        ProcedureModel.primary_operator_id == operator_id
    ).all()
    
    total_procedures = len(procedures)
    avg_fluoro_time = sum(p.fluoroscopy_time_seconds or 0 for p in procedures) / max(total_procedures, 1)
    avg_dap = sum(p.total_dap or 0 for p in procedures) / max(total_procedures, 1)
    
    return {
        "operator_id": operator_id,
        "operator_name": operator.name,
        "total_procedures": total_procedures,
        "avg_fluoroscopy_time_seconds": avg_fluoro_time,
        "avg_dap": avg_dap
    }
