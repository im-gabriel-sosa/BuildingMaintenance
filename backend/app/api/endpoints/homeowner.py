# backend/app/api/endpoints/homeowner.py
from fastapi import APIRouter, Depends, status, HTTPException, Request
from typing import Dict, List, Optional
from pymongo.errors import PyMongoError
import logging
from bson import ObjectId
from datetime import datetime
from app.api.deps import check_homeowner_role
from app.db.mongodb import get_db
from app.models.maintenance import MaintenanceRequest, MaintenanceRequestUpdate, MaintenanceStatus
import json

# Set up logging
logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/homeowner",
    tags=["homeowner"],
    dependencies=[Depends(check_homeowner_role)]
)


def serialize_mongo_doc(doc):
    """Convert MongoDB document to JSON-serializable format"""
    if doc is None:
        return None
    # Convert ObjectId to string
    if "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]  # Remove the original _id field
    # Convert any other ObjectId fields
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)
        elif isinstance(value, datetime):
            doc[key] = value.isoformat()
    return doc


@router.get("/debug/requests")
async def debug_requests(
        db=Depends(get_db),
        payload: Dict = Depends(check_homeowner_role)
):
    """Debug endpoint to see what's actually in the database"""
    try:
        user_id = payload.get("sub")
        logger.debug(f"Debug: Looking for requests for user: {user_id}")

        # Get raw documents
        requests_cursor = db["requests"].find({"homeowner_id": user_id})
        requests_list = await requests_cursor.to_list(length=100)

        logger.debug(f"Debug: Found {len(requests_list)} raw documents")

        debug_info = []
        for i, doc in enumerate(requests_list):
            doc_info = {
                "index": i,
                "_id": str(doc.get('_id')),
                "_id_type": str(type(doc.get('_id'))),
                "homeowner_id": doc.get('homeowner_id'),
                "title": doc.get('title'),
                "status": doc.get('status'),
                "created_at": str(doc.get('created_at'))
            }
            debug_info.append(doc_info)
            logger.debug(f"Document {i}: {doc_info}")

        return {
            "total_found": len(requests_list),
            "user_id": user_id,
            "documents": debug_info
        }
    except Exception as e:
        logger.error(f"Debug endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/requests")
async def get_all_requests_for_homeowner(
        db=Depends(get_db),
        payload: Dict = Depends(check_homeowner_role)
):
    """
    Retrieves all maintenance requests submitted by the authenticated homeowner.
    """
    try:
        logger.debug("Starting get_all_requests_for_homeowner")
        user_id = payload.get("sub")
        logger.debug(f"User ID from token: {user_id}")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID not found in token"
            )

        # Query the database
        logger.debug("Querying requests collection...")
        requests_cursor = db["requests"].find({"homeowner_id": user_id})
        requests_list = await requests_cursor.to_list(length=100)
        logger.debug(f"Found {len(requests_list)} requests")

        # Serialize MongoDB documents
        serialized_requests = []
        for request_doc in requests_list:
            logger.debug(
                f"Processing document with _id: {request_doc.get('_id')} (type: {type(request_doc.get('_id'))})")
            serialized_request = serialize_mongo_doc(request_doc.copy())
            logger.debug(
                f"Serialized to ID: {serialized_request.get('id')} (type: {type(serialized_request.get('id'))})")
            serialized_requests.append(serialized_request)

        logger.debug(f"Serialized {len(serialized_requests)} requests")
        return serialized_requests

    except HTTPException:
        raise
    except PyMongoError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.exception("Full traceback:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/requests/{request_id}")
async def get_request_by_id(
        request_id: str,
        db=Depends(get_db),
        payload: Dict = Depends(check_homeowner_role)
):
    """
    Retrieves a specific maintenance request by ID for the authenticated homeowner.
    """
    try:
        logger.debug(f"Getting request with ID: {request_id}")
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID not found in token"
            )

        # Validate ObjectId format
        try:
            object_id = ObjectId(request_id)
            logger.debug(f"Converted '{request_id}' to ObjectId: {object_id}")
        except Exception as e:
            logger.error(f"Invalid ObjectId format '{request_id}': {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request ID format"
            )

        # Find the request and ensure it belongs to the user
        logger.debug(f"Searching for request with _id={object_id} and homeowner_id={user_id}")
        request_doc = await db["requests"].find_one({
            "_id": object_id,
            "homeowner_id": user_id
        })

        if not request_doc:
            logger.error(f"Request not found: _id={object_id}, homeowner_id={user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found or you don't have permission to access it"
            )

        return serialize_mongo_doc(request_doc.copy())

    except HTTPException:
        raise
    except PyMongoError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/requests", status_code=status.HTTP_201_CREATED)
async def create_maintenance_request(
        request_data: Request,
        db=Depends(get_db),
        payload: Dict = Depends(check_homeowner_role)
):
    try:
        logger.debug("=== DEBUG: Starting create_maintenance_request ===")

        # Get raw request body first
        raw_body = await request_data.body()
        logger.debug(f"Raw request body: {raw_body}")

        try:
            json_body = json.loads(raw_body)
            logger.debug(f"Parsed JSON body: {json_body}")
        except Exception as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON")

        authenticated_user_id = payload.get("sub")
        logger.debug(f"Authenticated user ID: {authenticated_user_id}")

        if not authenticated_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID not found in token"
            )

        # Manually validate the required fields
        title = json_body.get("title")
        description = json_body.get("description")
        homeowner_id = json_body.get("homeowner_id")

        logger.debug(f"Title: '{title}' (length: {len(title) if title else 'None'})")
        logger.debug(f"Description: '{description}' (length: {len(description) if description else 'None'})")
        logger.debug(f"Homeowner ID: '{homeowner_id}'")

        # Validate title
        if not title or len(title.strip()) < 3:
            raise HTTPException(status_code=422, detail="Title must be at least 3 characters long")
        if len(title.strip()) > 100:
            raise HTTPException(status_code=422, detail="Title must be at most 100 characters long")

        # Validate description
        if not description or len(description.strip()) < 5:
            raise HTTPException(status_code=422, detail="Description must be at least 5 characters long")
        if len(description.strip()) > 500:
            raise HTTPException(status_code=422, detail="Description must be at most 500 characters long")

        # Validate homeowner_id
        if not homeowner_id:
            raise HTTPException(status_code=422, detail="Homeowner ID is required")

        if authenticated_user_id != homeowner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only create maintenance requests for your own account."
            )

        # Create the document manually
        request_dict = {
            "title": title.strip(),
            "description": description.strip(),
            "homeowner_id": homeowner_id,
            "status": MaintenanceStatus.OPEN,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "image_url": json_body.get("image_url"),
            "bids": []
        }

        logger.debug(f"Final request dict: {request_dict}")

        # Insert into database
        new_request = await db["requests"].insert_one(request_dict)
        logger.debug(f"Inserted request with ID: {new_request.inserted_id}")

        # Get the created request
        created_request = await db["requests"].find_one({"_id": new_request.inserted_id})
        logger.debug(f"Retrieved created request: {created_request}")

        # Serialize the response
        serialized_request = serialize_mongo_doc(created_request.copy())
        logger.debug(f"Returning created request: {serialized_request}")

        return serialized_request

    except HTTPException:
        raise
    except PyMongoError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.exception("Full traceback:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.put("/requests/{request_id}")
async def update_maintenance_request(
        request_id: str,
        update_data: MaintenanceRequestUpdate,
        db=Depends(get_db),
        payload: Dict = Depends(check_homeowner_role)
):
    """
    Updates a maintenance request. Only allows updating title and description.
    Homeowners can edit their requests regardless of status.
    """
    try:
        logger.debug(f"Updating request with ID: {request_id}")
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID not found in token"
            )

        # Validate ObjectId format
        try:
            object_id = ObjectId(request_id)
            logger.debug(f"Converted '{request_id}' to ObjectId: {object_id}")
        except Exception as e:
            logger.error(f"Invalid ObjectId format '{request_id}': {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request ID format"
            )

        # First, check if the request exists and belongs to the user
        logger.debug(f"Searching for request to update: _id={object_id}, homeowner_id={user_id}")
        existing_request = await db["requests"].find_one({
            "_id": object_id,
            "homeowner_id": user_id
        })

        if not existing_request:
            logger.error(f"Request not found for update: _id={object_id}, homeowner_id={user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found or you don't have permission to update it"
            )

        logger.debug(f"Found existing request: {existing_request.get('title')}")

        # Prepare update data (only include fields that are provided and non-None)
        update_fields = {}
        update_dict = update_data.model_dump(exclude_unset=True, exclude_none=True)

        if update_dict.get("title"):
            update_fields["title"] = update_dict["title"]
        if update_dict.get("description"):
            update_fields["description"] = update_dict["description"]
        if update_dict.get("status"):
            update_fields["status"] = update_dict["status"]
        if update_dict.get("image_url") is not None:  # Allow empty string to clear image
            update_fields["image_url"] = update_dict["image_url"]

        if not update_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields provided for update"
            )

        # Add updated timestamp
        update_fields["updated_at"] = datetime.utcnow()

        logger.debug(f"Update fields: {update_fields}")

        # Update the request
        result = await db["requests"].update_one(
            {"_id": object_id, "homeowner_id": user_id},
            {"$set": update_fields}
        )

        logger.debug(f"Update result: matched={result.matched_count}, modified={result.modified_count}")

        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found or no changes made"
            )

        # Get the updated request
        updated_request = await db["requests"].find_one({"_id": object_id})
        return serialize_mongo_doc(updated_request.copy())

    except HTTPException:
        raise
    except PyMongoError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/requests/{request_id}")
async def delete_maintenance_request(
        request_id: str,
        db=Depends(get_db),
        payload: Dict = Depends(check_homeowner_role)
):
    """
    Deletes a maintenance request. Homeowners can delete their requests regardless of status.
    """
    try:
        logger.debug(f"Deleting request with ID: {request_id}")
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID not found in token"
            )

        # Validate ObjectId format
        try:
            object_id = ObjectId(request_id)
            logger.debug(f"Converted '{request_id}' to ObjectId: {object_id}")
        except Exception as e:
            logger.error(f"Invalid ObjectId format '{request_id}': {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request ID format"
            )

        # First, check if the request exists and belongs to the user
        logger.debug(f"Searching for request to delete: _id={object_id}, homeowner_id={user_id}")
        existing_request = await db["requests"].find_one({
            "_id": object_id,
            "homeowner_id": user_id
        })

        if not existing_request:
            logger.error(f"Request not found for deletion: _id={object_id}, homeowner_id={user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found or you don't have permission to delete it"
            )

        logger.debug(f"Found existing request to delete: {existing_request.get('title')}")

        # Delete the request
        result = await db["requests"].delete_one({
            "_id": object_id,
            "homeowner_id": user_id
        })

        logger.debug(f"Delete result: deleted_count={result.deleted_count}")

        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found or already deleted"
            )

        return {"message": "Request deleted successfully", "deleted_id": request_id}

    except HTTPException:
        raise
    except PyMongoError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


# Test endpoint
@router.get("/test-db")
async def test_database_connection(
        db=Depends(get_db),
        payload: Dict = Depends(check_homeowner_role)
):
    """
    Test endpoint to verify database connectivity.
    """
    try:
        logger.debug("Testing database connection...")
        # Test basic operations
        collections = await db.list_collection_names()
        request_count = await db["requests"].count_documents({})
        user_id = payload.get("sub")
        user_requests_count = await db["requests"].count_documents({"homeowner_id": user_id})

        return {
            "database_connected": True,
            "collections": collections,
            "total_requests": request_count,
            "user_requests": user_requests_count,
            "user_id": user_id
        }
    except Exception as e:
        logger.error(f"Database test failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database test failed: {str(e)}"
        )