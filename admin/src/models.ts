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

export interface Campaign extends Entity {
  slug?: string
  address?: string
  start_date?: string | undefined
  end_date?: string | undefined
  lat?: number | undefined
  lon?: number | undefined
  company_id?: number
  actions?: EmployerActions
}

export interface Company extends Entity {
  administrators: string[]
  campaings?: Campaign[]
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
