export function getRandomId(): string {
  if (window.crypto && window.crypto.randomUUID) {
    return window.crypto.randomUUID()
  } else {
    // Fallback for environments without crypto.randomUUID
    return 'xxxx-xxxx-xxxx-xxxx'.replace(/[x]/g, () => Math.floor(Math.random() * 16).toString(16))
  }
}
