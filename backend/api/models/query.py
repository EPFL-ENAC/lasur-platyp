from typing import List, Optional, Dict

from pydantic import BaseModel, Field
from geojson_pydantic import Polygon, MultiPolygon
from api.models.domain import CompanyBase, CompanyActionBase, CampaignBase, ParticipantBase, RecordBase, DataEntryBase, WorkplaceBase
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


class WorkplaceRead(WorkplaceBase):
    id: int
    campaign_id: int


class WorkplaceDraft(WorkplaceBase):
    id: Optional[int] = Field(default=None)
    campaign_id: int = Field(default=None)


class CampaignRead(CampaignBase):
    id: int
    company_id: int
    workplaces: List[WorkplaceRead] = []


class CampaignDraft(CampaignBase):
    id: Optional[int] = Field(default=None)
    company_id: int = Field(default=None)
    workplaces: List[WorkplaceDraft] = []


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
    workplaces: List[WorkplaceRead] = []
    open_workplaces: bool = False


class WeeklyStats(BaseModel):
    week: str
    created: int
    completed: int


class CampaignStats(BaseModel):
    name: str
    company_id: Optional[int] = None
    campaign_id: Optional[int] = None
    nb_employees: Optional[int] = None
    completed_records: int = 0
    total_records: int = 0
    weekly: Optional[List[WeeklyStats]] = None


class Frequency(BaseModel):
    value: Optional[str] = None
    count: Optional[int] = None
    sum: Optional[int] = None


class Frequencies(BaseModel):
    field: Optional[str] = None
    total: Optional[int] = None
    data: List[Frequency] = []


class Emissions(BaseModel):
    """For each mode (actual or recommended), how much emissions were produced."""
    mode: Optional[str] = None
    total: Optional[int] = None
    distances: Optional[float] = None
    journeys: Optional[int] = None
    emissions: Optional[float] = None


class EmissionReductions(BaseModel):
    """For each recommended mode, how much emissions were reduced, independently from the actual mode used."""
    mode: Optional[str] = None
    total: Optional[int] = None
    reduced: Optional[float] = None


class Link(BaseModel):
    source: str
    target: str
    value: int


class Links(BaseModel):
    total: Optional[int] = None
    data: List[Link] = []


class Stats(BaseModel):
    total: int = 0
    frequencies: Optional[List[Frequencies]] = None
    mode_frequencies: Optional[List[Frequencies]] = None
    mode_emissions: Optional[List[Emissions]] = None
    reco_mode_emissions: Optional[List[Emissions]] = None
    mode_links: Optional[Links] = None
    pro_frequencies: Optional[List[Frequencies]] = None
    pro_mode_frequencies: Optional[List[Frequencies]] = None
    pro_mode_emissions: Optional[List[Emissions]] = None
    pro_mode_links: Optional[Links] = None


class GeoWithin(BaseModel):
    geometry: Polygon | MultiPolygon = Field(validation_alias="$geometry")


class LocationFilter(BaseModel):
    geo_within: GeoWithin = Field(validation_alias="$geoWithin")
