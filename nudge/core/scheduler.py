"""Spaced repetition scheduler based on forgetting curve."""
from datetime import datetime, timedelta
from typing import List

from sqlalchemy.orm import Session

from nudge.core.models import Item, ReviewSchedule

# Forgetting curve intervals in days
INTERVALS: List[int] = [1, 3, 7, 14, 30, 60, 120]


def mark_as_reviewed(session: Session, item_id: int, reviewed_at: datetime | None = None) -> ReviewSchedule:
    """Mark an item as reviewed and advance to next interval.
    
    Args:
        session: Database session
        item_id: ID of the item being reviewed
        reviewed_at: Optional datetime of review (defaults to now)
        
    Returns:
        Updated ReviewSchedule object
        
    Raises:
        ValueError: If item or schedule not found
    """
    if reviewed_at is None:
        reviewed_at = datetime.now()
    
    # Get the review schedule
    schedule = session.query(ReviewSchedule).filter_by(item_id=item_id).first()
    if schedule is None:
        raise ValueError(f"No review schedule found for item {item_id}")
    
    # Advance to next interval (capped at last interval)
    new_interval_index = min(schedule.current_interval_index + 1, len(INTERVALS) - 1)
    next_interval_days = INTERVALS[new_interval_index]
    next_review_date = reviewed_at + timedelta(days=next_interval_days)
    
    # Determine status
    new_status = "mastered" if new_interval_index == len(INTERVALS) - 1 else "learning"
    
    # Update schedule
    schedule.current_interval_index = new_interval_index
    schedule.review_count += 1
    schedule.last_review_date = reviewed_at
    schedule.next_review_date = next_review_date
    schedule.status = new_status
    
    session.commit()
    session.refresh(schedule)
    
    return schedule


def create_review_schedule(session: Session, item: Item) -> ReviewSchedule:
    """Create a new review schedule for an item.
    
    Args:
        session: Database session
        item: Item to create schedule for
        
    Returns:
        New ReviewSchedule object
    """
    # Start with first interval
    next_review_date = datetime.now() + timedelta(days=INTERVALS[0])
    
    schedule = ReviewSchedule(
        item_id=item.id,
        current_interval_index=0,
        review_count=0,
        last_review_date=None,
        next_review_date=next_review_date,
        status="learning"
    )
    
    session.add(schedule)
    session.commit()
    session.refresh(schedule)
    
    return schedule


def get_due_items(session: Session, days_ahead: int = 0) -> List[Item]:
    """Get items due for review.
    
    Args:
        session: Database session
        days_ahead: Number of days ahead to look (0 = due today only)
        
    Returns:
        List of items due for review
    """
    cutoff_date = datetime.now() + timedelta(days=days_ahead)
    
    schedules = (
        session.query(ReviewSchedule)
        .filter(ReviewSchedule.next_review_date <= cutoff_date)
        .order_by(ReviewSchedule.next_review_date)
        .all()
    )
    
    return [schedule.item for schedule in schedules]


def get_upcoming_items(session: Session, days_ahead: int = 7) -> List[Item]:
    """Get items due within the next N days.
    
    Args:
        session: Database session
        days_ahead: Number of days ahead to look
        
    Returns:
        List of items with upcoming reviews
    """
    now = datetime.now()
    cutoff_date = now + timedelta(days=days_ahead)
    
    schedules = (
        session.query(ReviewSchedule)
        .filter(ReviewSchedule.next_review_date >= now)
        .filter(ReviewSchedule.next_review_date <= cutoff_date)
        .order_by(ReviewSchedule.next_review_date)
        .all()
    )
    
    return [schedule.item for schedule in schedules]


def get_interval_name(interval_index: int) -> str:
    """Get human-readable name for interval.
    
    Args:
        interval_index: Index into INTERVALS array
        
    Returns:
        String like "1 day", "3 days", etc.
    """
    if interval_index < 0 or interval_index >= len(INTERVALS):
        return "Unknown"
    
    days = INTERVALS[interval_index]
    return f"{days} day" if days == 1 else f"{days} days"
