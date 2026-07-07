import * as h3 from 'h3-js'
import type { BoundaryLevel, PlaceLocation } from 'src/models'

// H3 types are available directly from the package
type H3Index = h3.H3Index // This is actually a string

// Utility functions with proper H3 types
class H3Utils {
  /**
   * Backward compatibility: derive an approximate PlaceLocation from a legacy
   * H3 index (cell center + level from resolution), for records saved before
   * boundary-based location selection replaced the H3 grid. Resolutions used
   * by the former hex grid: 1 (world), 2 (europe), 5 (local/Swiss).
   */
  static toPlaceLocation(hexId: H3Index): PlaceLocation {
    const [lat, lon] = h3.cellToLatLng(hexId)
    const resolution = h3.getResolution(hexId)
    const level: BoundaryLevel =
      resolution <= 1 ? 'national' : resolution <= 4 ? 'regional' : 'local'
    return { lat, lon, level }
  }

  /**
   * Backward compatibility (write path): derive the H3 cell that most closely
   * corresponds to a PlaceLocation, so `hex_id` stays populated for consumers
   * that haven't migrated to `location` yet. Mirrors the resolutions used by
   * the former hex grid, kept in sync with `toPlaceLocation`.
   */
  static fromPlaceLocation(location: PlaceLocation): H3Index {
    const resolution = location.level === 'national' ? 1 : location.level === 'regional' ? 3 : 6
    return h3.latLngToCell(location.lat, location.lon, resolution)
  }
}
export { H3Utils, type H3Index }
