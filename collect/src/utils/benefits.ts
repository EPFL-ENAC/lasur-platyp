// @ts-expect-error works with qmarkdown
import VeloEnMd from 'src/assets/benefits/velo-en.md'
// @ts-expect-error works with qmarkdown
import VeloFrMd from 'src/assets/benefits/velo-fr.md'
// @ts-expect-error works with qmarkdown
import CovoitEnMd from 'src/assets/benefits/covoit-en.md'
// @ts-expect-error works with qmarkdown
import CovoitFrMd from 'src/assets/benefits/covoit-fr.md'
// @ts-expect-error works with qmarkdown
import ElecEnMd from 'src/assets/benefits/elec-en.md'
// @ts-expect-error works with qmarkdown
import ElecFrMd from 'src/assets/benefits/elec-fr.md'
// @ts-expect-error works with qmarkdown
import InterEnMd from 'src/assets/benefits/inter-en.md'
// @ts-expect-error works with qmarkdown
import InterFrMd from 'src/assets/benefits/inter-fr.md'
// @ts-expect-error works with qmarkdown
import MarcheEnMd from 'src/assets/benefits/marche-en.md'
// @ts-expect-error works with qmarkdown
import MarcheFrMd from 'src/assets/benefits/marche-fr.md'
// @ts-expect-error works with qmarkdown
import TpuEnMd from 'src/assets/benefits/tpu-en.md'
// @ts-expect-error works with qmarkdown
import TpuFrMd from 'src/assets/benefits/tpu-fr.md'
// @ts-expect-error works with qmarkdown
import TrainEnMd from 'src/assets/benefits/train-en.md'
// @ts-expect-error works with qmarkdown
import TrainFrMd from 'src/assets/benefits/train-fr.md'
// @ts-expect-error works with qmarkdown
import VaeEnMd from 'src/assets/benefits/vae-en.md'
// @ts-expect-error works with qmarkdown
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
