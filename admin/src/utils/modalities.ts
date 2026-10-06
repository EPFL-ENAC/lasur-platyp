/**
 * Modality labelling, mirroring the Python reference implementation in
 * mobility-toolkit `typo_modal/service.py` (`TypoModalService.compute_reco_inter`).
 *
 * A "raw modality" is a transport mode as recorded by the collect app. Home-work
 * journeys carry an ordered list of modes, the last one being the leg that ends
 * the journey; professional journeys carry a single mode drawn from a wider
 * vocabulary (cargo bike, truck, boat, plane). From a modality, two labels are
 * derived:
 *
 * - a *simple* label: the typology bucket ('MA', 'TP', 'TIM' and their
 *   intermodal combinations)
 * - a *complex* label: the detailed mode, or a '+'-joined intermodal pair
 *   ordered as travelled (the last leg comes last). The transit side of a pair
 *   is the merged 'tp' bucket, as the backend stats and the `complex_labels`
 *   translations have it — 'pub' and 'train' only stand on their own.
 *
 * The same simple typology is also derived from a recommendation — the
 * `reco_sim` mapping for commuting (`typo.reco.reco_inter` values) and its
 * professional counterpart (`typo.reco_pro` values), which share the mode
 * table below.
 */

/** The simple typology buckets, in reporting order. */
export const SIMPLE_LABELS = ['MA', 'TP', 'MA+TP', 'MA+TIM', 'TIM+TP', 'TIM'] as const

export type SimpleLabel = (typeof SIMPLE_LABELS)[number]

/** Whether a key is a simple typology label rather than a mode or an aggregate bucket. */
export function isSimpleLabel(key: string | null | undefined): key is SimpleLabel {
  return !!key && (SIMPLE_LABELS as readonly string[]).includes(key)
}

export interface ModalityLabels {
  simple: SimpleLabel
  complex: string
}

/**
 * Mode -> simple typology bucket, for raw modalities and recommendations alike.
 *
 * The vocabularies overlap and never disagree ('train' and 'cargo' appear in
 * both, with the same bucket), so one table covers them all:
 *
 * - commuting modes, mapped as in the Python (note that 'other' lands in 'MA')
 * - professional-only modes, which have no counterpart in the toolkit typology
 *   and are folded in by family: cargo bike with active mobility, truck with
 *   individual motorized transport, boat and plane with collective transport
 * - recommendation values: the French names of `compute_reco_pro` / `reco_sim`
 *   (marche, velo, vae, tpu, covoit, elec) and the two intermodal commuting
 *   recommendations. 'avoid' (do not travel) is not a mode and is absent.
 */
export const MODE_TO_SIMPLE_LABEL: Record<string, SimpleLabel> = {
  walking: 'MA',
  bike: 'MA',
  ebike: 'MA',
  other: 'MA',
  pub: 'TP',
  train: 'TP',
  moto: 'TIM',
  car: 'TIM',
  carpool: 'TIM',
  // professional travel only
  cargo: 'MA',
  truck: 'TIM',
  elec_truck: 'TIM',
  boat: 'TP',
  plane: 'TP',
  // recommendation values
  marche: 'MA',
  velo: 'MA',
  vae: 'MA',
  tpu: 'TP',
  covoit: 'TIM',
  elec: 'TIM',
  elec_moto: 'TIM',
  inter_ma_tp: 'MA+TP',
  inter_tim_tp: 'TIM+TP',
}

/**
 * Single raw mode -> complex label. Identity for every known mode: the raw
 * modality vocabulary is already the detailed label vocabulary.
 */
export const MODE_TO_COMPLEX_LABEL: Record<string, string> = {
  walking: 'walking',
  bike: 'bike',
  ebike: 'ebike',
  pub: 'pub',
  train: 'train',
  moto: 'moto',
  car: 'car',
  carpool: 'carpool',
  other: 'other',
  // professional travel only
  cargo: 'cargo',
  truck: 'truck',
  elec_truck: 'elec_truck',
  boat: 'boat',
  plane: 'plane',
}

/**
 * Mode families used by the intermodal rules: a journey is classified by which
 * families it mixes, not by the individual modes.
 *
 * Commuting vocabulary only, as in the Python: a professional journey carries a
 * single mode, so the freight and long-distance modes never reach these rules.
 */
const ACTIVE_MODES = ['bike', 'ebike']
const TRANSIT_MODES = ['pub', 'train']
const MOTORIZED_MODES = ['car', 'carpool', 'moto']

function hasAny(modes: string[], family: string[]): boolean {
  return modes.some((mode) => family.includes(mode))
}

/**
 * Order an intermodal complex label so that the leg ending the journey comes
 * last, as the Python code does by testing `modes[-1]`.
 */
function orderedPair(modes: string[], lastFamily: string[], a: string, b: string): string {
  const last = modes[modes.length - 1]
  return last !== undefined && lastFamily.includes(last) ? `${a}+${b}` : `${b}+${a}`
}

/**
 * Labels of a raw modality: an ordered list of modes for one journey.
 *
 * Single-mode journeys — every professional journey, and the commuting ones
 * made of a single leg — map through MODE_TO_SIMPLE_LABEL / MODE_TO_COMPLEX_LABEL.
 * Multi-mode journeys go through the intermodal rules, in the order the Python
 * implementation applies them (first match wins):
 *
 *   1. active + transit      -> 'MA+TP'   'tp+bike' | 'bike+tp'
 *   2. motorized + transit   -> 'TIM+TP'  'tp+car'  | 'car+tp'
 *   3. active + motorized    -> 'MA+TIM'  'car+bike' | 'bike+car'
 *   4. pub + train only      -> 'TP'      'tp'
 *   5. walking + transit     -> 'MA+TP'   'tp+walk' | 'walk+tp'
 *   6. anything else         -> 'MA+TIM'  'other_inter'
 *
 * Returns null for an empty or fully unknown single modality, so callers can
 * decide how to report it.
 */
export function getModalityLabels(modes: string[] | null | undefined): ModalityLabels | null {
  if (!modes || modes.length === 0) return null

  if (modes.length === 1) {
    const mode = modes[0] as string
    const simple = MODE_TO_SIMPLE_LABEL[mode]
    const complex = MODE_TO_COMPLEX_LABEL[mode]
    if (!simple || !complex) return null
    return { simple, complex }
  }

  const active = hasAny(modes, ACTIVE_MODES)
  const transit = hasAny(modes, TRANSIT_MODES)
  const motorized = hasAny(modes, MOTORIZED_MODES)

  if (active && transit) {
    return { simple: 'MA+TP', complex: orderedPair(modes, ACTIVE_MODES, 'tp', 'bike') }
  }
  if (motorized && transit) {
    return { simple: 'TIM+TP', complex: orderedPair(modes, MOTORIZED_MODES, 'tp', 'car') }
  }
  if (active && motorized) {
    return { simple: 'MA+TIM', complex: orderedPair(modes, ACTIVE_MODES, 'car', 'bike') }
  }
  if (modes.includes('pub') && modes.includes('train')) {
    return { simple: 'TP', complex: 'tp' }
  }
  if (modes.includes('walking') && transit) {
    return { simple: 'MA+TP', complex: orderedPair(modes, ['walking'], 'tp', 'walk') }
  }
  return { simple: 'MA+TIM', complex: 'other_inter' }
}

/**
 * Labels of a professional modality: the single mode of a professional journey.
 * Long-distance and freight modes keep their own complex label ('plane',
 * 'boat', 'truck', 'cargo') and are folded into the simple typology by family.
 */
export function getProModalityLabels(mode: string | null | undefined): ModalityLabels | null {
  if (!mode) return null
  return getModalityLabels([mode])
}

/**
 * Simple typology bucket of a recommendation, commuting (`reco_sim`) or
 * professional. Returns null for 'avoid' (do not travel), which is not a mode.
 */
export function getRecoSimpleLabel(reco: string | null | undefined): SimpleLabel | null {
  if (!reco) return null
  return MODE_TO_SIMPLE_LABEL[reco] ?? null
}
