from sqlalchemy import Integer, String, Float, BIGINT, ForeignKey, DateTime, CheckConstraint, Date
from sqlalchemy.orm import Mapped, mapped_column
from src.database.entities.enums import AnnotatedTypes
from src.database.entities.core import Base

from datetime import datetime


class Worker(Base):
    __tablename__ = "workers"
    __table_args__ = (
        CheckConstraint("role IN ('admin', 'packer', 'manager', 'loader', 'pending') OR role IS NULL"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(64), nullable=True)
    second_name: Mapped[str] = mapped_column(String(64), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(64), nullable=True, unique=True)
    payment_details: Mapped[str] = mapped_column(String(64), nullable=True, unique=True)
    bank_name: Mapped[str] = mapped_column(String(64), nullable=True)
    date_of_birth: Mapped[datetime.date] = mapped_column(Date, nullable=True)  # Добавлено это поле
    role: Mapped[str] = mapped_column(String(256), nullable=True)
    tg_id: Mapped[int] = mapped_column(BIGINT, unique=True)
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
    type: Mapped[str] = mapped_column(String(256), nullable=True)
    sku: Mapped[int] = mapped_column(BIGINT, ForeignKey('goods.sku'), nullable=True)
    worker_id: Mapped[int] = mapped_column(Integer, ForeignKey('workers.id'))
    start_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    duration: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=True)
    performance: Mapped[float] = mapped_column(Float, nullable=True)
    defect: Mapped[int] = mapped_column(Integer, nullable=True)
    photo_url: Mapped[str] = mapped_column(String(255), nullable=True)


class ProductBalance(Base):
    __tablename__ = "product_balance"

    id: Mapped[AnnotatedTypes.int_pk] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sku: Mapped[int] = mapped_column(BIGINT, ForeignKey('goods.sku'), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=True)
    defect: Mapped[int] = mapped_column(Integer, nullable=True)
