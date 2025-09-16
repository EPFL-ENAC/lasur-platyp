export interface ParticipantData {
  data: {
    age_class: string
    employment_rate: number
    remote_work_rate: number
    company_vehicle: boolean
  }
}

export interface Location {
  lat?: number | undefined
  lon?: number | undefined
}

export interface AddressLocation extends Location {
  address: string | undefined
}

export interface Journey {
  modes: string[]
  days: number
}

export interface ProJourney {
  mode: string
  days: number
  hex_id: string | undefined
}

export interface RecordData {
  terms_conditions: boolean
  confidentiality: boolean

  age_class: string
  employment_rate: number
  remote_work_rate: number
  company_vehicle: boolean
  travel_time: number
  equipments: string[]
  constraints: string[]
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
  change: Change
}

export interface Record {
  data: RecordData
  token: string
}

export interface Recommendation {
  reco?: {
    reco_dt2: string[]
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
    mesure_pro_loc: string[]
    mesure_pro_regint: string[]
    mesures_globa?: string[]
    mesures_pro_globa?: string[]
  }
  reco_pro?: {
    reco_pro_int: string
    reco_pro_loc: string
    reco_pro_reg: string
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
}
