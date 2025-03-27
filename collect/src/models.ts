export interface ParticipantData {
  data: {
    age_class: string
    employment_rate: number
    remote_work_rate: number
    company_vehicle: boolean
  }
}

export interface AddressLocation {
  address: string | undefined
  lat?: number | undefined
  lon?: number | undefined
}

export interface RecordData {
  age_class: string
  employment_rate: number
  remote_work_rate: number
  company_vehicle: boolean
  travel_time: number
  equipments: string[]
  constraints: string[]
  freq_mod_walking: number
  freq_mod_bike: number
  freq_mod_pub: number
  freq_mod_moto: number
  freq_mod_car: number
  freq_mod_train: number
  freq_mod_combined: boolean

  trav_pro: string[]
  freq_mod_pro_local_walking: number
  freq_mod_pro_local_bike: number
  freq_mod_pro_local_pub: number
  freq_mod_pro_local_moto: number
  freq_mod_pro_local_car: number
  freq_mod_pro_local_train: number
  freq_mod_pro_local_combined: boolean

  freq_mod_pro_region_pub: number
  freq_mod_pro_region_moto: number
  freq_mod_pro_region_car: number
  freq_mod_pro_region_train: number
  freq_mod_pro_region_plane: number
  freq_mod_pro_region_combined: boolean

  freq_mod_pro_inter_car: number
  freq_mod_pro_inter_train: number
  freq_mod_pro_inter_plane: number
  freq_mod_pro_inter_combined: boolean

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
  adjectives_bikes: string[]
  adjectives_pubs: string[]
  adjectives_motors: string[]
  comments: string
  workplace: AddressLocation
  origin: AddressLocation
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
    }
  }
  reco_actions?: {
    mesure_dt1: string[]
    mesure_dt2: string[]
    mesure_pro_loc: string[]
    mesure_pro_regint: string[]
    mesures_globa?: string[]
  }
  reco_pro?: {
    reco_pro_int: string
    reco_pro_loc: string
    reco_pro_reg: string
  }
}
