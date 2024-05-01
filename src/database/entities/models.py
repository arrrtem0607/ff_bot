from sqlalchemy import Integer, String, DateTime, Float, BIGINT, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from src.database.entities.enums import AnnotatedTypes
from src.database.entities.core import Base


class Workers(Base):
    __tablename__ = "workers"

<<<<<<< HEAD
    id: Mapped[AnnotatedTypes.int_pk]
    username: Mapped[str] = mapped_column(String(256), nullable=True)
=======
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(256))
>>>>>>> 3bedc28922d5d1b7eaf2b08454db0b11c308b0e3
    tg_id: Mapped[int] = mapped_column(BIGINT)
    phone: Mapped[str] = mapped_column(String(18), nullable=True)


class Goods(Base):
    __tablename__ = "goods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sku: Mapped[int] = mapped_column(BIGINT)
    name: Mapped[str] = mapped_column(String(256))
    technical_task: Mapped[str] = mapped_column(String(256))
    video_url: Mapped[str] = mapped_column(String(512))


class PackingInfo(Base):
    __tablename__ = "packing_info"

    id: Mapped[AnnotatedTypes.int_pk] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sku: Mapped[int] = mapped_column(ForeignKey('goods.id'))
    username: Mapped[str] = mapped_column(ForeignKey('workers.id'))
    start_time: Mapped[str] = mapped_column(DateTime)
    end_time: Mapped[str] = mapped_column(DateTime)
    duration: Mapped[float] = mapped_column(Float)
    quantity: Mapped[int] = mapped_column(Integer)
    performance: Mapped[float] = mapped_column(Float)

