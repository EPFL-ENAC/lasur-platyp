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


class JourneyEnergyLeg(BaseModel):
    """Energy expenditure for a single journey leg (per person)."""
    token: str
    journey_id: str
    mode: str
    days: int
    travel_time: float
    energy_kcal: float
    is_intermodal: bool = False


class EnergyExpenditure(BaseModel):
    """Aggregated energy expenditure per mode."""
    mode: str
    total: int
    total_time: float
    journeys: int
    energy_kcal: float
    avg_daily_kcal: float


class EnergyByJourney(BaseModel):
    """Energy expenditure broken down by journey legs."""
    total: int
    data: List[JourneyEnergyLeg] = []


class BehaviorChangeLever(BaseModel):
    """Individual lever/measure category that helps adopt recommendations."""
    category: str  # finance, flexibility, collective, environment, other
    label: str  # French display label
    count: int
    percentage: float  # stored with 2 decimals


class BehaviorChangeMotivation(BaseModel):
    """Individual motivation level for adopting recommendations."""
    level: int  # 1-5
    label: str  # French label (e.g., "Très motivé·e")
    count: int
    percentage: float  # stored with 2 decimals


class BehaviorChangeByMode(BaseModel):
    """Behavior change stats for a specific mode or aggregated group."""
    mode: str  # e.g., "velo", "train", "Autres", "Total"
    response_count: int  # number of people who answered this question type
    levers: List[BehaviorChangeLever] = []  # empty if this is motivation-only data
    motivation: List[BehaviorChangeMotivation] = []  # empty if this is lever-only data


class BehaviorChangeStats(BaseModel):
    """Complete behavior change statistics."""
    total_lever_responses: int  # total people who answered lever questions
    total_motivation_responses: int  # total people who answered motivation question
    lever_aggregation_type: str  # "all_aggregated", "mode_split", or "mixed"
    motivation_aggregation_type: str  # "all_aggregated", "mode_split", or "mixed"
    by_mode_levers: List[BehaviorChangeByMode]
    by_mode_motivation: List[BehaviorChangeByMode]
    other_levers: List[str] = []  # free-text responses from all modes


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
    home_location_heatmap: Optional[Dict[str, int]] = None
    workplace_locations: Optional[List[dict]] = None
    workplace_location_heatmap: Optional[Dict[str, int]] = None
    mode_energy: Optional[List[EnergyExpenditure]] = None
    reco_mode_energy: Optional[List[EnergyExpenditure]] = None
    journey_energy_current: Optional[EnergyByJourney] = None
    journey_energy_reco: Optional[EnergyByJourney] = None
    behavior_change: Optional[BehaviorChangeStats] = None


class GeoWithin(BaseModel):
    geometry: Polygon | MultiPolygon = Field(validation_alias="$geometry")


class LocationFilter(BaseModel):
    geo_within: GeoWithin = Field(validation_alias="$geoWithin")
