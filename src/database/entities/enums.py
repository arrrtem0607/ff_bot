from enum import EnumType
from typing import Annotated

from sqlalchemy import text, Enum
from sqlalchemy.orm import mapped_column
from datetime import datetime


class AnnotatedTypes(EnumType):
    int_pk = Annotated[int, mapped_column(primary_key=True)]
    created_at = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
    updated_at = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"),
                                                   onupdate=datetime.utcnow
                                                   )]


class RoleEnum(Enum):
    admin = "admin"
    packer = "packer"
    manager = "manager"
    loader = "loader"


class ProcessEnum(Enum):
    packing = "packing"
    loading = "loading"
    reception = "reception"
