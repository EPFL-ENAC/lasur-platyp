import type { Frequencies } from 'src/models'
import { api } from 'src/boot/api'

const authStore = useAuthStore()

export const useStats = defineStore('stats', () => {
  const frequencies = ref<{ [key: string]: Frequencies }>({} as { [key: string]: Frequencies })
  const loading = ref(false)

  async function loadStats() {
    loading.value = true
    return Promise.all([
      loadFrequencies('equipments'),
      loadFrequencies('constraints'),
      loadFrequencies('travel_time'),
    ]).finally(() => {
      loading.value = false
    })
  }

  async function loadFrequencies(field: string) {
    frequencies.value[field] = { total: 0, data: [] }
    return authStore.updateToken().then(() => {
      const config = {
        headers: {
          Authorization: `Bearer ${authStore.accessToken}`,
        },
      }
      return api
        .get(`/stats/${field}`, config)
        .then((res) => {
          frequencies.value[field] = res.data
        })
        .catch(() => {
          frequencies.value[field] = { total: 0, data: [] }
        })
    })
  }

  return {
    frequencies,
    loading,
    loadStats,
  }
})
