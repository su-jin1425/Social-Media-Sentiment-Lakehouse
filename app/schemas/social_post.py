import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SocialPostCreate(BaseModel):
    """Schema for creating a new social post record."""
    platform: str = Field(..., max_length=50)
    author_name: str = Field(..., max_length=255)
    content: str = Field(..., min_length=1)
    source_id: Optional[str] = None


class SocialPostResponse(BaseModel):
    """Schema for social post data returned to clients."""
    id: uuid.UUID
    platform: str
    author_name: str
    content: str
    source_id: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SocialPostListResponse(BaseModel):
    """Paginated list of social posts."""
    items: list[SocialPostResponse]
    total: int
    page: int
    page_size: int
