from datetime import datetime

from pydantic import BaseModel


class CrawlJobResponse(BaseModel):
    # permite ler direto do model SQLAlchemy sem converter pra dict
    model_config = {"from_attributes": True}

    id: str
    job_type: str
    status: str
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    has_screenshot: bool = False
