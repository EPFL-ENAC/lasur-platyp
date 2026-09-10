import { registerTheme, type SetOptionOpts } from 'echarts'
import { getCssVar } from 'quasar'
import type { InjectionKey, Ref } from 'vue'
import {
  recommendationLabels,
  recommendationToEquipmentMap,
  type BehaviorChangeByModeLever,
  type BehaviorChangeByModeMotivation,
  type EquipmentPerRecommendation,
  type EmissionReduction,
  type Emissions,
  type EquipmentRecommendationMatrix,
  type equipmentLabels,
  type Frequencies,
  type Frequency,
} from '@/models'
import {
  getProModalityLabels,
  getRecoSimpleLabel,
  MODE_TO_SIMPLE_LABEL,
} from '@/utils/modalities'

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

// Family ramps, light -> dark, in the same pastel register as MOTIVATION_COLORS.
// A single mode sits on its family ramp according to its impact; an intermodal
// trip takes the hue of the family of its LAST leg and its intensity from the
// impact of its FIRST leg (issue #413, option B). Intermodal shades nudge the
// hue a little (sage greens, steel blues, rosy reds) so they stay apart from the
// single modes at the same lightness. The darkest shades need a light label on
// top, see readableTextColor().
export const ACTIVE_RAMP = ['#dfeacc', '#a9cf8f', '#8fb87d', '#7fa66b']
export const TRANSIT_RAMP = ['#c5d8ea', '#99c7df', '#7a9cc4', '#6a88b0']
export const MOTORIZED_RAMP = [
  '#f1c4c4',
  '#f2b4a3',
  '#e39590',
  '#d98a7a',
  '#c96f6b',
  '#b86466',
  '#9a5a56',
]

export const MODE_COLORS: { [key: string]: string } = {
  car: '#c96f6b',
  car_driver: '#c96f6b',
  elec: '#e39590',
  elec_moto: '#e39590',
  covoit: '#f2b4a3',
  carpool: '#f2b4a3',
  inter: '#c9b39c',
  moto: '#d98a7a',
  train: '#7a9cc4',
  train_demi_tarif: '#7a9cc4',
  train_abo_gen: '#7a9cc4',
  pub: '#99c7df',
  tpu: '#99c7df',
  tpu_unireso: '#99c7df',
  tpu_leman_pass: '#99c7df',
  cargo: '#7fa66b',
  vae: '#8fb87d',
  ebike: '#8fb87d',
  bike: '#a9cf8f',
  velo: '#a9cf8f',
  walking: '#dfeacc',
  marche: '#dfeacc',
  plane: '#9a5a56',
  boat: '#8aa3bf',
  truck: '#cf8fb0',
  elec_truck: '#d9a3c2',
  visio: '#b5b3ad',
  // Intermodal recommendations: same rule as the typology labels below
  // (active -> transit, motorized -> transit).
  inter_ma_tp: '#8fabd0',
  inter_tim_tp: '#6a88b0',
  default: '#d6d6d6',
}

// Muted palette with the same feel as the motivation scale below: warm,
// desaturated tones that keep the inside labels readable in dark text.
export const CATEGORY_COLORS: { [key: string]: string } = {
  collective: '#bfaad9',
  finance: '#e3cd72',
  environment: '#c0cca2',
  flexibility: '#99c7df',
  test: '#f38989',
  coaching: '#f2b4a3',
  events: '#ffdbc2',
  company_vehicle: '#78c1a3',
  default: '#d6d6d6',
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

// The intermodal buckets are undirected: 'MA+TP' is read as MA first, TP last.
export const SIMPLE_LABELS_COLORS: { [key: string]: string } = {
  MA: '#a9cf8f',
  TP: '#99c7df',
  'MA+TP': '#8fabd0',
  'MA+TIM': '#f1c4c4',
  'TIM+TP': '#6a88b0',
  TIM: '#c96f6b',
  default: '#d6d6d6',
}

/**
 * Modal split of the Geneva canton population, in % of the main mode used
 * (Microrecensement Mobilité et Transports, 2023). Keys are complex labels: the
 * MRMT reports public transport as a whole, which is the merged 'tp' bucket, and
 * has no intermodal category, so the intermodal labels have no reference value.
 */
export const MRMT_COMPLEX_MODAL_SPLIT_PERCENT: Record<string, number> = {
  walking: 9.5,
  bike: 23.8,
  tp: 26.6,
  moto: 9.9,
  car: 30.3,
}

/** The same figures folded into the simple typology buckets. */
export const MRMT_SIMPLE_MODAL_SPLIT_PERCENT: Record<string, number> = Object.entries(
  MRMT_COMPLEX_MODAL_SPLIT_PERCENT,
).reduce<Record<string, number>>((acc, [label, percent]) => {
  // 'tp' is a complex label only: it is absent from the raw mode table.
  const simple = label === 'tp' ? 'TP' : MODE_TO_SIMPLE_LABEL[label]
  if (simple) {
    acc[simple] = Number(((acc[simple] ?? 0) + percent).toFixed(1))
  }
  return acc
}, {})

/** Complex label -> the recommendation value standing for the same mode. */
const COMPLEX_LABEL_TO_RECO_MODE: Record<string, string> = {
  walking: 'marche',
  bike: 'velo',
  ebike: 'vae',
  tp: 'tpu',
  pub: 'tpu',
  carpool: 'covoit',
}

/**
 * The same figures in the mode vocabulary of the recommendation charts, whose
 * keys are `reco_inter` values: the MRMT modes that a recommendation can be
 * made of are renamed ('walking' -> 'marche'...), the merged 'tp' bucket maps to
 * 'tpu', and the modes no recommendation uses (car, motorcycle) keep their own
 * key, as they still have a label and a color.
 */
export const MRMT_MODE_MODAL_SPLIT_PERCENT: Record<string, number> = Object.entries(
  MRMT_COMPLEX_MODAL_SPLIT_PERCENT,
).reduce<Record<string, number>>((acc, [label, percent]) => {
  const mode = COMPLEX_LABEL_TO_RECO_MODE[label] ?? label
  acc[mode] = Number(((acc[mode] ?? 0) + percent).toFixed(1))
  return acc
}, {})

export const COMPLEX_LABELS_IDEAL_ORDER: Record<string, number> = {
  // Fallback order for unknown keys (keep them at the end)
  default: 999,
  walking: 10,
  bike: 20,
  ebike: 30,
  pub: 40,
  tp: 40,
  train: 50,
  moto: 60,
  car: 70,
  carpool: 80,
  other: 90,
  'pub+bike': 100,
  'bike+pub': 100,
  'tp+bike': 100,
  'bike+tp': 100,
  'pub+car': 110,
  'car+pub': 110,
  'tp+car': 110,
  'car+tp': 110,
  'car+bike': 120,
  'bike+car': 120,
  'pub+walk': 130,
  'walk+pub': 130,
  'tp+walk': 130,
  'walk+tp': 130,
  other_inter: 140,
}

export function complexLabelSortOrder(key: string): number {
  return COMPLEX_LABELS_IDEAL_ORDER[key] || COMPLEX_LABELS_IDEAL_ORDER.default!
}

// Used to distinguish comparison groups (Main Group + up to 4 "compare with" groups) when
// groups, rather than modes, are the dimension being colored.
export const GROUP_COLORS = ['#8fb87d', '#c96f6b', '#99c7df', '#e3cd72', '#bfaad9']

// Intermodal keys are 'first+last' (see getModalityLabels): hue of the last
// leg's family, intensity from the first leg. The legacy 'pub' keys mirror
// their merged 'tp' twin.
export const COMPLEX_LABELS_COLORS: { [key: string]: string } = {
  walking: '#dfeacc',
  bike: '#a9cf8f',
  ebike: '#8fb87d',
  pub: '#99c7df',
  tp: '#99c7df',
  train: '#7a9cc4',
  moto: '#d98a7a',
  car: '#c96f6b',
  carpool: '#f2b4a3',
  other: '#c9b39c',
  // transit -> bike: green, transit intensity
  'pub+bike': '#9ccaa8',
  'tp+bike': '#9ccaa8',
  // bike -> transit: blue, active intensity
  'bike+pub': '#8fabd0',
  'bike+tp': '#8fabd0',
  // transit -> car: red, transit intensity
  'pub+car': '#b86466',
  'tp+car': '#b86466',
  // car -> transit: blue, motorized intensity
  'car+pub': '#6a88b0',
  'car+tp': '#6a88b0',
  // car -> bike: green, motorized intensity
  'car+bike': '#78a98a',
  // bike -> car: red, active intensity
  'bike+car': '#f1c4c4',
  // transit -> walking: green, lighter than transit -> bike
  'pub+walk': '#c9e2cf',
  'tp+walk': '#c9e2cf',
  // walking -> transit: blue, lightest intensity
  'walk+pub': '#c5d8ea',
  'walk+tp': '#c5d8ea',
  other_inter: '#c9b39c',
  default: '#d6d6d6',
}

/**
 * Black or white, whichever reads better on the given hex background: the
 * darker ramp shades need a light label on top.
 */
export function readableTextColor(hex: string): '#000' | '#fff' {
  const match = /^#?([0-9a-f]{6})$/i.exec(hex.trim())
  if (!match) return '#000'
  const [r, g, b] = [0, 2, 4].map((i) => parseInt(match[1]!.slice(i, i + 2), 16) / 255)
  const channel = (c: number) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4)
  const luminance = 0.2126 * channel(r!) + 0.7152 * channel(g!) + 0.0722 * channel(b!)
  return luminance > 0.179 ? '#000' : '#fff'
}

/**
 * Compute rounded percentages that sum to exactly 100 using largest-remainder
 * method. Each returned item carries a `percent` field alongside its original
 * properties.
 */
export function computePercentages<T extends { value: number }>(
  items: T[],
): (T & { percent: number })[] {
  const total = items.reduce((sum, item) => sum + item.value, 0)
  if (total === 0) {
    return items.map((item) => ({ ...item, percent: 0 }))
  }

  const raw = items.map((item) => {
    const pct = (item.value / total) * 100
    return {
      ...item,
      floor: Math.floor(pct),
      frac: pct - Math.floor(pct),
    }
  })

  const sumFloored = raw.reduce((sum, item) => sum + item.floor, 0)
  let surplus = 100 - sumFloored

  // Distribute surplus to items with largest fractional parts
  const sorted = raw.map((item, idx) => ({ ...item, idx })).sort((a, b) => b.frac - a.frac)

  const percents = raw.map((item) => item.floor)
  for (const item of sorted) {
    if (surplus <= 0) break
    percents[item.idx] = (percents[item.idx] ?? 0) + 1
    surplus -= 1
  }

  return items.map((item, idx) => ({ ...item, percent: percents[idx] ?? 0 }))
}

/**
 * Recategorise behaviour-change stats from recommended modes to simple typology
 * labels: 'velo' and 'marche' both become 'MA', 'tpu' and 'train' become 'TP',
 * and so on.
 *
 * Entries whose mode is not a recommendation — the 'Total', 'allModes' and
 * 'Autres' aggregate buckets the backend adds — are left untouched: they
 * already span several modes and folding them into a label would double count.
 *
 * Counts are summed. Percentages are recomputed over `denominatorOf`, and only
 * for rows that actually merged, so that a row coming from a single mode keeps
 * the percentages the backend computed for it.
 */
function aggregateByModeSimpleLabel<E extends { count: number; percentage: number }>(
  byMode: ModeBucket<E>[],
  keyOf: (entry: E) => string | number,
  denominatorOf: (responseCount: number, entries: E[]) => number,
): ModeBucket<E>[] {
  const merged = new Map<string, { bucket: ModeBucket<E>; sources: number }>()

  byMode.forEach((item) => {
    const mode = getRecoSimpleLabel(item.mode) ?? item.mode
    const target = merged.get(mode)
    if (!target) {
      merged.set(mode, {
        bucket: { ...item, mode, entries: item.entries.map((entry) => ({ ...entry })) },
        sources: 1,
      })
      return
    }
    target.sources += 1
    target.bucket.response_count += item.response_count
    item.entries.forEach((entry) => {
      const known = target.bucket.entries.find((e) => keyOf(e) === keyOf(entry))
      if (known) {
        known.count += entry.count
      } else {
        target.bucket.entries.push({ ...entry })
      }
    })
  })

  return Array.from(merged.values())
    .map(({ bucket, sources }) => {
      if (sources === 1) {
        return bucket
      }
      const total = denominatorOf(bucket.response_count, bucket.entries)
      return {
        ...bucket,
        entries: bucket.entries.map((entry) => ({
          ...entry,
          percentage: total > 0 ? Math.round((entry.count / total) * 10000) / 100 : 0,
        })),
      }
    })
    .sort((a, b) => simpleLabelSortOrder(a.mode) - simpleLabelSortOrder(b.mode))
}

interface ModeBucket<E> {
  mode: string
  response_count: number
  entries: E[]
}

/**
 * Lever stats by simple typology label. Lever percentages are shares of all the
 * lever selections of the group, the denominator the backend uses.
 */
export function aggregateLeversBySimpleLabel(
  byMode: BehaviorChangeByModeLever[],
): BehaviorChangeByModeLever[] {
  return aggregateByModeSimpleLabel(
    byMode.map(({ levers, ...item }) => ({ ...item, entries: levers })),
    (lever) => lever.category,
    (_responseCount, entries) => entries.reduce((sum, entry) => sum + entry.count, 0),
  ).map(({ entries, ...bucket }) => ({ ...bucket, levers: entries }))
}

/**
 * Motivation stats by simple typology label. Motivation percentages are shares
 * of the people who answered the question, the denominator the backend uses.
 */
export function aggregateMotivationBySimpleLabel(
  byMode: BehaviorChangeByModeMotivation[],
): BehaviorChangeByModeMotivation[] {
  return aggregateByModeSimpleLabel(
    byMode.map(({ motivations, ...item }) => ({ ...item, entries: motivations })),
    (motivation) => motivation.level,
    (responseCount) => responseCount,
  ).map(({ entries, ...bucket }) => ({ ...bucket, motivations: entries }))
}

/**
 * Equipment matrix rows recategorised from recommendations to simple typology
 * labels: 'marche', 'velo', 'vae' and 'cargo' all become 'MA', and so on.
 * Counts are summed field by field, `total` included — a row total counts
 * recommendation instances, so summing gives the instances of the bucket.
 *
 * 'inter' has no simple label of its own (the typology splits intermodality
 * into 'MA+TP' and 'TIM+TP') and stays a row of its own.
 */
export function aggregateEquipmentMatrixBySimpleLabel(
  matrix: EquipmentRecommendationMatrix,
): Record<string, EquipmentPerRecommendation> {
  const merged: Record<string, EquipmentPerRecommendation> = {}

  recommendationLabels.forEach((reco) => {
    const label = getRecoSimpleLabel(reco) ?? reco
    const row = matrix[reco]
    const target = merged[label]
    if (!target) {
      merged[label] = { ...row }
      return
    }
    ;(Object.keys(target) as (keyof EquipmentPerRecommendation)[]).forEach((field) => {
      target[field] += row[field]
    })
  })

  return merged
}

/**
 * The equipments that match each row of {@link aggregateEquipmentMatrixBySimpleLabel}:
 * the union of the equipments of the recommendations folded into that label.
 */
export function aggregateRecommendationEquipmentsBySimpleLabel(): Record<
  string,
  (typeof equipmentLabels)[number][] | null
> {
  const merged: Record<string, (typeof equipmentLabels)[number][] | null> = {}

  recommendationLabels.forEach((reco) => {
    const label = getRecoSimpleLabel(reco) ?? reco
    const equipments = recommendationToEquipmentMap[reco]
    if (!equipments) {
      return
    }
    merged[label] = Array.from(new Set([...(merged[label] ?? []), ...equipments]))
  })

  return merged
}

/**
 * Frequencies recategorised from recommendations to simple typology labels,
 * for the data the backend only ships in detailed form (professional
 * recommendations). Counts are summed; a value with no simple label — 'avoid'
 * (do not travel) — stays an entry of its own.
 */
export function aggregateFrequenciesBySimpleLabel(frequencies: Frequencies): Frequencies {
  const merged = new Map<string, Frequency>()

  frequencies.data.forEach((item) => {
    const value = getRecoSimpleLabel(item.value) ?? item.value
    const known = merged.get(value)
    if (!known) {
      merged.set(value, { ...item, value })
      return
    }
    // `sum`, when the backend sets it, is what the charts plot instead of the
    // count, so it accumulates the same way — falling back to the count for
    // the entries that carry none. Computed before `count` moves.
    if (known.sum !== undefined || item.sum !== undefined) {
      known.sum = (known.sum ?? known.count) + (item.sum ?? item.count)
    }
    known.count += item.count
  })

  return { ...frequencies, data: Array.from(merged.values()) }
}

/**
 * Emission reductions recategorised from recommended modes to simple typology
 * labels. Reductions are summed; `total` is the number of records the backend
 * computed them over, identical on every row, so it is carried over as is. A
 * mode with no simple label — 'avoid' (do not travel) — stays a row of its own.
 */
export function aggregateReductionsBySimpleLabel(
  reductions: EmissionReduction[],
): EmissionReduction[] {
  const merged = new Map<string, EmissionReduction>()

  reductions.forEach((item) => {
    const mode = getRecoSimpleLabel(item.mode) ?? item.mode
    const known = merged.get(mode)
    if (!known) {
      merged.set(mode, { ...item, mode })
      return
    }
    known.reduced += item.reduced
    known.total = Math.max(known.total, item.total)
  })

  return Array.from(merged.values())
}

/**
 * Emissions recategorised from professional transport modes to simple typology
 * labels. Journeys, distances and emissions are summed; `total` is the number
 * of records the backend computed them over, identical on every row, so it is
 * carried over as is. A mode with no simple label stays a row of its own.
 */
export function aggregateEmissionsBySimpleLabel(emissions: Emissions[]): Emissions[] {
  const merged = new Map<string, Emissions>()

  emissions.forEach((item) => {
    const mode = getProModalityLabels(item.mode)?.simple ?? item.mode
    const known = merged.get(mode)
    if (!known) {
      merged.set(mode, { ...item, mode })
      return
    }
    known.distances += item.distances
    known.journeys += item.journeys
    known.emissions += item.emissions
    known.total = Math.max(known.total, item.total)
  })

  return Array.from(merged.values())
}
