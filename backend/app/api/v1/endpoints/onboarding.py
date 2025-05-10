from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.post("/")
async def complete_onboarding():
    raise HTTPException(status_code=501, detail="Not Implemented")

@router.get("/status/{user_id}")
async def get_onboarding_status(user_id: str):
    raise HTTPException(status_code=501, detail="Not Implemented") 