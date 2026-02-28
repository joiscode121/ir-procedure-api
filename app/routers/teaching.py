from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.models.database import get_db, TeachingFile as TeachingFileModel
from app.schemas.schemas import TeachingFile, TeachingFileCreate

router = APIRouter()

@router.get("/", response_model=List[TeachingFile])
def get_teaching_files(
    status: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(TeachingFileModel)
    
    if status:
        query = query.filter(TeachingFileModel.status == status)
    if category:
        query = query.filter(TeachingFileModel.category == category)
    
    files = query.offset(skip).limit(limit).all()
    return files

@router.get("/{file_id}", response_model=TeachingFile)
def get_teaching_file(file_id: int, db: Session = Depends(get_db)):
    file = db.query(TeachingFileModel).filter(TeachingFileModel.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="Teaching file not found")
    return file

@router.post("/", response_model=TeachingFile)
def create_teaching_file(file: TeachingFileCreate, db: Session = Depends(get_db)):
    db_file = TeachingFileModel(**file.model_dump())
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

@router.put("/{file_id}", response_model=TeachingFile)
def update_teaching_file(file_id: int, file: TeachingFileCreate, db: Session = Depends(get_db)):
    db_file = db.query(TeachingFileModel).filter(TeachingFileModel.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="Teaching file not found")
    
    for key, value in file.model_dump().items():
        setattr(db_file, key, value)
    
    db.commit()
    db.refresh(db_file)
    return db_file

@router.delete("/{file_id}")
def delete_teaching_file(file_id: int, db: Session = Depends(get_db)):
    db_file = db.query(TeachingFileModel).filter(TeachingFileModel.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="Teaching file not found")
    
    db.delete(db_file)
    db.commit()
    return {"message": "Teaching file deleted successfully"}

@router.get("/analytics/status-counts")
def get_status_counts(db: Session = Depends(get_db)):
    counts = db.query(
        TeachingFileModel.status,
        func.count(TeachingFileModel.id).label("count")
    ).group_by(TeachingFileModel.status).all()
    
    return [{"status": status, "count": count} for status, count in counts]
