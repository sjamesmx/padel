from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

@router.get("/")
async def get_social_wall(page: int = Query(1), limit: int = Query(10)):
    raise HTTPException(status_code=501, detail="Not Implemented")

@router.post("/")
async def post_social_wall():
    raise HTTPException(status_code=501, detail="Not Implemented")

@router.get("/{user_id}")
async def get_user_posts(user_id: str):
    raise HTTPException(status_code=501, detail="Not Implemented")

@router.post("/{post_id}/like")
async def like_post(post_id: str):
    raise HTTPException(status_code=501, detail="Not Implemented")

@router.post("/{post_id}/comment")
async def comment_post(post_id: str):
    raise HTTPException(status_code=501, detail="Not Implemented")

@router.get("/{post_id}/comments")
async def get_comments(post_id: str):
    raise HTTPException(status_code=501, detail="Not Implemented") 