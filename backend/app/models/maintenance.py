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
    status: str = Field(default=MaintenanceStatus.OPEN)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    image_url: Optional[str] = None
    bids: List[dict] = Field(default=[])

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = [
            MaintenanceStatus.OPEN,
            MaintenanceStatus.IN_PROGRESS,
            MaintenanceStatus.COMPLETED,
            MaintenanceStatus.CANCELED
        ]
        if v and v not in valid_statuses:
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
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    image_url: Optional[str] = None

    # Fix the syntax error - this should be a proper field assignment
    validate_status = validator('status', allow_reuse=True)(MaintenanceRequest.validate_status)