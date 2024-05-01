from sqlalchemy import Integer, String, DateTime, Float, BIGINT
from sqlalchemy.orm import Mapped, mapped_column
from src.database.entities.enums import AnnotatedTypes
from src.database.entities.core import Base


class Workers(Base):
    __tablename__ = "workers"

    id: Mapped[AnnotatedTypes.int_pk]
    username: Mapped[str] = mapped_column(String(256), nullable=True)
    tg_id: Mapped[int] = mapped_column(BIGINT)
    phone: Mapped[str] = mapped_column(String(18), nullable=True)


class Goods(Base):
    __tablename__ = "goods"
    sku: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    technical_task: Mapped[str] = mapped_column(String(256))
    video_url: Mapped[str] = mapped_column(String(512))


class PackingInfo(Base):
    __tablename__ = "packing_info"
    id: Mapped[AnnotatedTypes.int_pk] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sku: Mapped[int] = mapped_column(BIGINT)
    username: Mapped[str] = mapped_column(String(256))
    start_time: Mapped[str] = mapped_column(DateTime)
    end_time: Mapped[str] = mapped_column(DateTime)
    duration: Mapped[float] = mapped_column(Float)
    quantity: Mapped[int] = mapped_column(Integer)
    performance: Mapped[float] = mapped_column(Float)

