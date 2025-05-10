from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class FriendRequest(BaseModel):
    friend_id: str

@router.post("/request")
async def send_friend_request(request: FriendRequest):
    raise HTTPException(status_code=501, detail="Not Implemented")

@router.post("/accept")
async def accept_friend_request():
    raise HTTPException(status_code=501, detail="Not Implemented")

@router.get("/{user_id}")
async def list_friends(user_id: str):
    raise HTTPException(status_code=501, detail="Not Implemented")

@router.delete("/{friendship_id}")
async def delete_friend(friendship_id: str):
    raise HTTPException(status_code=501, detail="Not Implemented") 