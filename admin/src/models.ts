export interface Entity {
  id?: number
  name: string
  description?: string

  created_at?: string
  updated_at?: string
  created_by?: string
  updated_by?: string
}

export interface Participant extends Entity {
  token?: string
  identifier?: string
  status?: string
  company_id?: number
  campaign_id?: number
}

export interface Campaign extends Entity {
  url?: string
  company_id?: number
}

export interface Company extends Entity {
  campaings?: Campaign[]
}
