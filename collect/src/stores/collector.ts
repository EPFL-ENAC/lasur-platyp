import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from 'src/boot/api'
import type { Record, CampaignInfo, RecordCertificate } from 'src/models'
import { hashEmail } from 'src/utils/hash'
import { resolveLocation } from 'src/utils/boundaries'

// Current version of the form data structure
export const VERSION = '2.0.0'

function makeRecord(rec: Partial<Record>): Record {
  const data = {
    version: VERSION,
    terms_conditions: false,
    confidentiality: false,
    employment_rate: 100,
    remote_work_rate: 40,
    company_vehicle: null,
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
    changes: [],
    ...rec.data,
  }

  // Backward compatibility: records saved before boundary-based location
  // selection replaced the H3 grid only have `hex_id`; derive `location` from it.
  data.freq_mod_pro_journeys = (data.freq_mod_pro_journeys || []).map((journey) => ({
    ...journey,
    location: resolveLocation(journey.location, journey.hex_id),
  }))

  return {
    token: rec.token || '',
    data,
  } as unknown as Record // Type assertion to satisfy the original behavior
}

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

  async function loadRecordDraft(tkOrSlug: string): Promise<Record> {
    token.value = null
    loading.value = true

    return api
      .get(`/collect/record/${tkOrSlug}`)
      .then((response) => {
        token.value = response.data.token
        return makeRecord(response.data)
      })
      .finally(() => {
        loading.value = false
      })
  }

  async function loadRecordCertificate(tk: string): Promise<RecordCertificate> {
    loading.value = true

    return api
      .get(`/collect/certificate/${tk}`)
      .then((response) => {
        return response.data as RecordCertificate
      })
      .finally(() => {
        loading.value = false
      })
  }

  async function save(tkOrSlug: string, record: Record, plainEmail: string | null = null) {
    if (plainEmail) {
      record.email_hash = await hashEmail(plainEmail)
    }

    const response = await api.post(`/collect/record/${tkOrSlug}`, record)
    return response.data
  }

  async function loadTypo(record: Record, locale: string) {
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
    loading,
    token,
    loadInfo,
    loadRecordDraft,
    save,
    loadTypo,
    saveComments,
    loadRecordCertificate,
  }
})
