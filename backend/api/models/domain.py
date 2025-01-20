from typing import List, Dict, Any, Optional
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy.dialects.postgresql import JSONB as JSON
from sqlalchemy import TIMESTAMP
from datetime import datetime
from pydantic import BaseModel

# Base classes


class Entity(SQLModel):
    name: str
    description: Optional[str] = Field(default=None)

    created_at: datetime = Field(
        sa_column=TIMESTAMP(timezone=True), default=None)
    updated_at: datetime = Field(
        sa_column=TIMESTAMP(timezone=True), default=None)
    created_by: Optional[str] = Field(default=None)
    updated_by: Optional[str] = Field(default=None)


class FormBase(Entity):
    items: Dict[str, Any] = Field(default=None, sa_type=JSON)
    i18n: Dict[str, Any] = Field(default=None, sa_type=JSON)


class Form(FormBase, table=True):
    id: Optional[int] = Field(
        default=None,
        nullable=False,
        primary_key=True,
        index=True,
    )
    form_revisions: list["FormRevision"] = Relationship(back_populates="form")


class FormRevisionBase(Entity):
    items: Dict[str, Any] = Field(default=None, sa_type=JSON)
    i18n: Dict[str, Any] = Field(default=None, sa_type=JSON)
    version: int = Field(default=1)


class FormRevision(FormRevisionBase, table=True):
    id: Optional[int] = Field(
        default=None,
        nullable=False,
        primary_key=True,
        index=True,
    )
    form_id: int | None = Field(default=None, foreign_key="form.id")
    form: Form | None = Relationship(back_populates="form_revisions")
    campaigns: List["Campaign"] = Relationship(
        back_populates="form_revision", cascade_delete=True)


class CompanyBase(Entity):
    name: str


class Company(CompanyBase, table=True):
    id: Optional[int] = Field(
        default=None,
        nullable=False,
        primary_key=True,
        index=True,
    )
    campaigns: List["Campaign"] = Relationship(back_populates="company")


class CampaignBase(Entity):
    url: str


class Campaign(CampaignBase, table=True):
    id: Optional[int] = Field(
        default=None,
        nullable=False,
        primary_key=True,
        index=True,
    )
    form_revision_id: int = Field(default=None, foreign_key="formrevision.id")
    form_revision: FormRevision | None = Relationship(
        back_populates="campaigns")
    company_id: int = Field(default=None, foreign_key="company.id")
    company: Company | None = Relationship(back_populates="campaigns")
    participants: list["Participant"] = Relationship(back_populates="campaign")


class ParticipantBase(Entity):
    token: str
    identifier: str
    status: str = Field(default="open")


class Participant(ParticipantBase, table=True):
    id: Optional[int] = Field(
        default=None,
        nullable=False,
        primary_key=True,
        index=True,
    )
    campaign_id: int = Field(default=None, foreign_key="campaign.id")
    campaign: Campaign | None = Relationship(back_populates="participants")


class CaseReportBase(Entity):
    identifier: str


class CaseReport(CaseReportBase, table=True):
    id: Optional[int] = Field(
        default=None,
        nullable=False,
        primary_key=True,
        index=True,
    )
    data: str
    form_revision_id: int = Field(default=None, foreign_key="formrevision.id")
    participant_id: int = Field(default=None, foreign_key="participant.id")
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
