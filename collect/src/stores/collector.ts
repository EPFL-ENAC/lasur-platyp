import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from 'src/boot/api'
import type { ParticipantData } from 'src/models'

export const useCollector = defineStore('collector', () => {
  const token = ref<string | null>(null)
  const participantData = ref<ParticipantData | null>(null)
  const loading = ref<boolean>(false)

  async function loadToken(tk: string) {
    token.value = null
    loading.value = true
    return api
      .get(`/collect/participant/${tk}`)
      .then((response) => {
        participantData.value = response.data
        token.value = tk
      })
      .finally(() => {
        loading.value = false
      })
  }

  return {
    token,
    participantData,
    loading,
    loadToken,
  }
})
