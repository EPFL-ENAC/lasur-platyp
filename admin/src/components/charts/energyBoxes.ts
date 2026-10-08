import type { EnergyBoxSample } from '@/models'

/** A journey has a per-journey recommendation when its real reco mode is set;
 * its potential daily kcal falls back to current when it has none. */
export function boxRecoKcal(sample: EnergyBoxSample): number {
  return sample.reco_kcal ?? sample.current_kcal
}

/** The key a sample is grouped by in one (chart, modal split) combination. */
export type BoxKeyField = 'current_simple' | 'current_complex' | 'reco_simple' | 'reco_mode'

/**
 * Distinct key values in the samples, ordered: the spec's split rule puts
 * every mode with n >= SPLIT_THRESHOLD in its own pair, pools the modes below
 * it in one 'Autres' pair, and 'Total' is always present, first.
 */
export const BOX_SPLIT_THRESHOLD = 10

/** A sample counts for mode M in the reco chart when it is recommended M:
 * one sample per (token, journey) recommendation instance. */
export function boxKeyCounts(samples: EnergyBoxSample[], keyField: BoxKeyField): Map<string, number> {
  const counts = new Map<string, number>()
  samples.forEach((sample) => {
    const key = sample[keyField]
    if (key == null) return
    counts.set(key, (counts.get(key) ?? 0) + 1)
  })
  return counts
}

/**
 * The groups of the boxplot chart: 'Total' always first, then the modes
 * reaching the threshold (ordered by the spec's mode order), then 'Autres'
 * pooling the modes below it — omitted when every mode is separate (or when
 * there are no small modes at all).
 */
export function boxGroups(
  samples: EnergyBoxSample[],
  keyField: BoxKeyField,
  keyOrder: (key: string) => number,
): { key: string; label: string; samples: EnergyBoxSample[] }[] {
  const counts = boxKeyCounts(samples, keyField)
  const keys = Array.from(counts.keys())
  if (keys.length === 0) {
    return []
  }

  const separate = keys
    .filter((key) => counts.get(key)! >= BOX_SPLIT_THRESHOLD)
    .sort((a, b) => keyOrder(a) - keyOrder(b))
  const pooled = keys.filter((key) => counts.get(key)! < BOX_SPLIT_THRESHOLD)

  const groups: { key: string; label: string; samples: EnergyBoxSample[] }[] = [
    { key: 'total', label: 'total', samples },
  ]
  separate.forEach((key) => {
    groups.push({
      key,
      label: key,
      samples: samples.filter((sample) => sample[keyField] === key),
    })
  })
  if (pooled.length > 0) {
    groups.push({
      key: 'autres',
      label: 'autres',
      samples: samples.filter((sample) => {
        const key = sample[keyField]
        return key != null && counts.get(key)! < BOX_SPLIT_THRESHOLD
      }),
    })
  }
  return groups
}

/** Charted order of the group keys: 'total' first, then the modes, 'autres' last. */
export function boxGroupOrder(key: string, keyOrder: (key: string) => number): number {
  if (key === 'total') return -1
  if (key === 'autres') return 999
  return keyOrder(key)
}

/** Sort group keys for the x axis: total, separate modes by keyOrder, autres. */
export function sortBoxGroups(
  groups: { key: string; label: string; samples: EnergyBoxSample[] }[],
  keyOrder: (key: string) => number,
): { key: string; label: string; samples: EnergyBoxSample[] }[] {
  return [...groups].sort(
    (a, b) => boxGroupOrder(a.key, keyOrder) - boxGroupOrder(b.key, keyOrder),
  )
}

/** The chart's key ordering per (chart, modal split), matching the bar charts. */
export function boxKeyOrderFactory(
  modeOrder: (key: string) => number,
  simpleLabelOrder: (key: string) => number,
  complexLabelOrder: (key: string) => number,
): (keyField: BoxKeyField) => (key: string) => number {
  return (keyField: BoxKeyField) => {
    if (keyField === 'current_simple' || keyField === 'reco_simple') {
      return simpleLabelOrder
    }
    if (keyField === 'current_complex') {
      return complexLabelOrder
    }
    return modeOrder
  }
}
