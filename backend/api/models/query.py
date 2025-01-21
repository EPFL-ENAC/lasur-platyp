from typing import List, Optional, Dict
from sqlmodel import Field
from sqlalchemy.dialects.postgresql import JSONB as JSON
from api.models.domain import CompanyBase, CampaignBase, ParticipantBase, CaseReportBase, DataEntryBase
from enacit4r_sql.models.query import ListResult


class CompanyRead(CompanyBase):
    id: int


class CompanyResult(ListResult):
    data: List[CompanyRead] = []


class CampaignRead(CampaignBase):
    id: int


class CampaignResult(ListResult):
    data: List[CampaignRead] = []


class ParticipantRead(ParticipantBase):
    id: int


class ParticipantResult(ListResult):
    data: List[ParticipantRead] = []


class CaseReportRead(CaseReportBase):
    id: int


class CaseReportResult(ListResult):
    data: List[CaseReportRead] = []


class DataEntryRead(DataEntryBase):
    id: int
