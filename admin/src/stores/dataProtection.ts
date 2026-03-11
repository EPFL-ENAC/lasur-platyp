export const useDataProtectionStore = defineStore('dataProtection', () => {
  const STORAGE_KEY = "doNotShowDataProtectionNotice";

  const getStoredValue = () => {
    if (typeof window !== "undefined") {
      return localStorage.getItem(STORAGE_KEY) === "true";
    }
    return false;
  };

  const doNotShowNotice = ref(getStoredValue())

  watch(doNotShowNotice, (newValue) => {
    if (typeof window !== "undefined") {
      localStorage.setItem(STORAGE_KEY, newValue.toString())
    }
  })

  return {
    doNotShowNotice,
  }
})
