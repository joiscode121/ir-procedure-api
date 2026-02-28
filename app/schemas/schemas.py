from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Operator Schemas
class OperatorBase(BaseModel):
    name: str
    role: str
    specialty: str
    npi: str
    is_active: bool = True

class OperatorCreate(OperatorBase):
    pass

class Operator(OperatorBase):
    id: int
    
    class Config:
        from_attributes = True

# Procedure Schemas
class ProcedureBase(BaseModel):
    accession_number: str
    procedure_name: str
    procedure_date: datetime
    room_number: str
    category: str
    subcategory: Optional[str] = None
    access_site: Optional[str] = None
    target_site: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    fluoroscopy_time_seconds: Optional[float] = None
    total_dap: Optional[float] = None
    total_air_kerma: Optional[float] = None
    total_frames: Optional[int] = None
    patient_age: Optional[int] = None
    patient_sex: Optional[str] = None
    patient_bmi: Optional[float] = None
    dictated_report: Optional[str] = None
    indication: Optional[str] = None
    findings: Optional[str] = None
    complications: Optional[str] = None
    video_path: Optional[str] = None
    teaching_status: Optional[str] = None
    teaching_notes: Optional[str] = None
    primary_operator_id: Optional[int] = None

class ProcedureCreate(ProcedureBase):
    pass

class Procedure(ProcedureBase):
    id: int
    
    class Config:
        from_attributes = True

# Irradiation Event Schemas
class IrradiationEventBase(BaseModel):
    procedure_id: int
    event_number: int
    acquisition_protocol: Optional[str] = None
    image_type: Optional[str] = None
    primary_angle: Optional[float] = None
    secondary_angle: Optional[float] = None
    table_longitude: Optional[float] = None
    table_latitude: Optional[float] = None
    dap: Optional[float] = None
    air_kerma: Optional[float] = None
    kvp: Optional[float] = None
    ma: Optional[float] = None
    duration_ms: Optional[int] = None
    event_datetime: Optional[datetime] = None
    task_label: Optional[str] = None
    anatomic_region: Optional[str] = None

class IrradiationEventCreate(IrradiationEventBase):
    pass

class IrradiationEvent(IrradiationEventBase):
    id: int
    
    class Config:
        from_attributes = True

# Video Frame Schemas
class VideoFrameBase(BaseModel):
    procedure_id: int
    irradiation_event_id: Optional[int] = None
    frame_number: int
    timestamp_seconds: float
    file_path: str
    anatomic_grid: Optional[int] = None
    anatomic_grid_label: Optional[str] = None
    grid_confidence: Optional[float] = None
    task_detected: Optional[str] = None
    tool_detected: Optional[str] = None
    body_part: Optional[str] = None

class VideoFrameCreate(VideoFrameBase):
    pass

class VideoFrame(VideoFrameBase):
    id: int
    
    class Config:
        from_attributes = True

# Teaching File Schemas
class TeachingFileBase(BaseModel):
    procedure_id: int
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    status: str = "draft"
    video_url: Optional[str] = None
    youtube_url: Optional[str] = None
    view_count: int = 0
    avg_rating: Optional[float] = None
    annotations: Optional[dict] = None

class TeachingFileCreate(TeachingFileBase):
    pass

class TeachingFile(TeachingFileBase):
    id: int
    
    class Config:
        from_attributes = True
