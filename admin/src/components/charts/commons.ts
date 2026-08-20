import { registerTheme, type SetOptionOpts } from 'echarts'
import { getCssVar } from 'quasar'
import type { InjectionKey, Ref } from 'vue'

export const chartPanelDialogOpenKey: InjectionKey<Ref<boolean>> = Symbol('chartPanelDialogOpen')

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
  tpu_unireso: 50,
  tpu_leman_pass: 50,
  bus: 55,
  train: 60,
  rail: 60,
  train_demi_tarif: 60,
  train_abo_gen: 60,
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
  train_demi_tarif: '#335E96',
  train_abo_gen: '#335E96',
  pub: '#6093D3',
  tpu: '#6093D3',
  tpu_unireso: '#6093D3',
  tpu_leman_pass: '#6093D3',
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
  inter_ma_tp: '#D2F08D',
  inter_tim_tp: '#C50B07',
  default: '#ccc',
}

export const CATEGORY_COLORS: { [key: string]: string } = {
  collective: '#7030a0',
  finance: '#caad2e',
  environment: '#357165',
  flexibility: '#22cdf6',
  test: '#f38989',
  coaching: '#f2b4a3',
  events: '#ffdbc2',
  company_vehicle: '#78c1a3',
  default: '#ccc',
}

export const MOTIVATION_COLORS: { [key: string]: string } = {
  1: '#f38989',
  2: '#f2b4a3',
  3: '#ffdbc2',
  4: '#c1cbb1',
  5: '#78c1a3',
}

export const SIMPLE_LABELS_IDEAL_ORDER: Record<string, number> = {
  // Fallback order for unknown keys (keep them at the end)
  default: 999,
  MA: 10,
  TP: 20,
  'MA+TP': 30,
  'MA+TIM': 40,
  'TIM+TP': 50,
  TIM: 60,
}

export function simpleLabelSortOrder(key: string): number {
  return SIMPLE_LABELS_IDEAL_ORDER[key] || SIMPLE_LABELS_IDEAL_ORDER.default!
}

export const SIMPLE_LABELS_COLORS: { [key: string]: string } = {
  MA: '#8ABA6F',
  TP: '#6093D3',
  'MA+TP': '#4C7B31',
  'MA+TIM': '#F0988D',
  'TIM+TP': '#E15956',
  TIM: '#860706',
  default: '#ccc',
}

export const COMPLEX_LABELS_IDEAL_ORDER: Record<string, number> = {
  // Fallback order for unknown keys (keep them at the end)
  default: 999,
  walking: 10,
  bike: 20,
  ebike: 30,
  pub: 40,
  train: 50,
  moto: 60,
  car: 70,
  carpool: 80,
  other: 90,
  'pub+bike': 100,
  'bike+pub': 100,
  'pub+car': 110,
  'car+pub': 110,
  'car+bike': 120,
  'bike+car': 120,
  'pub+walk': 130,
  'walk+pub': 130,
  other_inter: 140,
}

export function complexLabelSortOrder(key: string): number {
  return COMPLEX_LABELS_IDEAL_ORDER[key] || COMPLEX_LABELS_IDEAL_ORDER.default!
}

// Used to distinguish comparison groups (Main Group + up to 4 "compare with" groups) when
// groups, rather than modes, are the dimension being colored.
export const GROUP_COLORS = ['#4C7B31', '#860706', '#6093D3', '#caad2e', '#7030A0']

export const COMPLEX_LABELS_COLORS: { [key: string]: string } = {
  walking: '#DEF1D3',
  bike: '#8ABA6F',
  ebike: '#4C7B31',
  pub: '#6093D3',
  train: '#335E96',
  moto: '#C00000',
  car: '#860706',
  carpool: '#F0988D',
  other: '#AB8D74',
  'pub+bike': '#4C7B31',
  'bike+pub': '#4C7B31',
  'pub+car': '#E15956',
  'car+pub': '#E15956',
  'car+bike': '#F0988D',
  'bike+car': '#F0988D',
  'pub+walk': '#DEF1D3',
  'walk+pub': '#DEF1D3',
  other_inter: '#AB8D74',
  default: '#ccc',
}
