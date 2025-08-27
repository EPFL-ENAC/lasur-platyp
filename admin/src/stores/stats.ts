import type { Frequencies } from 'src/models'
import { api } from 'src/boot/api'

const authStore = useAuthStore()

export const useStats = defineStore('stats', () => {
  const equipments = ref<Frequencies>({} as Frequencies)
  const constraints = ref<Frequencies>({} as Frequencies)
  const loading = ref(false)

  async function loadStats() {
    loading.value = true
    return Promise.all([loadEquipments(), loadConstraints()]).finally(() => {
      loading.value = false
    })
  }

  async function loadEquipments() {
    equipments.value = { total: 0, data: [] }
    return authStore.updateToken().then(() => {
      const config = {
        headers: {
          Authorization: `Bearer ${authStore.accessToken}`,
        },
      }
      return api
        .get('/stats/equipments', config)
        .then((res) => {
          equipments.value = res.data
        })
        .catch(() => {
          equipments.value = { total: 0, data: [] }
        })
    })
  }

  async function loadConstraints() {
    constraints.value = { total: 0, data: [] }
    return authStore.updateToken().then(() => {
      const config = {
        headers: {
          Authorization: `Bearer ${authStore.accessToken}`,
        },
      }
      return api
        .get('/stats/constraints', config)
        .then((res) => {
          constraints.value = res.data
        })
        .catch(() => {
          constraints.value = { total: 0, data: [] }
        })
    })
  }

  return {
    equipments,
    constraints,
    loading,
    loadStats,
  }
})
