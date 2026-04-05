import type { Campaign } from 'src/models'
const services = useServices()

export const useCampaigns = defineStore('campaigns', () => {
  const items = ref<Campaign[]>([])
  // const company = ref<Company>()
  const companyId = ref<number>()
  const service = services.make('campaign')
  const loading = ref(false)

  async function load() {
    if (!companyId.value) return
    console.log('Loading campaigns for company', companyId.value)
    loading.value = true
    return service
      .find({
        $limit: 100,
        filter: {
          company_id: companyId.value,
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

  async function loadIfNeeded(id: number | undefined) {
    if (!id) return
    if (companyId.value === id && items.value.length > 0) return
    
    companyId.value = id
    await load()
  }

  return {
    items,
    companyId,
    loading,
    service,
    load,
    loadIfNeeded
  }
})
