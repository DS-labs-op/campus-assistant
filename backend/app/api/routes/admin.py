"""
Admin API Routes.
Dashboard, analytics, and administration endpoints.

SECURITY: Uses bcrypt for password verification.
Admin password hash must be set via ADMIN_PASSWORD_HASH environment variable.
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password
from app.models.database import (
    ConversationLog,
    Document,
    Escalation,
    EscalationStatus,
    FAQ,
    Feedback,
    Message,
    Session,
)
from app.models.schemas import (
    AnalyticsSummary,
    EscalationCreate,
    EscalationResponse,
    EscalationUpdate,
)
from app.services.session_manager import get_session_manager
from app.services.vector_store import get_vector_store

router = APIRouter(prefix="/admin", tags=["Admin"])
security = HTTPBasic()
settings = get_settings()

# Default password hash for development (password: "dev-password-change-me")
# In production, set ADMIN_PASSWORD_HASH environment variable
DEV_PASSWORD_HASH = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYn/WNnBOAHy"


def verify_admin(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """
    Verify admin credentials using secure password comparison.

    Uses bcrypt for password verification to prevent timing attacks
    and ensure secure password storage.

    Returns:
        Admin username if authentication successful

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Use timing-safe comparison for username
    correct_username = secrets.compare_digest(
        credentials.username.encode("utf-8"),
        settings.admin_username.encode("utf-8")
    )

    # Get password hash - use env var or development default
    password_hash = settings.admin_password_hash
    if not password_hash:
        if settings.is_production:
            logger.error("ADMIN_PASSWORD_HASH not set in production environment")
            raise HTTPException(
                status_code=500,
                detail="Server configuration error",
            )
        # Use development default (password: "dev-password-change-me")
        password_hash = DEV_PASSWORD_HASH
        logger.warning("Using development default password. Set ADMIN_PASSWORD_HASH in production.")

    # Verify password using bcrypt (timing-attack resistant)
    correct_password = verify_password(credentials.password, password_hash)

    if not (correct_username and correct_password):
        logger.warning(f"Failed admin login attempt for user: {credentials.username}")
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    logger.info(f"Admin login successful: {credentials.username}")
    return credentials.username


# ==================== Dashboard ====================


@router.get("/dashboard")
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    admin: str = Depends(verify_admin),
):
    """
    Get dashboard summary with key metrics.
    """
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)

    # Total sessions
    total_sessions = await db.scalar(select(func.count(Session.id)))

    # Active sessions (last 24 hours)
    active_sessions = await db.scalar(
        select(func.count(Session.id)).where(
            Session.updated_at >= now - timedelta(hours=24)
        )
    )

    # Total messages
    total_messages = await db.scalar(select(func.count(Message.id)))

    # Today's messages
    today_messages = await db.scalar(
        select(func.count(Message.id)).where(Message.created_at >= today_start)
    )

    # Pending escalations
    pending_escalations = await db.scalar(
        select(func.count(Escalation.id)).where(
            Escalation.status == EscalationStatus.PENDING
        )
    )

    # FAQ count
    faq_count = await db.scalar(select(func.count(FAQ.id)).where(FAQ.is_active == True))

    # Document count
    doc_count = await db.scalar(select(func.count(Document.id)))

    # Vector store stats
    vector_store = get_vector_store()
    vector_stats = await vector_store.get_stats()

    # Average confidence (last 7 days)
    avg_confidence = await db.scalar(
        select(func.avg(Message.confidence)).where(
            Message.created_at >= week_ago, Message.confidence.isnot(None)
        )
    )

    return {
        "sessions": {
            "total": total_sessions,
            "active_24h": active_sessions,
        },
        "messages": {
            "total": total_messages,
            "today": today_messages,
        },
        "escalations": {
            "pending": pending_escalations,
        },
        "knowledge_base": {
            "faqs": faq_count,
            "documents": doc_count,
            "vector_chunks": vector_stats.get("total_documents", 0),
        },
        "performance": {
            "avg_confidence_7d": round(avg_confidence or 0, 1),
        },
    }


# ==================== Analytics ====================


@router.get("/analytics")
async def get_analytics(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    admin: str = Depends(verify_admin),
):
    """
    Get detailed analytics for the specified period.
    """
    now = datetime.utcnow()
    start_date = now - timedelta(days=days)

    # Messages by language
    result = await db.execute(
        select(Message.original_language, func.count(Message.id))
        .where(Message.created_at >= start_date, Message.original_language.isnot(None))
        .group_by(Message.original_language)
    )
    languages = {row[0]: row[1] for row in result.fetchall()}

    # Messages by intent
    result = await db.execute(
        select(Message.intent, func.count(Message.id))
        .where(Message.created_at >= start_date, Message.intent.isnot(None))
        .group_by(Message.intent)
        .order_by(func.count(Message.id).desc())
        .limit(10)
    )
    intents = {row[0]: row[1] for row in result.fetchall()}

    # Daily message counts
    daily_counts = []
    for i in range(days):
        day = start_date + timedelta(days=i)
        day_end = day + timedelta(days=1)

        count = await db.scalar(
            select(func.count(Message.id)).where(
                Message.created_at >= day, Message.created_at < day_end
            )
        )
        daily_counts.append({"date": day.strftime("%Y-%m-%d"), "count": count})

    # Sessions by platform
    result = await db.execute(
        select(Session.platform, func.count(Session.id))
        .where(Session.created_at >= start_date)
        .group_by(Session.platform)
    )
    platforms = {row[0]: row[1] for row in result.fetchall()}

    return {
        "period_days": days,
        "languages_used": languages,
        "top_intents": intents,
        "daily_messages": daily_counts,
        "platforms": platforms,
    }


# ==================== Conversation Logs ====================


@router.get("/conversations")
async def list_conversations(
    date: Optional[str] = None,
    platform: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    admin: str = Depends(verify_admin),
):
    """
    List conversation sessions with messages.
    """
    query = select(Session).order_by(Session.updated_at.desc())

    if platform:
        query = query.where(Session.platform == platform)

    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d")
            query = query.where(
                Session.created_at >= target_date,
                Session.created_at < target_date + timedelta(days=1),
            )
        except ValueError:
            pass

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    sessions = result.scalars().all()

    conversations = []
    for session in sessions:
        # Get messages for this session
        msg_result = await db.execute(
            select(Message)
            .where(Message.session_id == session.id)
            .order_by(Message.created_at)
        )
        messages = msg_result.scalars().all()

        conversations.append(
            {
                "session_id": session.session_id,
                "platform": session.platform,
                "language": session.language,
                "is_active": session.is_active,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "message_count": len(messages),
                "messages": [
                    {
                        "role": msg.role.value,
                        "content": msg.content,
                        "original_content": msg.original_content,
                        "intent": msg.intent,
                        "confidence": msg.confidence,
                        "created_at": msg.created_at.isoformat(),
                    }
                    for msg in messages
                ],
            }
        )

    return {"conversations": conversations, "total": len(conversations)}


@router.get("/conversations/export")
async def export_conversations(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    format: str = Query("json", description="Export format: json or csv"),
    db: AsyncSession = Depends(get_db),
    admin: str = Depends(verify_admin),
):
    """
    Export conversations for a specific date.
    """
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    # Get all sessions for the date
    result = await db.execute(
        select(Session).where(
            Session.created_at >= target_date,
            Session.created_at < target_date + timedelta(days=1),
        )
    )
    sessions = result.scalars().all()

    export_data = []
    for session in sessions:
        msg_result = await db.execute(
            select(Message)
            .where(Message.session_id == session.id)
            .order_by(Message.created_at)
        )
        messages = msg_result.scalars().all()

        for msg in messages:
            export_data.append(
                {
                    "session_id": session.session_id,
                    "platform": session.platform,
                    "language": session.language,
                    "role": msg.role.value,
                    "content": msg.content,
                    "original_language": msg.original_language,
                    "intent": msg.intent,
                    "confidence": msg.confidence,
                    "timestamp": msg.created_at.isoformat(),
                }
            )

    return {
        "date": date,
        "total_messages": len(export_data),
        "data": export_data,
    }


# ==================== Escalations ====================


@router.get("/escalations")
async def list_escalations(
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    admin: str = Depends(verify_admin),
):
    """
    List escalation requests.
    """
    query = select(Escalation).order_by(Escalation.created_at.desc())

    if status:
        try:
            status_enum = EscalationStatus(status)
            query = query.where(Escalation.status == status_enum)
        except ValueError:
            pass

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    escalations = result.scalars().all()

    return [
        {
            "id": esc.id,
            "session_id": esc.session_id,
            "reason": esc.reason,
            "status": esc.status.value,
            "assigned_to": esc.assigned_to,
            "resolution_notes": esc.resolution_notes,
            "created_at": esc.created_at.isoformat(),
            "resolved_at": esc.resolved_at.isoformat() if esc.resolved_at else None,
        }
        for esc in escalations
    ]


@router.put("/escalations/{escalation_id}")
async def update_escalation(
    escalation_id: int,
    update_data: EscalationUpdate,
    db: AsyncSession = Depends(get_db),
    admin: str = Depends(verify_admin),
):
    """
    Update escalation status.
    """
    result = await db.execute(
        select(Escalation).where(Escalation.id == escalation_id)
    )
    escalation = result.scalar_one_or_none()

    if not escalation:
        raise HTTPException(status_code=404, detail="Escalation not found")

    try:
        escalation.status = EscalationStatus(update_data.status)
        if update_data.assigned_to:
            escalation.assigned_to = update_data.assigned_to
        if update_data.resolution_notes:
            escalation.resolution_notes = update_data.resolution_notes

        if update_data.status in ["resolved", "closed"]:
            escalation.resolved_at = datetime.utcnow()

        await db.commit()
        return {"message": "Escalation updated successfully"}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Feedback ====================


@router.get("/feedback")
async def list_feedback(
    min_rating: Optional[int] = None,
    max_rating: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    admin: str = Depends(verify_admin),
):
    """
    List user feedback.
    """
    query = select(Feedback).order_by(Feedback.created_at.desc())

    if min_rating:
        query = query.where(Feedback.rating >= min_rating)
    if max_rating:
        query = query.where(Feedback.rating <= max_rating)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    feedback_list = result.scalars().all()

    return [
        {
            "id": fb.id,
            "message_id": fb.message_id,
            "rating": fb.rating,
            "comment": fb.comment,
            "created_at": fb.created_at.isoformat(),
        }
        for fb in feedback_list
    ]


# ==================== System ====================


@router.post("/cleanup")
async def cleanup_expired_sessions(
    db: AsyncSession = Depends(get_db),
    admin: str = Depends(verify_admin),
):
    """
    Clean up expired sessions.
    """
    session_manager = get_session_manager()
    count = await session_manager.cleanup_expired_sessions(db)

    return {"cleaned_sessions": count}


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    System health check (no auth required).
    """
    # Check database
    try:
        await db.execute(select(1))
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"

    # Check vector store
    try:
        vector_store = get_vector_store()
        await vector_store.get_stats()
        vector_status = "healthy"
    except Exception:
        vector_status = "unhealthy"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "version": settings.app_version,
        "database": db_status,
        "vector_db": vector_status,
        "llm_provider": settings.llm_provider,
    }
