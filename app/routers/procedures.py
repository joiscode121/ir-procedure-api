from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.database import get_db, Procedure as ProcedureModel
from app.schemas.schemas import Procedure, ProcedureCreate

router = APIRouter()

@router.get("/", response_model=List[Procedure])
def get_procedures(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    operator_id: Optional[int] = None,
    room: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ProcedureModel)
    
    if category:
        query = query.filter(ProcedureModel.category == category)
    if operator_id:
        query = query.filter(ProcedureModel.primary_operator_id == operator_id)
    if room:
        query = query.filter(ProcedureModel.room_number == room)
    if search:
        query = query.filter(
            (ProcedureModel.procedure_name.contains(search)) |
            (ProcedureModel.accession_number.contains(search))
        )
    
    procedures = query.order_by(ProcedureModel.procedure_date.desc()).offset(skip).limit(limit).all()
    return procedures

@router.get("/{procedure_id}", response_model=Procedure)
def get_procedure(procedure_id: int, db: Session = Depends(get_db)):
    procedure = db.query(ProcedureModel).filter(ProcedureModel.id == procedure_id).first()
    if not procedure:
        raise HTTPException(status_code=404, detail="Procedure not found")
    return procedure

@router.post("/", response_model=Procedure)
def create_procedure(procedure: ProcedureCreate, db: Session = Depends(get_db)):
    db_procedure = ProcedureModel(**procedure.model_dump())
    db.add(db_procedure)
    db.commit()
    db.refresh(db_procedure)
    return db_procedure

@router.put("/{procedure_id}", response_model=Procedure)
def update_procedure(procedure_id: int, procedure: ProcedureCreate, db: Session = Depends(get_db)):
    db_procedure = db.query(ProcedureModel).filter(ProcedureModel.id == procedure_id).first()
    if not db_procedure:
        raise HTTPException(status_code=404, detail="Procedure not found")
    
    for key, value in procedure.model_dump().items():
        setattr(db_procedure, key, value)
    
    db.commit()
    db.refresh(db_procedure)
    return db_procedure

@router.delete("/{procedure_id}")
def delete_procedure(procedure_id: int, db: Session = Depends(get_db)):
    db_procedure = db.query(ProcedureModel).filter(ProcedureModel.id == procedure_id).first()
    if not db_procedure:
        raise HTTPException(status_code=404, detail="Procedure not found")
    
    db.delete(db_procedure)
    db.commit()
    return {"message": "Procedure deleted successfully"}
