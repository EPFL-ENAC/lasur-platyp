from typing import List, Optional, Dict
from pydantic import BaseModel
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
    campaign_id: int


class ParticipantDraft(ParticipantBase):
    id: Optional[int] = Field(default=None)
    token: Optional[str] = Field(default=None)
    campaign_id: int = Field(default=None)


class ParticipantResult(ListResult):
    data: List[ParticipantRead] = []


class CaseReportRead(CaseReportBase):
    id: int


class CaseReportDraft(CaseReportBase):
    id: Optional[int] = Field(default=None)


class CaseReportResult(ListResult):
    data: List[CaseReportRead] = []


class DataEntryRead(DataEntryBase):
    id: int


class ParticipantData(BaseModel):
    data: Optional[Dict] = None
