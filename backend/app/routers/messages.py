import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.message import Message
from app.models.user import User
from app.schemas.message import ConversationSummary, MessageResponse, MessageSendRequest

router = APIRouter(prefix="/messages", tags=["messages"])


def _to_response(msg: Message) -> MessageResponse:
    return MessageResponse(
        id=msg.id,
        sender_display_name=msg.sender.display_name,
        recipient_display_name=msg.recipient.display_name,
        content=msg.content,
        read_at=msg.read_at,
        created_at=msg.created_at,
    )


@router.get("/conversations", response_model=list[ConversationSummary])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns a list of unique conversation partners with latest message + unread count."""
    result = await db.execute(
        select(Message)
        .where(or_(Message.sender_id == current_user.id, Message.recipient_id == current_user.id))
        .order_by(Message.created_at.desc())
    )
    all_msgs = result.scalars().all()

    seen: dict[uuid.UUID, ConversationSummary] = {}
    for msg in all_msgs:
        await db.refresh(msg, ["sender", "recipient"])
        other_id = msg.recipient_id if msg.sender_id == current_user.id else msg.sender_id
        other_display = msg.recipient.display_name if msg.sender_id == current_user.id else msg.sender.display_name
        if other_id not in seen:
            seen[other_id] = ConversationSummary(
                other_user_id=other_id,
                other_display_name=other_display,
                last_message=msg.content[:80],
                last_message_at=msg.created_at,
                unread_count=0,
            )
        if msg.recipient_id == current_user.id and msg.read_at is None:
            seen[other_id].unread_count += 1

    return list(seen.values())


@router.get("/{user_id}", response_model=list[MessageResponse])
async def get_conversation(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Message)
        .where(
            or_(
                and_(Message.sender_id == current_user.id, Message.recipient_id == user_id),
                and_(Message.sender_id == user_id, Message.recipient_id == current_user.id),
            )
        )
        .order_by(Message.created_at.asc())
    )
    msgs = result.scalars().all()

    responses = []
    for msg in msgs:
        await db.refresh(msg, ["sender", "recipient"])
        # Mark as read if we're the recipient
        if msg.recipient_id == current_user.id and msg.read_at is None:
            msg.read_at = datetime.now(timezone.utc)
        responses.append(_to_response(msg))

    await db.commit()
    return responses


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    body: MessageSendRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if body.recipient_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot message yourself")

    recipient = await db.get(User, body.recipient_id)
    if not recipient or not recipient.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient not found")

    if len(body.content.strip()) == 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Message cannot be empty")

    msg = Message(
        sender_id=current_user.id,
        recipient_id=body.recipient_id,
        content=body.content.strip(),
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg, ["sender", "recipient"])
    return _to_response(msg)
