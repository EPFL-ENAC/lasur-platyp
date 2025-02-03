from typing import List, Optional
from sqlmodel import Field
from api.models.domain import CompanyBase, CampaignBase, ParticipantBase, CaseReportBase, DataEntryBase
from enacit4r_sql.models.query import ListResult


class CompanyRead(CompanyBase):
    id: int


class CompanyResult(ListResult):
    data: List[CompanyRead] = []


class CampaignRead(CampaignBase):
    id: int
    company_id: int


class CampaignDraft(CampaignBase):
    id: Optional[int] = Field(default=None)
    company_id: int = Field(default=None)


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
