import type { EmployerActions } from 'src/models'
import type { FieldItem } from 'src/components/FieldsList.vue'
import { t } from 'src/boot/i18n'

export const actionItems: FieldItem[] = [
  'mesures_globa',
  'mesures_tpu',
  'mesures_train',
  'mesures_inter',
  'mesures_velo',
  'mesures_covoit',
  'mesures_elec',
].map((field) => ({
  field,
  label: `actions.${field}_label`,
  format: (actions: EmployerActions) =>
    actions?.[field]?.map((action: string) => t(`actions.${action}`)).join('; ') || '-',
}))

export const actionProItems: FieldItem[] = [
  'mesures_pro_velo',
  'mesures_pro_tpu',
  'mesures_pro_train',
  'mesures_pro_elec',
].map((field) => ({
  field,
  label: `actions.${field}_label`,
  format: (actions: EmployerActions) =>
    actions?.[field]?.map((action: string) => t(`actions.${action}`)).join('; ') || '-',
}))
