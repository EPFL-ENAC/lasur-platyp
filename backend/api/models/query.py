from typing import List, Optional, Dict
from pydantic import BaseModel
from sqlmodel import Field
from api.models.domain import CompanyBase, CompanyActionBase, CampaignBase, ParticipantBase, RecordBase, DataEntryBase
from enacit4r_sql.models.query import ListResult


class CompanyRead(CompanyBase):
    id: int


class CompanyResult(ListResult):
    data: List[CompanyRead] = []


class CompanyActionRead(CompanyActionBase):
    id: int
    company_id: int


class CompanyActionDraft(CompanyActionBase):
    id: Optional[int] = Field(default=None)
    company_id: int = Field(default=None)


class CompanyActionResult(ListResult):
    data: List[CompanyActionRead] = []


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


class RecordRead(RecordBase):
    id: int
    campaign_id: Optional[int] = Field(default=None)
    company_id: Optional[int] = Field(default=None)


class RecordDraft(RecordBase):
    id: Optional[int] = Field(default=None)


class RecordComments(BaseModel):
    comments: Optional[str] = None


class RecordResult(ListResult):
    data: List[RecordRead] = []


class DataEntryRead(DataEntryBase):
    id: int


class ParticipantData(BaseModel):
    data: Optional[Dict] = None


class CampaignInfo(BaseModel):
    name: str
    company_name: str
    contact_email: Optional[str] = None
    contact_name: Optional[str] = None
    info_url: Optional[str] = None


class Frequency(BaseModel):
    value: Optional[str] = None
    count: Optional[int] = None
    sum: Optional[int] = None


class Frequencies(BaseModel):
    field: Optional[str] = None
    total: Optional[int] = None
    data: List[Frequency] = []


class AllFrequencies(BaseModel):
    total: int = 0
    equipments: Optional[Frequencies] = None
    constraints: Optional[Frequencies] = None
    travel_time: Optional[Frequencies] = None
    reco_dt2: Optional[Frequencies] = None
    freq_mod: Optional[List[Frequencies]] = None


class Emissions(BaseModel):
    field: Optional[str] = None
    total: Optional[int] = None
    distances: Optional[float] = None
    journeys: Optional[int] = None
    emissions: Optional[float] = None


class Link(BaseModel):
    source: str
    target: str
    value: float


class Links(BaseModel):
    total: Optional[int] = None
    data: List[Link] = []
