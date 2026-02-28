from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./radflow.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Operator(Base):
    __tablename__ = "operators"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    role = Column(String)  # attending/fellow/resident/PA
    specialty = Column(String)
    npi = Column(String, unique=True)
    is_active = Column(Boolean, default=True)
    
    primary_procedures = relationship("Procedure", back_populates="primary_operator")
    procedure_associations = relationship("ProcedureOperator", back_populates="operator")

class Procedure(Base):
    __tablename__ = "procedures"
    
    id = Column(Integer, primary_key=True, index=True)
    accession_number = Column(String, unique=True, index=True)
    procedure_name = Column(String, index=True)
    procedure_date = Column(DateTime, index=True)
    room_number = Column(String)
    category = Column(String, index=True)  # cardiac/vascular/neuro/GI/GU/MSK/pulmonary
    subcategory = Column(String)
    access_site = Column(String)
    target_site = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration_minutes = Column(Integer)
    fluoroscopy_time_seconds = Column(Float)
    total_dap = Column(Float)  # Dose Area Product
    total_air_kerma = Column(Float)
    total_frames = Column(Integer)
    patient_age = Column(Integer)
    patient_sex = Column(String)
    patient_bmi = Column(Float)
    dictated_report = Column(Text)
    indication = Column(Text)
    findings = Column(Text)
    complications = Column(Text)
    video_path = Column(String)
    teaching_status = Column(String)
    teaching_notes = Column(Text)
    
    primary_operator_id = Column(Integer, ForeignKey("operators.id"))
    primary_operator = relationship("Operator", back_populates="primary_procedures")
    
    operator_associations = relationship("ProcedureOperator", back_populates="procedure")
    irradiation_events = relationship("IrradiationEvent", back_populates="procedure")
    video_frames = relationship("VideoFrame", back_populates="procedure")
    teaching_files = relationship("TeachingFile", back_populates="procedure")

class ProcedureOperator(Base):
    __tablename__ = "procedure_operators"
    
    id = Column(Integer, primary_key=True, index=True)
    procedure_id = Column(Integer, ForeignKey("procedures.id"))
    operator_id = Column(Integer, ForeignKey("operators.id"))
    role = Column(String)
    
    procedure = relationship("Procedure", back_populates="operator_associations")
    operator = relationship("Operator", back_populates="procedure_associations")

class IrradiationEvent(Base):
    __tablename__ = "irradiation_events"
    
    id = Column(Integer, primary_key=True, index=True)
    procedure_id = Column(Integer, ForeignKey("procedures.id"), index=True)
    event_number = Column(Integer)
    acquisition_protocol = Column(String)
    image_type = Column(String)  # fluoro/acquisition/DSA
    primary_angle = Column(Float)
    secondary_angle = Column(Float)
    table_longitude = Column(Float)
    table_latitude = Column(Float)
    dap = Column(Float)
    air_kerma = Column(Float)
    kvp = Column(Float)
    ma = Column(Float)
    duration_ms = Column(Integer)
    collimation_x1 = Column(Float)
    collimation_x2 = Column(Float)
    collimation_y1 = Column(Float)
    collimation_y2 = Column(Float)
    event_datetime = Column(DateTime)
    task_label = Column(String)
    anatomic_region = Column(String)
    
    procedure = relationship("Procedure", back_populates="irradiation_events")
    video_frames = relationship("VideoFrame", back_populates="irradiation_event")

class VideoFrame(Base):
    __tablename__ = "video_frames"
    
    id = Column(Integer, primary_key=True, index=True)
    procedure_id = Column(Integer, ForeignKey("procedures.id"), index=True)
    irradiation_event_id = Column(Integer, ForeignKey("irradiation_events.id"))
    frame_number = Column(Integer)
    timestamp_seconds = Column(Float)
    file_path = Column(String)
    anatomic_grid = Column(Integer)  # 1-29
    anatomic_grid_label = Column(String)
    grid_confidence = Column(Float)
    task_detected = Column(String)
    tool_detected = Column(String)
    body_part = Column(String)
    
    procedure = relationship("Procedure", back_populates="video_frames")
    irradiation_event = relationship("IrradiationEvent", back_populates="video_frames")

class TeachingFile(Base):
    __tablename__ = "teaching_files"
    
    id = Column(Integer, primary_key=True, index=True)
    procedure_id = Column(Integer, ForeignKey("procedures.id"), index=True)
    title = Column(String)
    description = Column(Text)
    category = Column(String, index=True)
    status = Column(String, index=True)  # draft/screened/approved/published
    video_url = Column(String)
    youtube_url = Column(String)
    view_count = Column(Integer, default=0)
    avg_rating = Column(Float)
    annotations = Column(JSON)
    
    procedure = relationship("Procedure", back_populates="teaching_files")

class AnatomicGrid(Base):
    __tablename__ = "anatomic_grids"
    
    id = Column(Integer, primary_key=True, index=True)
    grid_number = Column(Integer, unique=True)
    label = Column(String)
    body_region = Column(String)
    description = Column(Text)

# Create all tables
Base.metadata.create_all(bind=engine)
