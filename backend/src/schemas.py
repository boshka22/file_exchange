from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ProcessingStatus(StrEnum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class ScanStatus(StrEnum):
    CLEAN = "clean"
    SUSPICIOUS = "suspicious"
    FAILED = "failed"


class AlertLevel(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class FileItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    original_name: str
    mime_type: str
    size: int = Field(ge=0)
    processing_status: str
    scan_status: str | None
    scan_details: str | None
    metadata_json: dict | None
    requires_attention: bool
    created_at: datetime
    updated_at: datetime


class AlertItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    file_id: str
    level: str
    message: str
    created_at: datetime


class FileUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
