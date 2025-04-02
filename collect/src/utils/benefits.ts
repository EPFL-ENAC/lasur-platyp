import VeloEnMd from 'src/assets/benefits/velo-en.md'
import VeloFrMd from 'src/assets/benefits/velo-fr.md'
import CovoitEnMd from 'src/assets/benefits/covoit-en.md'
import CovoitFrMd from 'src/assets/benefits/covoit-fr.md'
import ElecEnMd from 'src/assets/benefits/elec-en.md'
import ElecFrMd from 'src/assets/benefits/elec-fr.md'
import InterEnMd from 'src/assets/benefits/inter-en.md'
import InterFrMd from 'src/assets/benefits/inter-fr.md'
import MarcheEnMd from 'src/assets/benefits/marche-en.md'
import MarcheFrMd from 'src/assets/benefits/marche-fr.md'
import TpuEnMd from 'src/assets/benefits/tpu-en.md'
import TpuFrMd from 'src/assets/benefits/tpu-fr.md'
import TrainEnMd from 'src/assets/benefits/train-en.md'
import TrainFrMd from 'src/assets/benefits/train-fr.md'
import VaeEnMd from 'src/assets/benefits/vae-en.md'
import VaeFrMd from 'src/assets/benefits/vae-fr.md'

export const benefits: { [key: string]: { en: string; fr: string } } = {
  velo: { en: VeloEnMd, fr: VeloFrMd },
  covoit: { en: CovoitEnMd, fr: CovoitFrMd },
  elec: { en: ElecEnMd, fr: ElecFrMd },
  inter: { en: InterEnMd, fr: InterFrMd },
  marche: { en: MarcheEnMd, fr: MarcheFrMd },
  tpu: { en: TpuEnMd, fr: TpuFrMd },
  train: { en: TrainEnMd, fr: TrainFrMd },
  vae: { en: VaeEnMd, fr: VaeFrMd },
}

export function hasBenefits(reco: string) {
  return reco in benefits
}

export function getBenefits(reco: string, locale: string) {
  const mds = benefits[reco]
  if (!mds) return ''
  return locale === 'fr' ? mds.fr : mds.en
}
