import VeloEnMd from '@/assets/benefits/velo-en.md'
import VeloFrMd from '@/assets/benefits/velo-fr.md'
import CovoitEnMd from '@/assets/benefits/covoit-en.md'
import CovoitFrMd from '@/assets/benefits/covoit-fr.md'
import ElecEnMd from '@/assets/benefits/elec-en.md'
import ElecFrMd from '@/assets/benefits/elec-fr.md'
import InterEnMd from '@/assets/benefits/inter-en.md'
import InterFrMd from '@/assets/benefits/inter-fr.md'
import MarcheEnMd from '@/assets/benefits/marche-en.md'
import MarcheFrMd from '@/assets/benefits/marche-fr.md'
import TpuEnMd from '@/assets/benefits/tpu-en.md'
import TpuFrMd from '@/assets/benefits/tpu-fr.md'
import TrainEnMd from '@/assets/benefits/train-en.md'
import TrainFrMd from '@/assets/benefits/train-fr.md'
import VaeEnMd from '@/assets/benefits/vae-en.md'
import VaeFrMd from '@/assets/benefits/vae-fr.md'
import CargoEnMd from '@/assets/benefits/cargo-en.md'
import CargoFrMd from '@/assets/benefits/cargo-fr.md'

export const benefits: { [key: string]: { en: string; fr: string } } = {
  bike: { en: VeloEnMd, fr: VeloFrMd },
  velo: { en: VeloEnMd, fr: VeloFrMd },
  covoit: { en: CovoitEnMd, fr: CovoitFrMd },
  elec: { en: ElecEnMd, fr: ElecFrMd },
  inter: { en: InterEnMd, fr: InterFrMd },
  marche: { en: MarcheEnMd, fr: MarcheFrMd },
  tpu: { en: TpuEnMd, fr: TpuFrMd },
  train: { en: TrainEnMd, fr: TrainFrMd },
  vae: { en: VaeEnMd, fr: VaeFrMd },
  cargo: { en: CargoEnMd, fr: CargoFrMd },
}

export function hasBenefits(reco: string) {
  return reco in benefits
}

export function getBenefits(reco: string, locale: string) {
  const mds = benefits[reco]
  if (!mds) return ''
  return locale === 'fr' ? mds.fr : mds.en
}
