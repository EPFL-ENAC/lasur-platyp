import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from 'src/boot/api'
import type { Record, CampaignInfo } from 'src/models'

// Current version of the form data structure
export const VERSION = '2.0.0'

export const useCollector = defineStore('collector', () => {
  const info = ref<CampaignInfo>({} as CampaignInfo)
  const token = ref<string | null>(null)
  const loading = ref<boolean>(false)

  async function loadInfo(tkOrSlug: string): Promise<CampaignInfo> {
    if (info.value.name) return Promise.resolve(info.value)
    return api.get(`/collect/info/${tkOrSlug}`).then((response) => {
      info.value = response.data
      return info.value
    })
  }

  async function load(tkOrSlug: string): Promise<Record> {
    token.value = null
    loading.value = true
    return api
      .get(`/collect/record/${tkOrSlug}`)
      .then((response) => {
        token.value = tkOrSlug
        const cr = response.data
        const data = {
          version: VERSION,

          terms_conditions: false,
          confidentiality: false,

          employment_rate: 100,
          remote_work_rate: 40,
          company_vehicle: false,
          travel_time: 5,
          equipments: [],
          constraints: [],
          freq_mod_journeys: [{ modes: [], days: 1 }],

          travel_pro: false,
          freq_mod_pro_journeys: [],

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

          change: {},
          change2: {},

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
    //loading.value = true
    return api.post(`/collect/record/${tkOrSlug}`, record).finally(() => {
      //loading.value = false
    })
  }

  async function loadTypo(record: Record, locale: string) {
    token.value = null
    loading.value = true
    return api
      .get(`/collect/record/${record.token}/typo`, { params: { locale } })
      .then((response) => {
        return response.data
      })
      .finally(() => {
        loading.value = false
      })
  }

  async function saveComments(record: Record) {
    token.value = null
    loading.value = true
    return api
      .put(`/collect/record/${record.token}/comments`, { comments: record.data.comments })
      .then((response) => {
        return response.data
      })
      .finally(() => {
        loading.value = false
      })
  }

  return {
    info,
    token,
    loading,
    loadInfo,
    load,
    save,
    loadTypo,
    saveComments,
  }
})
