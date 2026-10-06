export interface Filter {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  [key: string]: any
}

export interface Query {
  $skip?: number
  $limit?: number
  $sort?: [string, boolean] // [field, descending]
  $select?: string[]
  filter?: Filter
}

export const DefaultAlignment: 'left' | 'right' | 'center' = 'left'

export interface AddressLocation {
  address: string
  lat?: number | undefined
  lon?: number | undefined
}

export type BoundaryLevel = 'filtering'

export interface PlaceLocation {
  lat: number
  lon: number
  level: BoundaryLevel
  feature_id?: string | number | undefined
}
