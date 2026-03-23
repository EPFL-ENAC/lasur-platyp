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
    if (this.stops.length < 1) return '#000000' // Default to black if no stops

    // If value is below the first stop, return the first color
    if (value <= this.stops[0]!.value) return this.stops[0]!.color

    // If value is above the last stop, return the last color
    if (value >= this.stops[this.stops.length - 1]!.value)
      return this.stops[this.stops.length - 1]!.color

    // Find the two stops between which the value falls
    for (let i = 0; i < this.stops.length - 1; i++) {
      const stopA = this.stops[i]!
      const stopB = this.stops[i + 1]!

      if (value >= stopA.value && value <= stopB.value) {
        // Calculate the ratio of how far value is between stopA and stopB
        const ratio = (value - stopA.value) / (stopB.value - stopA.value)
        return this.interpolateColor(stopA.color, stopB.color, ratio)
      }
    }

    return '#000000' // Fallback color
  }

  private interpolateColor(colorA: string, colorB: string, ratio: number): string {
    const parseHex = (hex: string) => {
      const bigint = parseInt(hex.replace('#', ''), 16)
      return [(bigint >> 16) & 255, (bigint >> 8) & 255, bigint & 255]
    }

    const [rA, gA, bA] = parseHex(colorA)
    const [rB, gB, bB] = parseHex(colorB)

    const r = Math.round(rA! + (rB! - rA!) * ratio)
    const g = Math.round(gA! + (gB! - gA!) * ratio)
    const b = Math.round(bA! + (bB! - bA!) * ratio)

    return `rgb(${r}, ${g}, ${b})`
  }
}
