import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from 'src/boot/api'
import type { Record } from 'src/models'

export const useCollector = defineStore('collector', () => {
  const token = ref<string | null>(null)
  const loading = ref<boolean>(false)

  async function load(tkOrSlug: string): Promise<Record> {
    token.value = null
    loading.value = true
    return api
      .get(`/collect/record/${tkOrSlug}`)
      .then((response) => {
        token.value = tkOrSlug
        const cr = response.data
        const data = {
          employment_rate: 100,
          remote_work_rate: 40,
          company_vehicle: false,
          travel_time: 0,
          equipments: [],
          constraints: [],
          freq_mod_walking: 0,
          freq_mod_bike: 0,
          freq_mod_pub: 0,
          freq_mod_moto: 0,
          freq_mod_car: 0,
          freq_mod_train: 0,
          freq_mod_combined: false,
          freq_trav_pro_local: 0,
          freq_trav_pro_region: 0,
          freq_trav_pro_inter: 0,
          freq_mod_pro_walking: 0,
          freq_mod_pro_bike: 0,
          freq_mod_pro_pub: 0,
          freq_mod_pro_moto: 0,
          freq_mod_pro_car: 0,
          freq_mod_pro_train: 0,
          freq_mod_pro_plane: 0,
          importance_time: 1,
          importance_cost: 1,
          importance_flex: 1,
          importance_rel: 1,
          importance_comfort: 1,
          importance_most: 1,
          importance_env: 1,
          needs_walking: 1,
          needs_bike: 1,
          needs_pub: 1,
          needs_moto: 1,
          needs_car: 1,
          needs_train: 1,
          adjectives_bikes: [],
          adjectives_pubs: [],
          adjectives_motors: [],
          ...cr.data,
        }
        return {
          token: cr.token,
          data,
        } as Record
      })
      .finally(() => {
        loading.value = false
      })
  }

  async function save(tkOrSlug: string, record: Record) {
    token.value = null
    loading.value = true
    return api.post(`/collect/record/${tkOrSlug}`, record).finally(() => {
      loading.value = false
    })
  }

  async function loadTypo(record: Record) {
    token.value = null
    loading.value = true
    return api.get(`/collect/typo/${record.token}`, record).finally(() => {
      loading.value = false
    })
  }

  return {
    token,
    loading,
    load,
    save,
    loadTypo,
  }
})
