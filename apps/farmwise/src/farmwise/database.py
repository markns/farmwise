from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine


class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    role: str
    content: str
    agent: str | None
    # user_name: str | None  # Todo: normalize to users table
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    trace_id: str | None


engine = create_engine("sqlite:///farmwise.db")
SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
