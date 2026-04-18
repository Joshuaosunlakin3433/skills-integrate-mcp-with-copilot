"""SQLAlchemy data models for the school activities application."""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database import Base

# Association table for users and clubs (many-to-many)
user_club_association = Table(
    'user_club_association',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('club_id', Integer, ForeignKey('clubs.id'), primary_key=True)
)

# Association table for activities and participants (many-to-many)
activity_participant_association = Table(
    'activity_participant_association',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('activity_id', Integer, ForeignKey('activities.id'), primary_key=True),
    Column('signup_date', DateTime, default=datetime.utcnow)
)


class User(Base):
    """User model with roles (Student, Teacher, Admin)."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    password_hash = Column(String, nullable=True)
    role = Column(String, default="student")  # student, teacher, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    clubs = relationship(
        "Club",
        secondary=user_club_association,
        back_populates="members"
    )
    activities = relationship(
        "Activity",
        secondary=activity_participant_association,
        back_populates="participants"
    )
    notifications = relationship("Notification", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class Club(Base):
    """Club model for organizing activities and members."""
    __tablename__ = "clubs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    leader_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    members = relationship(
        "User",
        secondary=user_club_association,
        back_populates="clubs"
    )
    activities = relationship("Activity", back_populates="club")


class Activity(Base):
    """Activity model for events that students can sign up for."""
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    schedule = Column(String, nullable=True)
    max_participants = Column(Integer, default=999)
    club_id = Column(Integer, ForeignKey('clubs.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    club = relationship("Club", back_populates="activities")
    participants = relationship(
        "User",
        secondary=activity_participant_association,
        back_populates="activities"
    )
    attendances = relationship("Attendance", back_populates="activity")


class Attendance(Base):
    """Attendance tracking for activities."""
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    activity_id = Column(Integer, ForeignKey('activities.id'), nullable=False)
    attended = Column(Boolean, default=False)
    date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    activity = relationship("Activity", back_populates="attendances")


class Classroom(Base):
    """Classroom model for reservations."""
    __tablename__ = "classrooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    building = Column(String, nullable=True)
    capacity = Column(Integer, nullable=False)
    has_smartboard = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Reservation(Base):
    """Reservation model for booking classrooms."""
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    classroom_id = Column(Integer, ForeignKey('classrooms.id'), nullable=False)
    activity_id = Column(Integer, ForeignKey('activities.id'), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String, default="pending")  # pending, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow)


class Notification(Base):
    """Notification model for user communications."""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    notification_type = Column(String, nullable=False)  # invitation, reminder, update
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="notifications")


class AuditLog(Base):
    """Audit log model for tracking system actions."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="audit_logs")
