export interface ModeIcon {
  icon: string
  isSvg: boolean
}

export const modeIcons: Record<string, ModeIcon> = {
  walking: { icon: 'directions_walk', isSvg: false },
  bike: { icon: 'pedal_bike', isSvg: false },
  ebike: { icon: 'electric_bike', isSvg: false },
  pub: { icon: 'directions_bus', isSvg: false },
  moto: { icon: 'two_wheeler', isSvg: false },
  car: { icon: 'directions_car', isSvg: false },
  carpool: { icon: '/icons/directions_carpool.svg', isSvg: true },
  train: { icon: 'directions_railway', isSvg: false },
  other: { icon: '/icons/scooter.svg', isSvg: true },
  cargo: { icon: 'directions_bike', isSvg: false },
  truck: { icon: 'directions_car', isSvg: false },
  plane: { icon: 'airplanemode_active', isSvg: false },
  boat: { icon: 'directions_boat', isSvg: false },
}

/**
 * Get the icon for a given mode code.
 */
export function getModeIcon(mode: string): ModeIcon | undefined {
  return modeIcons[mode]
}

/**
 * Recommendation codes are their own vocabulary, separate from the mode codes
 * above, so they need their own lookup rather than reusing `modeIcons`.
 */
export const recoIcons: Record<string, string> = {
  covoit: 'groups',
  elec: 'electric_car',
  elec_moto: 'electric_moped',
  elec_truck: 'local_shipping',
  inter: 'alt_route',
  inter_ma_tp: 'alt_route',
  inter_tim_tp: 'alt_route',
  marche: 'directions_walk',
  walking: 'directions_walk',
  tpu: 'directions_bus',
  pub: 'directions_bus',
  train: 'directions_railway',
  vae: 'electric_bike',
  velo: 'pedal_bike',
  bike: 'pedal_bike',
  cargo: 'directions_bike',
  boat: 'directions_boat',
  avoid: 'videocam',
}

/**
 * Get the icon for a given recommendation code, falling back to a generic one.
 */
export function getRecoIcon(reco: string): string {
  return recoIcons[reco] ?? 'commute'
}
