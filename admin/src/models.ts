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
  company_id?: number
  actions?: EmployerActions
  workplaces?: Workplace[]
}

export interface CompanyAction {
  id?: number
  group: string
  labels?: { [key: string]: string }
  company_id: number
}

export interface Company extends Entity {
  administrators: string[]
  contact_email?: string
  contact_name?: string
  info_url?: string
  campaings?: Campaign[]
  custom_actions?: CompanyAction[]
  actions?: EmployerActions
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

export interface Record {
  id: number
  token: string
  created_at?: string
  updated_at?: string
  created_by?: string
  updated_by?: string
  company_id: number
  campaign_id: number

  data?: { [key: string]: number | string | string[] | boolean }
  typo?: { [key: string]: { [key: string]: number | string | string[] | boolean } }
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

export interface Link {
  source: string
  target: string
  value: number
}

export interface Links {
  total: number
  data: Link[]
}

export interface Stats {
  total: number
  frequencies: Frequencies[] | null
  mode_frequencies: Frequencies[] | null
  mode_emissions: Emissions[] | null
  reco_mode_emissions: Emissions[] | null
  mode_links: Links | null
  pro_frequencies: Frequencies[] | null
  pro_mode_frequencies: Frequencies[] | null
  pro_mode_emissions: Emissions[] | null
  pro_mode_links: Links | null
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

export interface IsochronesModes {
  [key: string]: string[]
}
