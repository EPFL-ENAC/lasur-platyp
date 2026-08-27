import { collectUrl } from '@/boot/api'

export function makeSurveyLink(slug: string) {
  return `${collectUrl}/go/${slug}`
}
