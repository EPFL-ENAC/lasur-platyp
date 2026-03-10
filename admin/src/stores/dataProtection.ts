export const useDataProtectionStore = defineStore('dataProtection', () => {
  const doNotShowNotice = ref(localStorage.getItem('doNotShowDataProtectionNotice') === 'true')

  watch(doNotShowNotice, (newValue) => {
    localStorage.setItem('doNotShowDataProtectionNotice', newValue.toString())
  })

  return {
    doNotShowNotice,
  }
})
