from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List
from app.models.database import get_db, Procedure as ProcedureModel, Operator as OperatorModel

router = APIRouter()

@router.get("/")
def search_all(q: str = Query(..., min_length=2), db: Session = Depends(get_db)):
    # Search procedures
    procedures = db.query(ProcedureModel).filter(
        or_(
            ProcedureModel.procedure_name.contains(q),
            ProcedureModel.accession_number.contains(q),
            ProcedureModel.dictated_report.contains(q),
            ProcedureModel.indication.contains(q),
            ProcedureModel.findings.contains(q)
        )
    ).limit(20).all()
    
    # Search operators
    operators = db.query(OperatorModel).filter(
        or_(
            OperatorModel.name.contains(q),
            OperatorModel.specialty.contains(q),
            OperatorModel.npi.contains(q)
        )
    ).limit(20).all()
    
    return {
        "procedures": [
            {
                "id": p.id,
                "accession_number": p.accession_number,
                "procedure_name": p.procedure_name,
                "procedure_date": p.procedure_date,
                "type": "procedure"
            } for p in procedures
        ],
        "operators": [
            {
                "id": o.id,
                "name": o.name,
                "role": o.role,
                "specialty": o.specialty,
                "type": "operator"
            } for o in operators
        ]
    }
