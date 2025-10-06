export interface Option {
  value: string
  label: string
  hint?: string
  icon?: string
  exclusive?: boolean
  children?: Option[]
}

export interface ToggleOption {
  trueValue: string
  falseValue: string
  trueLabel: string
  falseLabel: string
  hint?: string
}
