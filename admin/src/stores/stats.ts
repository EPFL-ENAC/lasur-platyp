import type { Frequencies } from 'src/models'
import { api } from 'src/boot/api'

const authStore = useAuthStore()

export const useStats = defineStore('stats', () => {
  const equipments = ref<Frequencies>({} as Frequencies)
  const loading = ref(false)

  async function loadEquipments() {
    equipments.value = { total: 0, data: [] }
    loading.value = true
    return authStore
      .updateToken()
      .then(() => {
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
      .finally(() => {
        loading.value = false
      })
  }

  return {
    equipments,
    loading,
    loadEquipments,
  }
})
