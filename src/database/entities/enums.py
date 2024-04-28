from enum import EnumType
from typing import Annotated

from sqlalchemy import text
from sqlalchemy.orm import mapped_column
from datetime import datetime


class AnnotatedTypes(EnumType):
    int_pk = Annotated[int, mapped_column(primary_key=True)]
    created_at = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
    updated_at = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"),
                                                   onupdate=datetime.utcnow
                                                   )]
