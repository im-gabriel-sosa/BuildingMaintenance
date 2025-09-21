# app/api/endpoints/homeowner.py

from fastapi import APIRouter, Depends, status, HTTPException
from typing import Dict, List
from pymongo.errors import PyMongoError
from bson import ObjectId

# We get the payload from check_homeowner_role
from app.api.deps import check_homeowner_role
from app.db.mongodb import get_db
from app.models.maintenance import MaintenanceRequest, MaintenanceRequestUpdate

router = APIRouter(
    prefix="/homeowner",
    tags=["homeowner"],
    # This dependency runs for every endpoint in this router
    dependencies=[Depends(check_homeowner_role)]
)


@router.post("/requests", response_model=MaintenanceRequest, status_code=status.HTTP_201_CREATED)
async def create_maintenance_request(
        request: MaintenanceRequest,
        db=Depends(get_db),
        # Add the dependency here to get the token payload from the role check
        payload: Dict = Depends(check_homeowner_role)
):
    """
    Creates a new maintenance request for a homeowner.
    """
    try:
        # Get the authenticated user's ID from the token payload
        authenticated_user_id = payload.get("sub")

        # Security check: Ensure the ID in the token matches the one in the request
        if authenticated_user_id != request.homeowner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only create maintenance requests for your own account."
            )

        # Use Pydantic's model_dump to convert the model to a dictionary
        request_dict = request.model_dump()

        # Insert the new request into the database collection named 'requests'
        new_request = await db["requests"].insert_one(request_dict)

        # Retrieve the created document to return it
        created_request = await db["requests"].find_one({"_id": new_request.inserted_id})

        # To satisfy the response_model, we need to handle the ObjectId
        # Pydantic v2's `from_attributes` should handle this if configured,
        # but returning a dict after manual conversion is safest.
        if created_request:
            created_request["id"] = str(created_request["_id"])  # Add 'id' field
            return created_request

    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}"
        )

# (We will add GET, PUT, DELETE endpoints here later)