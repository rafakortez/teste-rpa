import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base_entity import BaseEntity


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class JobType(str, enum.Enum):
    HOCKEY = "hockey"
    OSCAR = "oscar"


class CrawlJob(BaseEntity):
    __tablename__ = "crawl_jobs"

    # uuid4 gera id unico sem depender de sequencia do banco
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    job_type: Mapped[str] = mapped_column(Enum(JobType), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(JobStatus), nullable=False, default=JobStatus.PENDING
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        # server_default = quem gera o timestamp e o Postgres, nao o Python
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        # onupdate = Postgres atualiza sozinho quando o registro muda
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
