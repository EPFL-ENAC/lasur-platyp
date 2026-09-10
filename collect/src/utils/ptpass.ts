/**
 * Public transport pass suggested alongside a recommendation, as provided by the
 * modal typology toolkit (reco.pt_pass) for the home-to-work origin/destination.
 */

// Recommendations that rely on public transport, and so may call for a pass.
const ptRecos = ['tpu', 'pub', 'train', 'inter', 'inter_ma_tp', 'inter_tim_tp']

// Passes the toolkit knows about; anything else falls back to a generic wording.
const ptPasses = ['unireso', 'leman', 'cff', 'sncf']

export function isPtReco(reco: string) {
  return ptRecos.includes(reco)
}

export function getPtPassKey(ptPass: string | undefined) {
  return ptPass && ptPasses.includes(ptPass) ? ptPass : 'other'
}
