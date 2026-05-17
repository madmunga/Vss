"""Initial migration — creates all VSS tables."""

import uuid
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- enums ---
    op.execute("CREATE TYPE user_role AS ENUM ('USER', 'PROFESSIONAL', 'ADMIN')")
    op.execute("CREATE TYPE professional_specialty AS ENUM ('PSYCHIATRIST','PSYCHOLOGIST','COUNSELOR','THERAPIST','ADVISOR')")
    op.execute("CREATE TYPE professional_tier AS ENUM ('S','A','B')")
    op.execute("CREATE TYPE assignment_tier AS ENUM ('S','A','B')")
    op.execute("CREATE TYPE vetting_status AS ENUM ('PENDING','APPROVED','REJECTED')")
    op.execute("CREATE TYPE addiction_type AS ENUM ('ALCOHOL','DRUGS','GAMBLING','GAMING','SEX','FOOD','SMOKING','OTHER')")
    op.execute("CREATE TYPE community_tier AS ENUM ('S','A','B')")
    op.execute("CREATE TYPE subscription_tier AS ENUM ('S','A','B')")
    op.execute("CREATE TYPE subscription_status AS ENUM ('ACTIVE','CANCELLED','PAST_DUE','TRIALING')")

    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String, nullable=False),
        sa.Column("real_name", sa.String(255)),
        sa.Column("phone", sa.String(50)),
        sa.Column("display_name", sa.String(100), nullable=False, unique=True),
        sa.Column("addiction_types", JSONB, nullable=False, server_default="[]"),
        sa.Column("role", sa.Enum("USER", "PROFESSIONAL", "ADMIN", name="user_role", create_type=False), nullable=False, server_default="USER"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("is_verified", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("refresh_token_hash", sa.String),
        sa.Column("verification_token", sa.String),
        sa.Column("reset_token", sa.String),
        sa.Column("reset_token_expires", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_display_name", "users", ["display_name"])

    # --- communities ---
    op.create_table(
        "communities",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("addiction_type", sa.Enum("ALCOHOL","DRUGS","GAMBLING","GAMING","SEX","FOOD","SMOKING","OTHER", name="addiction_type", create_type=False), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("required_tier", sa.Enum("S","A","B", name="community_tier", create_type=False), nullable=True),
        sa.Column("member_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_communities_slug", "communities", ["slug"])

    # --- community_memberships ---
    op.create_table(
        "community_memberships",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("community_id", UUID(as_uuid=True), sa.ForeignKey("communities.id"), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("user_id", "community_id", name="uq_membership"),
    )

    # --- professionals ---
    op.create_table(
        "professionals",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column("license_number", sa.String(100), nullable=False, unique=True),
        sa.Column("specialty", sa.Enum("PSYCHIATRIST","PSYCHOLOGIST","COUNSELOR","THERAPIST","ADVISOR", name="professional_specialty", create_type=False), nullable=False),
        sa.Column("tier", sa.Enum("S","A","B", name="professional_tier", create_type=False), nullable=False),
        sa.Column("vetting_status", sa.Enum("PENDING","APPROVED","REJECTED", name="vetting_status", create_type=False), nullable=False, server_default="PENDING"),
        sa.Column("vetting_facility", sa.String(255)),
        sa.Column("bio", sa.Text),
        sa.Column("years_experience", sa.Integer),
        sa.Column("languages", JSONB, nullable=False, server_default='["en"]'),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # --- professional_assignments ---
    op.create_table(
        "professional_assignments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("professional_id", UUID(as_uuid=True), sa.ForeignKey("professionals.id"), nullable=False),
        sa.Column("community_id", UUID(as_uuid=True), sa.ForeignKey("communities.id"), nullable=False),
        sa.Column("tier", sa.Enum("S","A","B", name="assignment_tier", create_type=False), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # --- posts ---
    op.create_table(
        "posts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("community_id", UUID(as_uuid=True), sa.ForeignKey("communities.id"), nullable=False),
        sa.Column("author_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("parent_id", UUID(as_uuid=True), sa.ForeignKey("posts.id"), nullable=True),
        sa.Column("upvotes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_deleted", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_posts_community_id", "posts", ["community_id"])
    op.create_index("ix_posts_parent_id", "posts", ["parent_id"])

    # --- post_votes ---
    op.create_table(
        "post_votes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("post_id", UUID(as_uuid=True), sa.ForeignKey("posts.id"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.UniqueConstraint("post_id", "user_id", name="uq_post_vote"),
    )

    # --- subscriptions ---
    op.create_table(
        "subscriptions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column("tier", sa.Enum("S","A","B", name="subscription_tier", create_type=False), nullable=False),
        sa.Column("stripe_subscription_id", sa.String, unique=True),
        sa.Column("stripe_customer_id", sa.String),
        sa.Column("status", sa.Enum("ACTIVE","CANCELLED","PAST_DUE","TRIALING", name="subscription_status", create_type=False), nullable=False, server_default="TRIALING"),
        sa.Column("price_usd", sa.Integer, nullable=False),
        sa.Column("current_period_start", sa.DateTime(timezone=True)),
        sa.Column("current_period_end", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # --- messages ---
    op.create_table(
        "messages",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("sender_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("recipient_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_messages_recipient", "messages", ["recipient_id"])
    op.create_index("ix_messages_sender", "messages", ["sender_id"])


def downgrade() -> None:
    op.drop_table("messages")
    op.drop_table("subscriptions")
    op.drop_table("post_votes")
    op.drop_table("posts")
    op.drop_table("professional_assignments")
    op.drop_table("professionals")
    op.drop_table("community_memberships")
    op.drop_table("communities")
    op.drop_table("users")
    for enum in ["user_role","professional_specialty","professional_tier","assignment_tier",
                 "vetting_status","addiction_type","community_tier","subscription_tier","subscription_status"]:
        op.execute(f"DROP TYPE IF EXISTS {enum}")
