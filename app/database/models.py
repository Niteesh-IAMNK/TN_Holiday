from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import String, Integer, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base

class PriorityEnum(str, PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RunStatusEnum(str, PyEnum):
    SUCCESS = "success"
    FAILED = "failed"
    RUNNING = "running"

class DeliveryStatusEnum(str, PyEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class District(Base):
    __tablename__ = "districts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    alerts: Mapped[list["Alert"]] = relationship("Alert", back_populates="district")


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_scraped_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    alerts: Mapped[list["Alert"]] = relationship("Alert", back_populates="source")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source_id: Mapped[int] = mapped_column(Integer, ForeignKey("sources.id"), nullable=False)
    district_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("districts.id"), nullable=True) # Null signals state-wide alert
    priority: Mapped[PriorityEnum] = mapped_column(Enum(PriorityEnum), default=PriorityEnum.MEDIUM, nullable=False)
    raw_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    source: Mapped["Source"] = relationship("Source", back_populates="alerts")
    district: Mapped["District"] = relationship("District", back_populates="alerts")
    predictions: Mapped[list["HolidayPrediction"]] = relationship("HolidayPrediction", back_populates="alert")
    messages: Mapped[list["MessageHistory"]] = relationship("MessageHistory", back_populates="alert")


class HolidayPrediction(Base):
    __tablename__ = "holiday_predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    alert_id: Mapped[int] = mapped_column(Integer, ForeignKey("alerts.id"), nullable=False)
    predicted_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Integer)  # Multiplied by 100 for integer safety across backends
    is_holiday: Mapped[bool] = mapped_column(Boolean, default=True)
    ai_reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    alert: Mapped["Alert"] = relationship("Alert", back_populates="predictions")


class SchedulerRun(Base):
    __tablename__ = "scheduler_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_name: Mapped[str] = mapped_column(String(100), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[RunStatusEnum] = mapped_column(Enum(RunStatusEnum), default=RunStatusEnum.RUNNING, nullable=False)
    logs_summary: Mapped[str | None] = mapped_column(Text, nullable=True)


class MessageHistory(Base):
    __tablename__ = "message_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    alert_id: Mapped[int] = mapped_column(Integer, ForeignKey("alerts.id"), nullable=False)
    telegram_chat_id: Mapped[str] = mapped_column(String(50), nullable=False)
    telegram_message_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[DeliveryStatusEnum] = mapped_column(Enum(DeliveryStatusEnum), default=DeliveryStatusEnum.PENDING, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    alert: Mapped["Alert"] = relationship("Alert", back_populates="messages")


class Setting(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)