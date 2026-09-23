import type { Company, CompanyAction } from '@/models'
const services = useServices()

export const useActions = defineStore('actions', () => {
  const items = ref<CompanyAction[]>([])
  const company = ref<Company>()
  const service = services.make('action')
  const loading = ref(false)
  // id of the company for which the items were successfully loaded
  const loadedCompanyId = ref<number>()

  function isLoadedFor(companyId: number | undefined) {
    return companyId !== undefined && !loading.value && loadedCompanyId.value === companyId
  }

  // whether a custom action id does not match any existing custom action of the company
  function isDeleted(action: string, companyId: number | undefined) {
    const actionId = parseInt(action, 10)
    if (isNaN(actionId) || !isLoadedFor(companyId)) return false
    return !items.value.find((item) => item.id === actionId)
  }

  async function load() {
    items.value = []
    loadedCompanyId.value = undefined
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
        loadedCompanyId.value = company.value?.id
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
    isLoadedFor,
    isDeleted,
  }
})
