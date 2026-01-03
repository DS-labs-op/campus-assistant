"""Initial schema migration

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

This migration creates all initial tables for the Campus Assistant.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("platform", sa.String(length=50), nullable=True),
        sa.Column("preferred_language", sa.String(length=10), nullable=True, default="en"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("last_active", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_external_id"), "users", ["external_id"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    # Create sessions table
    op.create_table(
        "sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.String(length=255), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("platform", sa.String(length=50), nullable=True),
        sa.Column("language", sa.String(length=10), nullable=True, default="en"),
        sa.Column("context", sa.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, default=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sessions_id"), "sessions", ["id"], unique=False)
    op.create_index(op.f("ix_sessions_session_id"), "sessions", ["session_id"], unique=True)

    # Create messages table
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=True),
        sa.Column(
            "role",
            sa.Enum("USER", "ASSISTANT", "SYSTEM", name="messagerole"),
            nullable=True,
        ),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("original_content", sa.Text(), nullable=True),
        sa.Column("original_language", sa.String(length=10), nullable=True),
        sa.Column("intent", sa.String(length=100), nullable=True),
        sa.Column("confidence", sa.Integer(), nullable=True),
        sa.Column("sources", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_messages_id"), "messages", ["id"], unique=False)
    op.create_index(op.f("ix_messages_session_id"), "messages", ["session_id"], unique=False)

    # Create FAQs table
    op.create_table(
        "faqs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("question", sa.Text(), nullable=True),
        sa.Column("answer", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("language", sa.String(length=10), nullable=True, default="en"),
        sa.Column("keywords", sa.JSON(), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=True, default=0),
        sa.Column("is_active", sa.Boolean(), nullable=True, default=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_by", sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_faqs_id"), "faqs", ["id"], unique=False)

    # Create documents table
    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=True),
        sa.Column("original_filename", sa.String(length=255), nullable=True),
        sa.Column("file_type", sa.String(length=50), nullable=True),
        sa.Column("file_path", sa.String(length=500), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_indexed", sa.Boolean(), nullable=True, default=False),
        sa.Column("chunk_count", sa.Integer(), nullable=True, default=0),
        sa.Column("uploaded_at", sa.DateTime(), nullable=True),
        sa.Column("uploaded_by", sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_documents_id"), "documents", ["id"], unique=False)

    # Create escalations table
    op.create_table(
        "escalations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("PENDING", "ASSIGNED", "RESOLVED", "CLOSED", name="escalationstatus"),
            nullable=True,
        ),
        sa.Column("assigned_to", sa.String(length=100), nullable=True),
        sa.Column("resolution_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_escalations_id"), "escalations", ["id"], unique=False)

    # Create conversation_logs table
    op.create_table(
        "conversation_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.DateTime(), nullable=True),
        sa.Column("total_conversations", sa.Integer(), nullable=True, default=0),
        sa.Column("total_messages", sa.Integer(), nullable=True, default=0),
        sa.Column("languages_used", sa.JSON(), nullable=True),
        sa.Column("intents_detected", sa.JSON(), nullable=True),
        sa.Column("escalation_count", sa.Integer(), nullable=True, default=0),
        sa.Column("avg_confidence", sa.Integer(), nullable=True, default=0),
        sa.Column("top_queries", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_conversation_logs_id"), "conversation_logs", ["id"], unique=False)
    op.create_index(op.f("ix_conversation_logs_date"), "conversation_logs", ["date"], unique=False)

    # Create feedback table
    op.create_table(
        "feedback",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("message_id", sa.Integer(), nullable=True),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["message_id"], ["messages.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_feedback_id"), "feedback", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_feedback_id"), table_name="feedback")
    op.drop_table("feedback")
    op.drop_index(op.f("ix_conversation_logs_date"), table_name="conversation_logs")
    op.drop_index(op.f("ix_conversation_logs_id"), table_name="conversation_logs")
    op.drop_table("conversation_logs")
    op.drop_index(op.f("ix_escalations_id"), table_name="escalations")
    op.drop_table("escalations")
    op.drop_index(op.f("ix_documents_id"), table_name="documents")
    op.drop_table("documents")
    op.drop_index(op.f("ix_faqs_id"), table_name="faqs")
    op.drop_table("faqs")
    op.drop_index(op.f("ix_messages_session_id"), table_name="messages")
    op.drop_index(op.f("ix_messages_id"), table_name="messages")
    op.drop_table("messages")
    op.drop_index(op.f("ix_sessions_session_id"), table_name="sessions")
    op.drop_index(op.f("ix_sessions_id"), table_name="sessions")
    op.drop_table("sessions")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_external_id"), table_name="users")
    op.drop_table("users")

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS messagerole")
    op.execute("DROP TYPE IF EXISTS escalationstatus")
