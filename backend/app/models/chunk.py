from pgvector.sqlalchemy import Vector
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.config import get_settings

settings = get_settings()


class Base(DeclarativeBase):
    pass


class Chunk(Base):
    """A single retrievable unit of evidence: one section/clause from one source document."""

    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Identity / citation
    source_file: Mapped[str] = mapped_column(String(255), index=True)
    section_id: Mapped[str] = mapped_column(String(64), index=True)
    citation: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    heading: Mapped[str] = mapped_column(String(512), default="")
    page: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Content
    text: Mapped[str] = mapped_column(Text)

    # Vector embedding
    embedding: Mapped[list[float]] = mapped_column(Vector(settings.embedding_dim))

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Chunk {self.citation}>"
