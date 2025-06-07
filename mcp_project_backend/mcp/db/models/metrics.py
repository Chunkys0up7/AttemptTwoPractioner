from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from datetime import datetime
from mcp.db.base import Base

class Metric(Base):
    __tablename__ = 'metrics'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    value = Column(Float, nullable=False)
    labels = Column(JSON, nullable=True)  # e.g., {"workflow_id": ..., "type": ...}
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    source = Column(String(100), nullable=True)  # e.g., 'backend', 'worker', etc.

    def __repr__(self):
        return f"<Metric(name={self.name}, value={self.value}, recorded_at={self.recorded_at})>"

class Alert(Base):
    __tablename__ = 'alerts'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    metric_name = Column(String(255), nullable=False)
    threshold = Column(Float, nullable=False)
    comparison = Column(String(10), nullable=False, default='>')  # e.g., '>', '<', '=='
    is_active = Column(Boolean, default=True, nullable=False)
    triggered_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    details = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<Alert(name={self.name}, metric={self.metric_name}, threshold={self.threshold}, active={self.is_active})>" 