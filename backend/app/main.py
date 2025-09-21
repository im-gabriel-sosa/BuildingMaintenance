# app/main.py

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

# Import your database connection logic
from app.db.mongodb import connect_to_mongo, close_mongo_connection

# Import your security dependencies and routers
from app.api.deps import check_homeowner_role
from app.api.endpoints import homeowner

# Initialize the FastAPI app
app = FastAPI(
    title="Property Maintenance API",
    version="1.0.0",
    description="API for homeowners and contractors to manage maintenance requests."
)

# --- Middleware ---
# Add CORS middleware to allow cross-origin requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development (lock down in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database Connection Events ---
@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

# --- API Routers ---
# Include the router from homeowner.py. All endpoints from that file will now be active.
app.include_router(homeowner.router)


# --- Test & Root Endpoints ---
@app.get("/", tags=["Root"])
async def read_root():
    """A simple health check endpoint."""
    return {"message": "Welcome to the Property Maintenance API!"}

@app.get("/test-auth", tags=["Test"], dependencies=[Depends(check_homeowner_role)])
async def test_auth():
    """An endpoint to test if the homeowner role check is working."""
    return {"message": "You are a homeowner and have successfully authenticated!"}