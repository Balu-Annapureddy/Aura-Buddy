from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.post import Post
from app.schemas.schemas import PostCreate, PostResponse
from app.utils.auth import get_current_user
from app.services.rate_limiter import RateLimiter

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("/", response_model=PostResponse, status_code=201)
def create_post(
    data: PostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new post. Enforces daily post limit server-side."""
    if not current_user.username:
        raise HTTPException(status_code=400, detail="Set a username before posting")

    # Enforce rate limit
    RateLimiter.check_daily_post_limit(db, current_user)

    post = Post(
        user_id=current_user.id,
        content=data.content,
        image_url=data.image_url,
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    return PostResponse(
        id=post.id,
        user_id=post.user_id,
        content=post.content,
        image_url=post.image_url,
        aura_score=post.aura_score,
        created_at=post.created_at,
        author_username=current_user.username,
    )


@router.get("/feed", response_model=List[PostResponse])
def get_feed(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """Get the global post feed, ordered by newest first."""
    posts = (
        db.query(Post)
        .join(User, Post.user_id == User.id)
        .order_by(Post.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        PostResponse(
            id=p.id,
            user_id=p.user_id,
            content=p.content,
            image_url=p.image_url,
            aura_score=p.aura_score,
            created_at=p.created_at,
            author_username=p.author.username if p.author else None,
        )
        for p in posts
    ]


@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """Get a single post by ID."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return PostResponse(
        id=post.id,
        user_id=post.user_id,
        content=post.content,
        image_url=post.image_url,
        aura_score=post.aura_score,
        created_at=post.created_at,
        author_username=post.author.username if post.author else None,
    )


@router.get("/remaining/count")
def get_remaining_posts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the number of remaining posts for today."""
    remaining = RateLimiter.get_remaining_posts(db, current_user)
    return {"remaining_posts": remaining}
