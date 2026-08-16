from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import settings
from app.core.database import Base


class SessaoRefresh(Base):
    __tablename__ = "tb_sessao_refresh"
    __table_args__ = {"schema": settings.db_schema}

    co_seq_sessao: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    co_usuario: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(f"{settings.db_schema}.tb_usuario.co_seq_usuario"),
        nullable=False,
    )
    ds_token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    dt_expiracao: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    dt_revogacao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    dt_registro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    co_sessao_substituta: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(f"{settings.db_schema}.tb_sessao_refresh.co_seq_sessao"),
    )
    ds_ip: Mapped[str | None] = mapped_column(String(45))
    ds_user_agent: Mapped[str | None] = mapped_column(String(500))