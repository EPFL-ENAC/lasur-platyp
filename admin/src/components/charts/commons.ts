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
  car: '#7030A0',
  car_driver: '#7030A0',
  elec: '#7030A0',
  covoit: '#4f4f4f',
  inter: '#caad2e',
  moto: '#D86ECC',
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
  default: '#ccc',
}
