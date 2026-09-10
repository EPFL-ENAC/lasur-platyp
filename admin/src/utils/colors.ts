import type { DataDrivenPropertyValueSpecification } from 'maplibre-gl'

export interface ColorStop {
  value: number
  color: string
}

export class GradientScale {
  private stops: ColorStop[]

  constructor(stops: ColorStop[]) {
    // Ensure stops are sorted by value ascending
    this.stops = [...stops].sort((a, b) => a.value - b.value)
  }

  /**
   * Returns the expression for MapLibre's 'fill-color' paint property
   */
  toMapLibreExpression(
    propertyName: string = 'value',
  ): DataDrivenPropertyValueSpecification<string> {
    const expression: DataDrivenPropertyValueSpecification<string> = [
      'interpolate',
      ['linear'],
      ['get', propertyName],
    ]

    this.stops.forEach((stop) => {
      expression.push(stop.value)
      expression.push(stop.color)
    })

    return expression
  }

  /**
   * Returns a CSS linear-gradient string (usually for a legend preview)
   * @param direction The direction of the gradient (e.g., 'to right' or 'to top')
   */
  toCSSGradient(direction: string = 'to right'): string {
    const min = this.stops[0]?.value || 0
    const max = this.stops[this.stops.length - 1]?.value || 100
    const range = max - min

    const cssStops = this.stops.map((stop) => {
      // Calculate percentage relative to the min/max values
      const percentage = range === 0 ? 0 : ((stop.value - min) / range) * 100
      return `${stop.color} ${percentage}%`
    })

    return `linear-gradient(${direction}, ${cssStops.join(', ')})`
  }

  getStops(): ColorStop[] {
    return this.stops
  }

  colorAt(value: number): string {
    const [r, g, b] = this.rgbAt(value)
    return `rgb(${r}, ${g}, ${b})`
  }

  /** Interpolated colour as an RGB tuple (e.g. for deck.gl accessors). */
  rgbAt(value: number): RGB {
    if (this.stops.length < 1) return [0, 0, 0] // Default to black if no stops

    // If value is below the first stop, return the first color
    if (value <= this.stops[0]!.value) return parseHex(this.stops[0]!.color)

    // If value is above the last stop, return the last color
    if (value >= this.stops[this.stops.length - 1]!.value)
      return parseHex(this.stops[this.stops.length - 1]!.color)

    // Find the two stops between which the value falls
    for (let i = 0; i < this.stops.length - 1; i++) {
      const stopA = this.stops[i]!
      const stopB = this.stops[i + 1]!

      if (value >= stopA.value && value <= stopB.value) {
        // Calculate the ratio of how far value is between stopA and stopB
        const ratio = (value - stopA.value) / (stopB.value - stopA.value)
        return interpolateRgb(parseHex(stopA.color), parseHex(stopB.color), ratio)
      }
    }

    return [0, 0, 0] // Fallback color
  }
}

export type RGB = [number, number, number]

function parseHex(hex: string): RGB {
  const bigint = parseInt(hex.replace('#', ''), 16)
  return [(bigint >> 16) & 255, (bigint >> 8) & 255, bigint & 255]
}

function interpolateRgb(a: RGB, b: RGB, ratio: number): RGB {
  return [
    Math.round(a[0] + (b[0] - a[0]) * ratio),
    Math.round(a[1] + (b[1] - a[1]) * ratio),
    Math.round(a[2] + (b[2] - a[2]) * ratio),
  ]
}
