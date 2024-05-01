from sqlalchemy import Integer, String, Float, BIGINT, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from src.database.entities.enums import AnnotatedTypes
from src.database.entities.core import Base


class Worker(Base):
    __tablename__ = "workers"
    __table_args__ = (
        CheckConstraint("role IN ('admin', 'packer', 'manager') OR role IS NULL"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(256), nullable=True, unique=True)
    tg_id: Mapped[int] = mapped_column(BIGINT, unique=True)
    name: Mapped[str] = mapped_column(String(256), nullable=True)
    phone: Mapped[str] = mapped_column(String(18), nullable=True)
    role: Mapped[str] = mapped_column(String(256), nullable=True)
    salary: Mapped[int] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(256), nullable=True)


class Good(Base):
    __tablename__ = "goods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sku: Mapped[int] = mapped_column(BIGINT, unique=True)
    name: Mapped[str] = mapped_column(String(256))
    technical_task: Mapped[str] = mapped_column(String(256))
    video_url: Mapped[str] = mapped_column(String(512))


class PackingInfo(Base):
    __tablename__ = "packing_info"

    id: Mapped[AnnotatedTypes.int_pk] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sku: Mapped[int] = mapped_column(Integer, ForeignKey('goods.sku'))
    username: Mapped[str] = mapped_column(String(256), ForeignKey('workers.username'), nullable=True)
    start_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    duration: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    performance: Mapped[float] = mapped_column(Float, nullable=False)