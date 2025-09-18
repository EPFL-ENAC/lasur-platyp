import { api } from 'src/boot/api'
import type { IsochronesParams, IsochronesData } from 'src/models'

const authStore = useAuthStore()

export const CATEGORY_TAGS = {
  food: {
    amenity: ['restaurant', 'cafe', 'fast_food', 'food_court'],
    shop: ['supermarket', 'convenience', 'bakery', 'butcher', 'pastry'],
  },
  education: {
    amenity: [
      'school',
      'library',
      'university',
      'college',
      'public_bookcase',
      'waste_disposal',
      'toy_library',
      'childcare',
      'library_dropoff',
      'prep_school',
    ],
  },
  service: {
    amenity: [
      'post_box',
      'bank',
      'post_office',
      'police',
      'townhall',
      'public_building',
      'public_bath',
    ],
    office: ['coworking', 'administrative'],
    shop: ['dry_cleaning', 'laundry', 'copyshop'],
  },
  health: {
    amenity: ['pharmacy', 'doctors', 'hospital', 'dentist', 'clinic', 'veterinary'],
    healthcare: [
      'pharmacy',
      'doctor',
      'alternative',
      'physiotherapist',
      'hospital',
      'dentist',
      'clinic',
      'laboratory',
      'podiatrist',
      'psychotherapist',
      'centre',
      'audiologist',
      'birthing_centre',
      'blood_donation',
      'optometrist',
      'psychomotricist',
    ],
  },
  leisure: {
    amenity: [
      'bar',
      'community_centre',
      'theatre',
      'social_facility',
      'pub',
      'bbq',
      'nightclub',
      'cinema',
      'music_school',
      'arts_centre',
      'events_venue',
      'social_centre',
      'exhibition_centre',
      'concert_hall',
      'biergarten',
    ],
    shop: ['art'],
    tourism: [
      'artwork',
      'hotel',
      'information',
      'attraction',
      'museum',
      'viewpoint',
      'gallery',
      'zoo',
      'picnic_site',
      'theme_park',
      'camp_site',
      'chalet',
      'motel',
    ],
  },
  transport: {
    amenity: [
      'car_sharing',
      'car_rental',
      'charging_station',
      'ferry_terminal',
      'bicycle_rental',
      'bicycle_repair_station',
      'bus_station',
    ],
    public_transport: ['stop_position', 'platform', 'station'],
  },
  commerce: {
    amenity: ['marketplace'],
    shop: [
      'clothes',
      'kiosk',
      'bicycle',
      'department_store',
      'shoes',
      'books',
      'florist',
      'sports',
      'mall',
      'coffee',
      'second_hand',
      'tea',
      'grocery',
    ],
  },
}

export const useIsochrones = defineStore('isochrones', () => {
  function computeIsochrones(payload: IsochronesParams) {
    return authStore.updateToken().then(() => {
      const config = {
        headers: {
          Authorization: `Bearer ${authStore.accessToken}`,
        },
      }
      return api
        .post('/isochrones/_compute', payload, config)
        .then((res) => {
          return res.data as IsochronesData
        })
        .catch(() => {
          return undefined
        })
    })
  }

  function findCategory(tag: string, value: string) {
    for (const [category, tags] of Object.entries(CATEGORY_TAGS)) {
      if (tags[tag as keyof typeof tags]?.includes(value)) {
        return category
      }
    }
    return 'other'
  }

  return { computeIsochrones, findCategory }
})
