export interface Entity {
  id?: number
  name: string
  description?: string

  created_at?: string
  updated_at?: string
  created_by?: string
  updated_by?: string
}

export interface EmployerActions {
  [key: string]: string[]
}

export interface Participant extends Entity {
  token?: string
  identifier?: string
  status?: string
  company_id?: number
  campaign_id?: number
  data?: ParticipantData
}

export interface Workplace {
  id?: number
  name: string
  address: string
  lat: number
  lon: number
}

export interface Campaign extends Entity {
  slug?: string
  address?: string
  start_date?: string | undefined
  end_date?: string | undefined
  lat?: number | undefined
  lon?: number | undefined
  contact_email?: string
  contact_name?: string
  info_url?: string
  nb_employees?: number
  company_id?: number
  actions?: EmployerActions
  rewards_message?: { [locale: string]: string } | undefined
  workplaces?: Workplace[]
  open_workplaces?: boolean
  with_professional_questions: boolean
}

export interface CompanyAction {
  id?: number
  group: string
  labels?: { [key: string]: string }
  company_id: number
}

export interface Company extends Entity {
  administrators: string[]
  mobility_advisors?: string[]
  can_be_cited: boolean
  contact_email?: string
  contact_name?: string
  info_url?: string
  campaigns?: Campaign[]
  custom_actions?: CompanyAction[]
}

export interface AppUser {
  id?: string
  username: string
  email: string
  email_verified: boolean
  first_name?: string
  last_name?: string
  enabled: boolean
  totp: boolean
  roles: string[]
  password?: string
}

export interface ParticipantData {
  identifier: string
  age_class: string
  employment_rate: number
  remote_work_rate: number
  company_vehicle: boolean
}

export interface RecordData {
  [key: string]: number | string | string[] | boolean
}

export interface RecordTypo {
  [key: string]: RecordData
}

export interface Record {
  id: number
  token: string
  response_id_in_campaign?: number
  created_at?: string
  updated_at?: string
  created_by?: string
  updated_by?: string
  company_id: number
  campaign_id: number
  data?: RecordData
  typo?: RecordTypo
  comments?: string
}

export interface Frequency {
  value: string
  count: number
  sum?: number
}
export interface Frequencies {
  field: string
  total: number
  data: Frequency[]
}

export interface Emissions {
  mode: string
  total: number
  distances: number
  journeys: number
  emissions: number
}

export interface EmissionReduction {
  mode: string
  total: number
  reduced: number
}

export interface Link {
  source: string
  target: string
  value: number
}

export interface Links {
  total: number
  data: Link[]
}

export interface StatLinks extends Links {
  most_recommended_target: {
    target: string
    value: number
  } | null
}

export interface EnergyByLabel {
  token: string
  label: string
  energy_kcal: number
}
export interface EnergyBreakdown {
  simple: EnergyByLabel[]
  detailed: EnergyByLabel[]
}
export interface JourneyEnergy {
  total: number
  average_energy_per_unique_token?: number | null
  breakdown: EnergyBreakdown
}
export interface JourneyEnergyGainsByLabel {
  label: string
  added_kcal: number
}
export interface JourneyEnergyGainsBreakdown {
  simple: JourneyEnergyGainsByLabel[]
  detailed: JourneyEnergyGainsByLabel[]
}
export interface JourneyEnergyGains {
  total: number
  gains_per_mode: JourneyEnergyGainsBreakdown
  current_above_who_count: number
  reco_above_who_count: number
}
export interface JourneyEnergyStats {
  current: JourneyEnergy
  reco: JourneyEnergy
  gains: JourneyEnergyGains
}

export function makeDefaultJourneyEnergyStats(): JourneyEnergyStats {
  return {
    current: { total: 0, breakdown: { simple: [], detailed: [] } },
    reco: { total: 0, breakdown: { simple: [], detailed: [] } },
    gains: {
      total: 0,
      gains_per_mode: { simple: [], detailed: [] },
      current_above_who_count: 0,
      reco_above_who_count: 0,
    },
  }
}

export interface BehaviorChangeLever {
  category: string
  count: number
  percentage: number
}

export interface BehaviorChangeMotivation {
  level: number
  count: number
  percentage: number
}

export interface BehaviorChangeByModeBase {
  mode: string
  response_count: number
}

export interface BehaviorChangeByModeLever extends BehaviorChangeByModeBase {
  levers: BehaviorChangeLever[]
}

export interface BehaviorChangeByModeMotivation extends BehaviorChangeByModeBase {
  motivations: BehaviorChangeMotivation[]
}

export interface BehaviorChangeStatsBase {
  total_responses: number
  aggregation_type: string
}

export interface BehaviorChangeStatsLever extends BehaviorChangeStatsBase {
  by_mode_levers: BehaviorChangeByModeLever[]
}

export interface BehaviorChangeStatsMotivation extends BehaviorChangeStatsBase {
  by_mode_motivation: BehaviorChangeByModeMotivation[]
}

export interface BehaviorChangeStats {
  levers: BehaviorChangeStatsLever
  motivation: BehaviorChangeStatsMotivation
  other_levers: string[]
}

export function makeDefaultBehaviorChangeStats(): BehaviorChangeStats {
  return {
    levers: {
      total_responses: 0,
      aggregation_type: 'all_aggregated',
      by_mode_levers: [],
    },
    motivation: {
      total_responses: 0,
      aggregation_type: 'all_aggregated',
      by_mode_motivation: [],
    },
    other_levers: [],
  }
}

export interface EquipmentPerRecommendation {
  bike: number
  ebike: number
  tpu_unireso: number
  tpu_leman_pass: number
  train_demi_tarif: number
  train_abo_gen: number
  mob_subs: number
  moto: number
  car: number
  ev: number
  inter: number

  total: number
}

export interface EquipmentRecommendationMatrix {
  marche: EquipmentPerRecommendation
  velo: EquipmentPerRecommendation
  vae: EquipmentPerRecommendation
  cargo: EquipmentPerRecommendation
  train: EquipmentPerRecommendation
  tpu: EquipmentPerRecommendation
  covoit: EquipmentPerRecommendation
  elec: EquipmentPerRecommendation
  inter: EquipmentPerRecommendation
}

export const recommendationLabels = [
  'marche',
  'velo',
  'vae',
  'cargo',
  'train',
  'tpu',
  'covoit',
  'elec',
  'inter',
] as const

export const recommendationLabelsReversed = recommendationLabels.toReversed()

export const equipmentLabels = [
  'bike',
  'ebike',
  'tpu_unireso',
  'tpu_leman_pass',
  'train_demi_tarif',
  'train_abo_gen',
  'mob_subs',
  'moto',
  'car',
  'ev',
  'inter',
] as const

export const recommendationToEquipmentMap: {
  [key in (typeof recommendationLabels)[number]]: (typeof equipmentLabels)[number][] | null
} = {
  marche: null,
  velo: ['bike'],
  vae: ['ebike'],
  cargo: null,
  train: ['train_demi_tarif', 'train_abo_gen'],
  tpu: ['tpu_unireso', 'tpu_leman_pass'],
  covoit: ['mob_subs'],
  elec: ['ev'],
  inter: ['inter'],
}

export interface EquipmentsStats {
  total: number
  equipment_recommendation_matrix: EquipmentRecommendationMatrix
}

export type H3Heatmap = { [hexId: string]: number }

export interface LatLon {
  lat: number
  lon: number
}

export interface Stats {
  total: number
  frequencies: Frequencies[] | null
  mode_frequencies_complex_labels: Frequencies[] | null
  mode_frequencies_simple_labels: Frequencies[] | null
  mode_emissions_simple_labels: Emissions[] | null
  mode_emissions_complex_labels: Emissions[] | null
  mode_emission_reductions_simple_labels: EmissionReduction[] | null
  mode_emission_reductions_complex_labels: EmissionReduction[] | null
  reco_mode_emissions_simple_labels: Emissions[] | null
  reco_mode_emissions_complex_labels: Emissions[] | null
  mode_links_simple_labels: StatLinks | null
  mode_links_complex_labels: StatLinks | null
  pro_frequencies: Frequencies[] | null
  pro_mode_frequencies: Frequencies[] | null
  pro_mode_emissions: Emissions[] | null
  pro_reco_mode_emissions: Emissions[] | null
  pro_mode_emission_reductions: EmissionReduction[] | null
  pro_mode_links: StatLinks | null
  home_location_heatmap: H3Heatmap | null
  workplace_locations: LatLon[] | null
  journey_energy_stats: JourneyEnergyStats | null
  behavior_change: BehaviorChangeStats | null
  equipments_stats: EquipmentsStats | null
}

export type ComparisonMode = 'cross_sectional' | 'longitudinal'

export interface CampaignGroup {
  name: string
  label?: string
  campaign_ids: number[]
}

export interface ComparisonStats extends Stats {
  name: string
  campaign_ids: number[]
}

export interface ModeTransition {
  source_group: string
  target_group: string
  source_mode: string
  target_mode: string
  count: number
}

export interface ComparisonResult {
  groups: ComparisonStats[]
  mode_transitions?: ModeTransition[]
  warnings?: string[]
}

export interface IsochronesParams {
  lon: number
  lat: number
  mode: string
  cutoffSec: number[]
  bikeSpeed?: number
  datetime: string
  categories: string[]
}

export interface IsochronesData {
  isochrones: GeoJSON.FeatureCollection<GeoJSON.Geometry>
  pois: GeoJSON.FeatureCollection<GeoJSON.Geometry>
  transit?: GeoJSON.FeatureCollection<GeoJSON.Geometry> | null
}

export interface PoisParams {
  categories: string[]
  bbox: [number, number, number, number]
}

export interface IsochronesModes {
  [key: string]: string[]
}

export interface WeeklyStats {
  week: string
  created: number
  completed: number
}

export interface CampaignStats {
  name: string
  company_id?: number
  campaign_id?: number
  nb_employees?: number
  completed_records: number
  total_records: number
  weekly?: WeeklyStats[]
}
