from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.core.database import Base


class Dominio(Base):
    __tablename__ = "tb_dominio"
    __table_args__ = {"schema": settings.db_schema}

    co_seq_dominio: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    co_dominio: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(f"{settings.db_schema}.tb_dominio.co_seq_dominio"),
        nullable=True,
    )
    no_dominio: Mapped[str] = mapped_column(String(100), nullable=False)
    ds_dominio: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ds_observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)


class Usuario(Base):
    __tablename__ = "tb_usuario"
    __table_args__ = {"schema": settings.db_schema}

    co_seq_usuario: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    co_cpf: Mapped[str] = mapped_column(String(11), unique=True, nullable=False)
    no_nome: Mapped[str] = mapped_column(String(200), nullable=False)
    ds_email: Mapped[str] = mapped_column(String(254), nullable=False)
    ds_celular: Mapped[str | None] = mapped_column(String(20), nullable=True)
    ds_senha: Mapped[str] = mapped_column(String(255), nullable=False)
    dt_registro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    dt_ultima_atualizacao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    co_status: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(f"{settings.db_schema}.tb_dominio.co_seq_dominio"),
        nullable=False,
    )
    co_tp_usuario: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(f"{settings.db_schema}.tb_dominio.co_seq_dominio"),
        nullable=False,
    )

    status: Mapped[Dominio] = relationship(foreign_keys=[co_status], lazy="joined")
    tipo_usuario: Mapped[Dominio] = relationship(foreign_keys=[co_tp_usuario], lazy="joined")
