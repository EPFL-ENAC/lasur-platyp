import { Notify } from 'quasar'
import { t } from 'src/boot/i18n'

export function notifySuccess(message: string) {
  Notify.create({
    type: 'positive',
    message: t(message),
  })
}

export function notifyInfo(message: string) {
  Notify.create({
    type: 'info',
    message: t(message),
  })
}

export function notifyWarning(message: string) {
  Notify.create({
    type: 'warning',
    message: t(message),
  })
}

// Matches the backend's expired/invalid bearer token detail, e.g.
// "Not found 'Expired at 1783588004, time: 1783594855(leeway: 60)'".
// Kept here (rather than duplicated) so both the axios interceptor and
// notifyError agree on what counts as a session-expiry error.
const sessionExpiredPattern = /expired at \d+, time: \d+\(leeway: \d+\)/i

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function isSessionExpiredError(error: any): boolean {
  const detail = error?.response?.data?.detail
  return typeof detail === 'string' && sessionExpiredPattern.test(detail)
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function notifyError(error: any) {
  // Already surfaced as a friendlier "session expired" warning by the
  // axios interceptor in boot/api.ts — avoid a second, confusing toast.
  if (isSessionExpiredError(error)) return

  let message = t('unknown_error')
  if (typeof error === 'string') {
    message = t(error)
  } else {
    console.error(error)
    message = error.message
    if (error.response?.data && error.response.data?.detail) {
      message = t(error.response.data.detail)
    }
  }
  Notify.create({
    type: 'negative',
    message,
  })
}
