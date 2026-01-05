from typing import List, Dict, Optional
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy.dialects.postgresql import JSONB as JSON
from sqlalchemy import TIMESTAMP
from datetime import datetime
from pydantic import BaseModel

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


class EmployerActions(BaseModel):
    mesures_globa: Optional[List[str]] = Field(default=[])
    mesures_tpu: Optional[List[str]] = Field(default=[])
    mesures_train: Optional[List[str]] = Field(default=[])
    mesures_inter: Optional[List[str]] = Field(default=[])
    mesures_velo: Optional[List[str]] = Field(default=[])
    mesures_covoit: Optional[List[str]] = Field(default=[])
    mesures_elec: Optional[List[str]] = Field(default=[])
    mesures_pro_globa: Optional[List[str]] = Field(default=[])
    mesures_pro_velo: Optional[List[str]] = Field(default=[])
    mesures_pro_tpu: Optional[List[str]] = Field(default=[])
    mesures_pro_train: Optional[List[str]] = Field(default=[])
    mesures_pro_elec: Optional[List[str]] = Field(default=[])


class CompanyBase(Entity):
    administrators: Optional[List[str]] = Field(default=None)
    actions: Optional[EmployerActions] = Field(
        default=None, sa_column=Column(JSON))


class Company(CompanyBase, table=True):
    id: Optional[int] = Field(
        default=None,
        nullable=False,
        primary_key=True,
        index=True,
    )
    administrators: Optional[List[str]] = Field(
        default=None, sa_column=Column(JSON))
    contact_email: Optional[str] = Field(default=None)
    contact_name: Optional[str] = Field(default=None)
    info_url: Optional[str] = Field(default=None)
    campaigns: List["Campaign"] = Relationship(
        back_populates="company", cascade_delete=True)
    custom_actions: List["CompanyAction"] = Relationship(
        back_populates="company", cascade_delete=True)


class CompanyActionBase(SQLModel):
    group: str  # mode of transport or global
    # key is language code, value is label in this language
    labels: Optional[Dict] = Field(default=None, sa_column=Column(JSON))


class CompanyAction(CompanyActionBase, table=True):
    id: Optional[int] = Field(
        default=None,
        nullable=False,
        primary_key=True,
        index=True,
    )
    company_id: int = Field(default=None, foreign_key="company.id")
    company: Company | None = Relationship(back_populates="custom_actions")


class CampaignBase(Entity):
    slug: Optional[str] = Field(default=None)
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
    contact_email: Optional[str] = Field(default=None)
    contact_name: Optional[str] = Field(default=None)
    info_url: Optional[str] = Field(default=None)
    actions: Optional[EmployerActions] = Field(
        default=None, sa_column=Column(JSON))
    open_workplaces: bool = Field(default=False)


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
    workplaces: list["Workplace"] = Relationship(
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


class WorkplaceBase(SQLModel):
    name: Optional[str] = Field(default=None)
    address: Optional[str] = Field(default=None)
    lat: Optional[float] = Field(default=None)
    lon: Optional[float] = Field(default=None)


class Workplace(WorkplaceBase, table=True):
    id: Optional[int] = Field(
        default=None,
        nullable=False,
        primary_key=True,
        index=True,
    )
    campaign_id: int = Field(default=None, foreign_key="campaign.id")
    campaign: Campaign | None = Relationship(back_populates="workplaces")


class RecordBase(SQLModel):
    token: str
    data: Optional[Dict] = Field(default=None, sa_column=Column(JSON))
    typo: Optional[Dict] = Field(default=None, sa_column=Column(JSON))
    comments: Optional[str] = Field(default=None)
    created_at: Optional[datetime] = Field(
        sa_column=TIMESTAMP(timezone=True), default=None)
    updated_at: Optional[datetime] = Field(
        sa_column=TIMESTAMP(timezone=True), default=None)


class Record(RecordBase, table=True):
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
