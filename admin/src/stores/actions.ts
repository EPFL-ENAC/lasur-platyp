import type { Company, CompanyAction } from 'src/models'
const services = useServices()

export const useActions = defineStore('actions', () => {
  const items = ref<CompanyAction[]>([])
  const company = ref<Company>()
  const service = services.make('action')
  const loading = ref(false)

  async function load() {
    items.value = []
    if (!company.value || !company.value.id) return
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
