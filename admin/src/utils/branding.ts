// Deployment branding, loaded at runtime by index.html from public/branding/branding.js.
// Mount another folder over /app/branding to rebrand without rebuilding (see branding/README.md).

export interface BrandingPartner {
  /** URL of a single-colour logo, painted with the footer foreground colour */
  logo: string
  /** Width of the logo box in px (height is 32px) */
  width: number
  url: string
  /** Accessible name of the logo */
  alt: string
  /** i18n key of the partner name */
  name?: string
  /** label is an i18n key */
  links?: { label: string; url: string }[]
}

export interface Branding {
  /** i18n messages per locale, merged over the built-in ones (e.g. main.brand) */
  messages?: Record<string, Record<string, unknown>>
  /** Partner columns shown in the footer */
  partners?: BrandingPartner[]
}

export const branding: Branding = (window as unknown as { branding?: Branding }).branding ?? {}
