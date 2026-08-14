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