"""Database models for the Nudge application."""
from datetime import datetime
from typing import List

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


# Association table for many-to-many relationship between items and tags
item_tags = Table(
    "item_tags",
    Base.metadata,
    Column("item_id", Integer, ForeignKey("items.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Item(Base):
    """Study item to be reviewed."""
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    date_added: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    
    # Relationships
    tags: Mapped[List["Tag"]] = relationship(
        "Tag", secondary=item_tags, back_populates="items", lazy="selectin"
    )
    review_schedule: Mapped["ReviewSchedule"] = relationship(
        "ReviewSchedule", back_populates="item", cascade="all, delete-orphan", uselist=False, lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Item(id={self.id}, name='{self.name}')>"


class Tag(Base):
    """Tag for categorizing study items."""
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    color: Mapped[str] = mapped_column(String, nullable=False)  # Hex color code like "#FF6B6B"
    
    # Relationships
    items: Mapped[List["Item"]] = relationship(
        "Item", secondary=item_tags, back_populates="tags", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name='{self.name}', color='{self.color}')>"


class ReviewSchedule(Base):
    """Spaced repetition schedule for an item."""
    __tablename__ = "review_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Interval tracking
    current_interval_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    review_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Date tracking
    last_review_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    next_review_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    
    # Status: 'learning', 'mastered'
    status: Mapped[str] = mapped_column(String, default="learning", nullable=False)
    
    # Relationships
    item: Mapped["Item"] = relationship("Item", back_populates="review_schedule")

    def __repr__(self) -> str:
        return f"<ReviewSchedule(item_id={self.item_id}, interval_index={self.current_interval_index}, status='{self.status}')>"
