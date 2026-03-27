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
  car: '#7030a0',
  car_driver: '#7030a0',
  elec: '#7030a0',
  elec_moto: '#d86ecc',
  covoit: '#4f4f4f',
  inter: '#caad2e',
  moto: '#d86ecc',
  train: '#cfd6b9',
  train_subs: '#cfd6b9',
  pub: '#80a795',
  tpu: '#80a795',
  upt_subs: '#80a795',
  vae: '#357165',
  ebike: '#357165',
  bike: '#35a040',
  velo: '#35a040',
  walking: '#c7ff0a',
  marche: '#c7ff0a',
  plane: '#99001A',
  boat: '#22cdf6',
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

