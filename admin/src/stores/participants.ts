import type { Campaign, Participant } from 'src/models'
const services = useServices()

export const useParticipants = defineStore('participants', () => {
  const items = ref<Participant[]>([])
  const campaign = ref<Campaign>()
  const service = services.make('participant')
  const loading = ref(false)

  async function load() {
    if (!campaign.value) return
    loading.value = true
    return service
      .find({
        $limit: 100,
        filter: {
          campaign_id: campaign.value.id,
        },
      })
      .then((res) => {
        items.value = res.data
      })
      .catch(() => {
        items.value = []
      })
      .finally(() => {
        loading.value = false
      })
  }

  return {
    items,
    campaign,
    loading,
    service,
    load,
  }
})
