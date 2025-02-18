from typing import List, Dict, Optional
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy.dialects.postgresql import JSONB as JSON
from sqlalchemy import TIMESTAMP
from datetime import datetime

# Base classes


class TimestampMixin(SQLModel):
    created_at: datetime = Field(
        sa_column=TIMESTAMP(timezone=True), default=None)
    updated_at: datetime = Field(
        sa_column=TIMESTAMP(timezone=True), default=None)
    created_by: Optional[str] = Field(default=None)
    updated_by: Optional[str] = Field(default=None)


class Entity(TimestampMixin):
    name: str
    description: Optional[str] = Field(default=None)


class CompanyBase(Entity):
    administrators: Optional[List[str]]


class Company(CompanyBase, table=True):
    id: Optional[int] = Field(
        default=None,
        nullable=False,
        primary_key=True,
        index=True,
    )
    administrators: Optional[List[str]] = Field(
        default=None, sa_column=Column(JSON))
    campaigns: List["Campaign"] = Relationship(
        back_populates="company", cascade_delete=True)


class CampaignBase(Entity):
    slug: Optional[str] = Field(default=None)
    address: Optional[str] = Field(default=None)
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
    lat: Optional[float] = Field(default=None)
    lon: Optional[float] = Field(default=None)


class Campaign(CampaignBase, table=True):
    id: Optional[int] = Field(
        default=None,
        nullable=False,
        primary_key=True,
        index=True,
    )
    company_id: int = Field(default=None, foreign_key="company.id")
    company: Company | None = Relationship(back_populates="campaigns")
    participants: list["Participant"] = Relationship(
        back_populates="campaign", cascade_delete=True)


class ParticipantBase(TimestampMixin):
    token: str = Field(default=None, unique=True)
    identifier: str
    status: str = Field(default="open")
    data: Optional[Dict] = Field(default=None, sa_column=Column(JSON))


class Participant(ParticipantBase, table=True):
    id: Optional[int] = Field(
        default=None,
        nullable=False,
        primary_key=True,
        index=True,
    )
    campaign_id: int = Field(default=None, foreign_key="campaign.id")
    campaign: Campaign | None = Relationship(back_populates="participants")


class CaseReportBase(SQLModel):
    token: str
    data: Optional[Dict] = Field(default=None, sa_column=Column(JSON))


class CaseReport(CaseReportBase, table=True):
    id: Optional[int] = Field(
        default=None,
        nullable=False,
        primary_key=True,
        index=True,
    )
    campaign_id: int = Field(default=None, foreign_key="campaign.id")
    company_id: int = Field(default=None, foreign_key="company.id")


class DataEntryBase(Entity):
    identifier: str


class DataEntry(DataEntryBase, table=True):
    id: Optional[int] = Field(
        default=None,
        nullable=False,
        primary_key=True,
        index=True,
    )
    data: str


class AccessLogBase(Entity):
    username: str
    method: str = Field(default="GET")
    timestamp: datetime = Field(
        sa_column=TIMESTAMP(timezone=True), default=None)


class AccessLog(AccessLogBase, table=True):
    id: Optional[int] = Field(
        default=None,
        nullable=False,
        primary_key=True,
        index=True,
    )
    data_entry_id: int = Field(default=None, foreign_key="dataentry.id")

# Association tables


# Domain tables
