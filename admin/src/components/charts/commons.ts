import type { SetOptionOpts } from 'echarts'

export const initOptions: InitOptions = {
  renderer: 'svg',
}
export const updateOptions: SetOptionOpts = {
  notMerge: true,
}

/**
 * https://echarts.apache.org/en/api.html#echarts.init
 */
interface InitOptions {
  renderer: 'canvas' | 'svg'
}

export const MODE_COLORS: { [key: string]: string } = {
  car: '#860706',
  car_driver: '#860706',
  elec: '#E15956',
  elec_moto: '#E15956',
  covoit: '#F0988D',
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
  1: '#ff0000',
  2: '#ff8800',
  3: '#ffff00',
  4: '#aaff00',
  5: '#00c000',
}
