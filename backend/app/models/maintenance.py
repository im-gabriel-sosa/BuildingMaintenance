from datetime import datetime
from pydantic import BaseModel, Field, validator
from typing import Optional, List


class MaintenanceStatus:
    """
    Enums for the different states of a maintenance request.
    """
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELED = "canceled"


class MaintenanceRequest(BaseModel):
    """
    Pydantic model for a maintenance request.
    This model defines the structure and validation for our data.
    """
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    homeowner_id: str
    status: str = Field(MaintenanceStatus.OPEN)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    image_url: Optional[str] = None
    bids: List[dict] = Field([])

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = [
            MaintenanceStatus.OPEN,
            MaintenanceStatus.IN_PROGRESS,
            MaintenanceStatus.COMPLETED,
            MaintenanceStatus.CANCELED
        ]
        if v not in valid_statuses:
            raise ValueError(f'status must be one of {valid_statuses}')
        return v

    class Config:
        # Pydantic's configuration class
        # from_attributes is now used to replace orm_mode
        from_attributes = True


class MaintenanceRequestUpdate(BaseModel):
    """
    Pydantic model for updating a maintenance request.
    All fields are optional, so a partial update is possible.
    """
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    image_url: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = [
            MaintenanceStatus.OPEN,
            MaintenanceStatus.IN_PROGRESS,
            MaintenanceStatus.COMPLETED,
            MaintenanceStatus.CANCELED
        ]
        if v not in valid_statuses:
            raise ValueError(f'status must be one of {valid_statuses}')
        return v
