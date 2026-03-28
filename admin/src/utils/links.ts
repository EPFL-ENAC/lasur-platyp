import { collectUrl } from "src/boot/api";

export function makeSurveyLink(slug: string) {
  return `${collectUrl}/go/${slug}`
}
