import type { Campaign, Company } from 'src/models'
const services = useServices()

export const useCampaigns = defineStore('campaigns', () => {
  const items = ref<Campaign[]>([])
  const company = ref<Company>()
  const service = services.make('campaign')
  const loading = ref(false)

  async function load() {
    if (!company.value) return
    loading.value = true
    return service
      .find({
        $limit: 100,
        filter: {
          company_id: company.value.id,
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
    company,
    loading,
    service,
    load,
  }
})
