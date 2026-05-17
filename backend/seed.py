"""
Seed script — creates initial communities and an admin user.

Usage:
    DATABASE_URL=postgresql+asyncpg://... SECRET_KEY=... python seed.py
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.community import Community
from app.models.user import User
from app.utils.security import hash_password
from app.utils.pseudonym import generate_pseudonym
import uuid

COMMUNITIES = [
    {"name": "Alcohol Support", "slug": "alcohol", "addiction_type": "ALCOHOL",
     "description": "A safe, anonymous space for those dealing with alcohol dependency. Share, listen, and heal."},
    {"name": "Substance Recovery", "slug": "drugs", "addiction_type": "DRUGS",
     "description": "Community support for people navigating substance addiction. No judgment, only support."},
    {"name": "Gambling Anonymous", "slug": "gambling", "addiction_type": "GAMBLING",
     "description": "For those struggling with gambling addiction. Share experiences and strategies for recovery."},
    {"name": "Gaming Balance", "slug": "gaming", "addiction_type": "GAMING",
     "description": "Discussing compulsive gaming and finding healthier relationships with technology."},
    {"name": "Food & Body", "slug": "food", "addiction_type": "FOOD",
     "description": "A supportive space for eating disorders and compulsive eating behaviours."},
    {"name": "Smoke-Free Journey", "slug": "smoking", "addiction_type": "SMOKING",
     "description": "Support for quitting smoking and nicotine dependency."},
    {"name": "Other Addictions", "slug": "other", "addiction_type": "OTHER",
     "description": "A space for any addiction not covered by a specific community."},
    # Tier-gated professional communities
    {"name": "Professional Support — S Tier", "slug": "pro-s", "addiction_type": "OTHER",
     "description": "Exclusive group with assigned S-tier psychiatrists. Requires active S-tier subscription.",
     "required_tier": "S"},
    {"name": "Professional Support — A Tier", "slug": "pro-a", "addiction_type": "OTHER",
     "description": "Group with assigned A-tier psychologists. Requires active A-tier subscription.",
     "required_tier": "A"},
    {"name": "Professional Support — B Tier", "slug": "pro-b", "addiction_type": "OTHER",
     "description": "Group with assigned B-tier counselors. Requires active B-tier subscription.",
     "required_tier": "B"},
]

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@vss.app")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin1234!")


async def seed():
    async with AsyncSessionLocal() as db:
        # --- seed communities ---
        created_count = 0
        for c in COMMUNITIES:
            existing = await db.execute(select(Community).where(Community.slug == c["slug"]))
            if existing.scalar_one_or_none():
                print(f"  skip community '{c['slug']}' (already exists)")
                continue
            community = Community(**c)
            db.add(community)
            created_count += 1
            print(f"  + community '{c['slug']}'")

        await db.commit()
        print(f"Communities: {created_count} created\n")

        # --- seed admin user ---
        existing_admin = await db.execute(select(User).where(User.email == ADMIN_EMAIL))
        if existing_admin.scalar_one_or_none():
            print(f"  skip admin '{ADMIN_EMAIL}' (already exists)")
        else:
            admin_id = uuid.uuid4()
            admin = User(
                id=admin_id,
                email=ADMIN_EMAIL,
                password_hash=hash_password(ADMIN_PASSWORD),
                real_name="Platform Admin",
                display_name=generate_pseudonym(str(admin_id)),
                addiction_types=[],
                role="ADMIN",
                is_verified=True,
            )
            db.add(admin)
            await db.commit()
            print(f"  + admin user '{ADMIN_EMAIL}' (password: {ADMIN_PASSWORD})")
            print("  IMPORTANT: change the admin password immediately in production!")

    print("\nSeed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
