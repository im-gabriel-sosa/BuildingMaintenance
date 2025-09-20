from fastapi import FastAPI, Depends
from app.api.deps import check_homeowner_role

app = FastAPI()

@app.get("/test-auth", dependencies=[Depends(check_homeowner_role)])
async def test_auth():
    return {"message": "You are a homeowner and have successfully authenticated!"}
