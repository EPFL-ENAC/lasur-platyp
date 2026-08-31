from typing import List, Literal, Optional, Dict

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
    response_id_in_campaign: Optional[int] = Field(default=None)


class RecordDraft(RecordBase):
    id: Optional[int] = Field(default=None)


class RecordComments(BaseModel):
    comments: Optional[str] = None


class RecordResult(ListResult):
    data: List[RecordRead] = []


class RecordCertificate(BaseModel):
    response_id_in_campaign: int
    rewards_message: dict[str, str]


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
    with_professional_questions: bool = True
    rewards_message: Optional[Dict[str, str]] = None


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


class Recommendation(BaseModel):
    target: str = ""
    value: int = 0


class StatLinks(Links):
    most_recommended_target: Optional[Recommendation] = None


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
    average_energy_per_unique_token: Optional[float] = None


class JourneyEnergyGainsByMode(BaseModel):
    """Energy gain (reduction) thanks to a specific mode if recommendations were followed."""
    mode: str
    added_kcal: float


class JourneyEnergyGains(BaseModel):
    """Energy gain (reduction) for a journey leg if recommendations were followed."""
    total: float
    gains_per_mode: List[JourneyEnergyGainsByMode] = []
    current_above_who_count: int = 0
    reco_above_who_count: int = 0


class JourneyEnergyStats(BaseModel):
    """Complete energy expenditure statistics."""
    current: EnergyByJourney
    reco: EnergyByJourney
    gains: JourneyEnergyGains


class BehaviorChangeLever(BaseModel):
    """Individual lever/measure category that helps adopt recommendations."""
    category: str  # finance, flexibility, collective, environment, other
    count: int
    percentage: float  # stored with 2 decimals


class BehaviorChangeMotivation(BaseModel):
    """Individual motivation level for adopting recommendations."""
    level: int  # 1-5
    count: int
    percentage: float  # stored with 2 decimals


class BehaviorChangeByModeBase(BaseModel):
    """Behavior change stats for a specific mode or aggregated group."""
    mode: str  # e.g., "velo", "train", "Autres", "Total"
    response_count: int  # number of people who answered this question type


class BehaviorChangeByModeLever(BehaviorChangeByModeBase):
    levers: List[BehaviorChangeLever] = []


class BehaviorChangeByModeMotivation(BehaviorChangeByModeBase):
    motivations: List[BehaviorChangeMotivation] = []


class BehaviorChangeStatsBase(BaseModel):
    total_responses: int
    aggregation_type: str  # "all_aggregated", "mode_split", or "mixed"


class BehaviorChangeStatsLever(BehaviorChangeStatsBase):
    by_mode_levers: List[BehaviorChangeByModeLever]


class BehaviorChangeStatsMotivation(BehaviorChangeStatsBase):
    by_mode_motivation: List[BehaviorChangeByModeMotivation] = []


class BehaviorChangeStats(BaseModel):
    """Complete behavior change statistics."""
    levers: BehaviorChangeStatsLever
    motivation: BehaviorChangeStatsMotivation
    other_levers: List[str] = []  # free-text responses from all modes


class EquipmentPerRecommendation(BaseModel):
    bike: int = 0
    ebike: int = 0
    tpu_unireso: int = 0
    tpu_leman_pass: int = 0
    train_demi_tarif: int = 0
    train_abo_gen: int = 0
    mob_subs: int = 0
    moto: int = 0
    car: int = 0
    car_driver: int = 0
    ev: int = 0
    inter: int = 0
    car_passenger: int = 0

    total: int = 0


class EquipmentRecommendationMatrix(BaseModel):
    marche: EquipmentPerRecommendation = EquipmentPerRecommendation()
    velo: EquipmentPerRecommendation = EquipmentPerRecommendation()
    vae: EquipmentPerRecommendation = EquipmentPerRecommendation()
    cargo: EquipmentPerRecommendation = EquipmentPerRecommendation()
    train: EquipmentPerRecommendation = EquipmentPerRecommendation()
    tpu: EquipmentPerRecommendation = EquipmentPerRecommendation()
    covoit: EquipmentPerRecommendation = EquipmentPerRecommendation()
    elec: EquipmentPerRecommendation = EquipmentPerRecommendation()
    inter: EquipmentPerRecommendation = EquipmentPerRecommendation()


class EquipmentsStats(BaseModel):
    total: int
    equipment_recommendation_matrix: EquipmentRecommendationMatrix


class Stats(BaseModel):
    total: int = 0
    frequencies: Optional[List[Frequencies]] = None
    mode_frequencies_simple_labels: Optional[List[Frequencies]] = None
    mode_frequencies_complex_labels: Optional[List[Frequencies]] = None
    mode_emissions_simple_labels: Optional[List[Emissions]] = None
    mode_emissions_complex_labels: Optional[List[Emissions]] = None
    reco_mode_emissions_simple_labels: Optional[List[Emissions]] = None
    reco_mode_emissions_complex_labels: Optional[List[Emissions]] = None
    mode_emission_reductions_simple_labels: Optional[List[EmissionReductions]] = None
    mode_emission_reductions_complex_labels: Optional[List[EmissionReductions]] = None
    mode_links_simple_labels: Optional[StatLinks] = None
    mode_links_complex_labels: Optional[StatLinks] = None
    pro_frequencies: Optional[List[Frequencies]] = None
    pro_mode_frequencies: Optional[List[Frequencies]] = None
    pro_mode_emissions: Optional[List[Emissions]] = None
    pro_reco_mode_emissions: Optional[List[Emissions]] = None
    pro_mode_emission_reductions: Optional[List[EmissionReductions]] = None
    pro_mode_links: Optional[StatLinks] = None
    home_location_heatmap: Optional[Dict[str, int]] = None
    workplace_locations: Optional[List[dict]] = None
    workplace_location_heatmap: Optional[Dict[str, int]] = None
    mode_energy: Optional[List[EnergyExpenditure]] = None
    reco_mode_energy: Optional[List[EnergyExpenditure]] = None
    journey_energy_stats: Optional[JourneyEnergyStats] = None
    behavior_change: Optional[BehaviorChangeStats] = None
    equipments_stats: Optional[EquipmentsStats] = None


class CampaignGroup(BaseModel):
    name: str
    campaign_ids: List[int]


class ComparisonRequest(BaseModel):
    groups: List[CampaignGroup]
    mode: Literal["cross_sectional", "longitudinal"] = "cross_sectional"
    filter: Optional[dict] = None


class ComparisonStats(Stats):
    name: str
    campaign_ids: List[int]


class ModeTransition(BaseModel):
    source_group: str
    target_group: str
    source_mode: str
    target_mode: str
    count: int


class ComparisonResult(BaseModel):
    groups: List[ComparisonStats] = []
    mode_transitions: Optional[List[ModeTransition]] = None
    warnings: Optional[List[str]] = None


class GeoWithin(BaseModel):
    geometry: Polygon | MultiPolygon = Field(validation_alias="$geometry")


class LocationFilter(BaseModel):
    geo_within: GeoWithin = Field(validation_alias="$geoWithin")
