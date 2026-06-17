from sqlalchemy.orm import DeclarativeBase , Mapped, mapped_column
from sqlalchemy import DateTime, text
from datetime import datetime

class Base(DeclarativeBase):
    """It's an abstract base class to tell sqlalchemy that these classes are database tables"""
    created_at : Mapped[datetime] = mapped_column(
                                        DateTime,
                                        server_default=text("now()"),
                                        nullable=False,
                                        index=True
    )
    updated_at : Mapped[datetime] = mapped_column(
                                        DateTime,
                                        server_default=text("now()"),
                                        onupdate=text("now()"),
                                        nullable=False
    )
    def __repr__(self):
        fields = getattr(self, "__repr_fields__", ["id"])
        values = ", ".join(
            f"{field}={getattr(self, field, None)!r}" for field in fields
        )
        return f"<{self.__class__.__name__}({values})>"