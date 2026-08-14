export interface ParticipantData {
  data: {
    age_class: string
    employment_rate: number
    remote_work_rate: number
    company_vehicle?: boolean
  }
}

export interface Location {
  lat?: number | undefined
  lon?: number | undefined
}

export interface AddressLocation extends Location {
  name?: string | undefined
  address: string | undefined
}

export interface Journey {
  modes: string[]
  days: number
}

export type BoundaryLevel = 'national' | 'regional' | 'local'

export interface PlaceLocation {
  lat: number
  lon: number
  level: BoundaryLevel
  feature_id?: string | number | undefined
}

export interface ProJourney {
  mode: string
  days: number
  days_per: 'week' | 'month' | 'year'
  is_company_vehicle?: boolean | undefined
  constraints?: string[]
  /** @deprecated superseded by `location`, kept for backward compatibility with older records */
  hex_id?: string | undefined
  location?: PlaceLocation | undefined
}

export interface RecordData {
  terms_conditions: boolean
  confidentiality: boolean

  age_class: string
  employment_rate: number
  remote_work_rate: number
  company_vehicle?: boolean
  travel_time: number
  equipments: string[]
  equipments_custom?: string | undefined
  constraints: string[]
  constraints_custom?: string | undefined
  freq_mod_journeys: Journey[]

  travel_pro: boolean
  freq_mod_pro_journeys: ProJourney[]

  importance_time: number
  importance_cost: number
  importance_flex: number
  importance_rel: number
  importance_comfort: number
  importance_most: number
  importance_env: number
  needs_walking: number
  needs_bike: number
  needs_pub: number
  needs_moto: number
  needs_car: number
  needs_train: number
  comments: string
  workplace: AddressLocation
  origin: AddressLocation
  changes: Change[]
}

export interface Record {
  data: RecordData
  typo: Recommendation | null
  token: string
  email_hash: string | null
  response_id_in_campaign: number | null
}

export interface RecordCertificate {
  response_id_in_campaign: number | null
  rewards_message: { [key: string]: string } | null
}

export interface Recommendation {
  reco?: {
    reco_inter: string[]
    scores: {
      covoit: number
      elec: number
      inter: number
      marche: number
      tpu: number
      train: number
      vae: number
      velo: number
      cargo: number
    }
    access: {
      covoit: number
      elec: number
      inter: number
      marche: number
      tpu: number
      train: number
      vae: number
      velo: number
      cargo: number
    }
  }
  reco_actions?: {
    mesure_dt1: string[]
    mesure_dt2: string[]
    mesures_globa?: string[]
    mesure_pro: string[][]
    mesures_pro_globa?: string[]
    mesures_pro_velo?: string[]
    mesures_pro_tpu?: string[]
    mesures_pro_train?: string[]
    mesures_pro_elec?: string[]
  }
  reco_pro?: {
    reco_pros: string[]
  }
}

export interface Change {
  motivation?: number
  levers?: string[]
  other_levers?: string | undefined
}

export interface CampaignInfo {
  name: string
  company_name: string
  contact_name?: string
  contact_email?: string
  info_url?: string
  workplaces: AddressLocation[]
  with_professional_questions?: boolean
  open_workplaces?: boolean
  rewards_message?: { [key: string]: string }
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
}

export interface PoisParams {
  categories: string[]
  bbox: [number, number, number, number]
}

export interface RecommendationsPreviewData {
  perso: {
    mainFm: string
    isModeSustainable: boolean
    isModeOptions: boolean
    journeys: Journey[]
    recoInter: string[]
    center: [number, number] | null
    mesureDt1: string[]
    mesureDt2: string[]
    globalActions: string[]
  }
  pro: {
    proJourneys: ProJourney[]
    recoPros: string[]
    proJourneyLocations: (PlaceLocation | undefined)[]
    mesurePro: string[][]
    globalActions: string[]
  }
}
