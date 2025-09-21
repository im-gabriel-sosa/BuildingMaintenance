# backend/app/models/maintenance.py
from datetime import datetime
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from app.api.utils import PyObjectId


class MaintenanceStatus:
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELED = "canceled"


class MaintenanceRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    homeowner_id: str
    status: Optional[str] = Field(default=MaintenanceStatus.OPEN)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    image_url: Optional[str] = None
    bids: List[dict] = Field(default=[])

    @validator('status', pre=True, always=True)
    def validate_status(cls, v):
        # If status is None or empty, set to default
        if not v:
            return MaintenanceStatus.OPEN

        valid_statuses = [
            MaintenanceStatus.OPEN,
            MaintenanceStatus.IN_PROGRESS,
            MaintenanceStatus.COMPLETED,
            MaintenanceStatus.CANCELED
        ]
        if v not in valid_statuses:
            raise ValueError(f'status must be one of {valid_statuses}')
        return v


class MaintenanceRequestOut(MaintenanceRequest):
    # Use our PyObjectId helper for the id field
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {PyObjectId: str}


class MaintenanceRequestUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, min_length=10, max_length=500)
    status: Optional[str] = None
    image_url: Optional[str] = None

    @validator('status', pre=True)
    def validate_status(cls, v):
        if v is None:
            return v

        valid_statuses = [
            MaintenanceStatus.OPEN,
            MaintenanceStatus.IN_PROGRESS,
            MaintenanceStatus.COMPLETED,
            MaintenanceStatus.CANCELED
        ]
        if v not in valid_statuses:
            raise ValueError(f'status must be one of {valid_statuses}')
        return v