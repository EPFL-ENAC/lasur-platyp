import { registerTheme, type SetOptionOpts } from 'echarts'
import { getCssVar } from 'quasar'

export const initOptions: InitOptions = {
  renderer: 'svg',
}
export const updateOptions: SetOptionOpts = {
  notMerge: true,
}

registerTheme('platyp', {
  textStyle: {
    fontFamily: 'Nunito, sans-serif',
  },
  markLine: {
    lineStyle: {
      color: 'black', // Your default color
    },
    label: {
      color: 'black', // Matching the label color to the line
    },
  },
  color: [getCssVar('primary')],
})
registerTheme('platyp-dark', {
  textStyle: {
    fontFamily: 'Nunito, sans-serif',
    color: '#bca2b0',
  },
  title: {
    textStyle: {
      color: getCssVar('primary'),
    },
    subtextStyle: {
      color: '#bca2b0',
    },
  },
  legend: {
    textStyle: {
      color: '#fffcf4',
    },
  },
  label: {
    color: '#fffcf4',
    fill: '#fffcf4',
  },
  bar: {
    label: {
      color: '#fffcf4',
      fill: '#fffcf4',
    },
  },
  line: {
    label: {
      color: '#fffcf4',
      fill: '#fffcf4',
    },
  },
  markLine: {
    lineStyle: {
      color: getCssVar('primary'), // Your default color
    },
    label: {
      color: getCssVar('primary'), // Matching the label color to the line
    },
  },
  color: [getCssVar('primary')],
})

/**
 * https://echarts.apache.org/en/api.html#echarts.init
 */
interface InitOptions {
  renderer: 'canvas' | 'svg'
}

export const MODE_IDEAL_ORDER: Record<string, number> = {
  // Fallback order for unknown keys (keep them at the end)
  default: 999,
  // --- Active mobility ---
  walking: 10,
  walk: 10,
  marche: 10,
  bike: 20,
  velo: 20,
  ebike: 30,
  vae: 30,
  cargo: 40,
  // --- Public transport ---
  pub: 50,
  tpu: 50,
  transit: 50,
  upt_subs: 50,
  bus: 55,
  train: 60,
  rail: 60,
  train_subs: 60,
  pub_train: 65,
  // --- Private motorized ---
  carpool: 70,
  covoit: 70,
  car: 80,
  car_driver: 80,
  car_passenger: 81,
  car_moto: 85,
  elec: 90,
  ev: 90,
  moto: 95,
  elec_moto: 96,
  // --- Long distance / other ---
  truck: 110,
  elec_truck: 111,
  boat: 120,
  plane: 130,
  // --- Alternative / abstract ---
  avoid: 200,
  combined: 210,
  inter: 220,
  visio: 230,
  other: 900,
  unknown: 950,
}

export function modeSortOrder(key: string): number {
  return MODE_IDEAL_ORDER[key] || MODE_IDEAL_ORDER.default!
}

export const MODE_COLORS: { [key: string]: string } = {
  car: '#860706',
  car_driver: '#860706',
  elec: '#E15956',
  elec_moto: '#E15956',
  covoit: '#F0988D',
  carpool: '#F0988D',
  inter: '#AB8D74',
  moto: '#C00000',
  train: '#335E96',
  train_subs: '#335E96',
  pub: '#6093D3',
  tpu: '#6093D3',
  upt_subs: '#6093D3',
  cargo: '#325220',
  vae: '#4C7B31',
  ebike: '#4C7B31',
  bike: '#8ABA6F',
  velo: '#8ABA6F',
  walking: '#DEF1D3',
  marche: '#DEF1D3',
  plane: '#7030A0',
  boat: '#213D61',
  truck: '#842152',
  elec_truck: '#C2307A',
  visio: '#D1D1D1',
  default: '#ccc',
}

export const CATEGORY_COLORS: { [key: string]: string } = {
  collective: '#7030a0',
  finance: '#caad2e',
  environment: '#357165',
  flexibility: '#22cdf6',
  default: '#ccc',
}

export const MOTIVATION_COLORS: { [key: string]: string } = {
  1: '#f38989',
  2: '#f2b4a3',
  3: '#ffdbc2',
  4: '#c1cbb1',
  5: '#78c1a3',
}
