import { i18n } from '@/boot/i18n'

// Function to convert decimal degrees to DMS (Degrees, Minutes, Seconds)
export function toDMS(deg: number) {
  const d = Math.floor(deg)
  const minFloat = (deg - d) * 60
  const m = Math.floor(minFloat)
  const secFloat = (minFloat - m) * 60
  const s = Math.round(secFloat)

  return `${d}° ${m}' ${s}"`
}

// Function to convert decimal coordinates to a user-friendly format (DMS + N/S/E/W)
export function formatCoordinates(lat: number, lon: number) {
  const latDirection = lat >= 0 ? 'N' : 'S'
  const lonDirection = lon >= 0 ? 'E' : 'W'

  const latDMS = toDMS(Math.abs(lat)) // Get absolute value of latitude
  const lonDMS = toDMS(Math.abs(lon)) // Get absolute value of longitude

  return `${latDMS} ${latDirection}, ${lonDMS} ${lonDirection}`
}

// Follow the app locale, not the browser's: the user switches language in the
// UI, and the separators must switch with it. One formatter is kept per locale
// because building an Intl.NumberFormat is costly and the locale rarely changes.
const numberFormatters = new Map<string, Intl.NumberFormat>()

function numberFormatter(): Intl.NumberFormat {
  const locale = i18n.global.locale.value
  let formatter = numberFormatters.get(locale)
  if (!formatter) {
    formatter = new Intl.NumberFormat(locale, { maximumFractionDigits: 2 })
    numberFormatters.set(locale, formatter)
  }
  return formatter
}

export function formatNumber(value: number | null | undefined): string {
  if (value === null || value === undefined) {
    return 'N/A'
  }
  return numberFormatter().format(value)
}

// Significant digits rules, to be applied in all charts and texts:
// percentages are rounded to the unit, tCO2 to the tenth, kcal to the unit.

export function roundTo(value: number, decimals: number): number {
  const factor = 10 ** decimals
  // Avoid "-0" when a small negative value rounds to zero.
  return Math.round(value * factor) / factor || 0
}

/** Percentage value (without the % sign), rounded to the unit. */
export function formatPercent(value: number | null | undefined): string {
  return value === null || value === undefined ? 'N/A' : formatNumber(roundTo(value, 0))
}

/** Tons of CO2, rounded to the tenth. */
export function formatTons(value: number | null | undefined): string {
  return value === null || value === undefined ? 'N/A' : formatNumber(roundTo(value, 1))
}

/** Kilocalories, rounded to the unit. */
export function formatKcal(value: number | null | undefined): string {
  return value === null || value === undefined ? 'N/A' : formatNumber(roundTo(value, 0))
}

export function formatSignedPercent(value: number): string {
  const rounded = roundTo(value, 0)
  return `${rounded > 0 ? '+' : ''}${formatNumber(rounded)}%`
}

export function toMaxDecimals(x: number | null, n: number): number | null {
  if (x === null) {
    return null
  }
  return +x.toFixed(n)
}

export function checkUrlParamNumber(param: string | string[] | null | undefined): number | null {
  if (!param || Array.isArray(param)) {
    return null
  }
  const num = Number(param)
  return Number.isFinite(num) ? num : null
}
