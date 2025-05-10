from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class MatchRequest(BaseModel):
    level: str = None
    position: str = None

@router.post("/find_match")
async def find_match(request: MatchRequest):
    raise HTTPException(status_code=501, detail="Not Implemented")

@router.get("/get_matches")
async def get_matches():
    raise HTTPException(status_code=501, detail="Not Implemented")

@router.get("/matches")
async def get_matches_list():
    raise HTTPException(status_code=501, detail="Not Implemented")

@router.post("/create_match")
async def create_match():
    raise HTTPException(status_code=501, detail="Not Implemented") 