from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.community import Community, CommunityMembership
from app.models.post import Post, PostVote
from app.models.user import User
from app.schemas.post import PostCreateRequest, PostFeedResponse, PostResponse

router = APIRouter(prefix="/posts", tags=["posts"])

MAX_CONTENT_LENGTH = 5000


def _to_response(post: Post, reply_count: int = 0) -> PostResponse:
    return PostResponse(
        id=post.id,
        community_id=post.community_id,
        display_name=post.display_name,        # pseudonym only — author_id never exposed
        content="[deleted]" if post.is_deleted else post.content,
        parent_id=post.parent_id,
        upvotes=post.upvotes,
        is_deleted=post.is_deleted,
        created_at=post.created_at,
        reply_count=reply_count,
    )


@router.get("", response_model=PostFeedResponse)
async def get_feed(
    community: str = Query(..., description="Community slug"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Returns top-level posts (confessions) for a community — replies excluded."""
    comm_result = await db.execute(select(Community).where(Community.slug == community))
    comm = comm_result.scalar_one_or_none()
    if not comm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Community not found")

    offset = (page - 1) * page_size

    total_result = await db.execute(
        select(func.count(Post.id)).where(
            Post.community_id == comm.id,
            Post.parent_id.is_(None),  # top-level only
        )
    )
    total = total_result.scalar() or 0

    posts_result = await db.execute(
        select(Post)
        .where(Post.community_id == comm.id, Post.parent_id.is_(None))
        .order_by(Post.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    posts = list(posts_result.scalars().all())

    post_responses = []
    for post in posts:
        rc_result = await db.execute(
            select(func.count(Post.id)).where(Post.parent_id == post.id)
        )
        reply_count = rc_result.scalar() or 0
        post_responses.append(_to_response(post, reply_count))

    return PostFeedResponse(posts=post_responses, total=total, page=page, page_size=page_size)


@router.get("/{post_id}/replies", response_model=PostFeedResponse)
async def get_replies(
    post_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Returns paginated replies for a specific post."""
    parent = await db.get(Post, post_id)
    if not parent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    offset = (page - 1) * page_size
    total_result = await db.execute(
        select(func.count(Post.id)).where(Post.parent_id == post_id)
    )
    total = total_result.scalar() or 0

    result = await db.execute(
        select(Post)
        .where(Post.parent_id == post_id)
        .order_by(Post.created_at.asc())
        .offset(offset)
        .limit(page_size)
    )
    replies = list(result.scalars().all())
    return PostFeedResponse(
        posts=[_to_response(r) for r in replies],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    body: PostCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not body.content.strip():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Content cannot be empty")
    if len(body.content) > MAX_CONTENT_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Content exceeds {MAX_CONTENT_LENGTH} characters",
        )

    comm_result = await db.execute(select(Community).where(Community.id == body.community_id))
    community = comm_result.scalar_one_or_none()
    if not community:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Community not found")

    # Verify membership
    mem_result = await db.execute(
        select(CommunityMembership).where(
            CommunityMembership.user_id == current_user.id,
            CommunityMembership.community_id == community.id,
        )
    )
    if not mem_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Join this community first")

    if body.parent_id:
        parent_result = await db.execute(select(Post).where(Post.id == body.parent_id))
        if not parent_result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent post not found")

    post = Post(
        community_id=body.community_id,
        author_id=current_user.id,
        display_name=current_user.display_name,  # snapshot pseudonym at post time
        content=body.content.strip(),
        parent_id=body.parent_id,
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return _to_response(post)


@router.post("/{post_id}/vote", status_code=status.HTTP_204_NO_CONTENT)
async def vote_post(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    vote_result = await db.execute(
        select(PostVote).where(PostVote.post_id == post_id, PostVote.user_id == current_user.id)
    )
    existing_vote = vote_result.scalar_one_or_none()

    if existing_vote:
        await db.delete(existing_vote)
        post.upvotes = max(0, post.upvotes - 1)
    else:
        db.add(PostVote(post_id=post.id, user_id=current_user.id))
        post.upvotes += 1
    await db.commit()


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if str(post.author_id) != str(current_user.id) and current_user.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    post.is_deleted = True
    await db.commit()
