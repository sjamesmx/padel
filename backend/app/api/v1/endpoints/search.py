from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.post("/players")
async def search_players():
    raise HTTPException(status_code=501, detail="Not Implemented")

@router.get("/nearby")
async def get_nearby_players():
    raise HTTPException(status_code=501, detail="Not Implemented") 