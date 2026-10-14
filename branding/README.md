# Branding

The admin and collect apps ship with a neutral "Platform" branding (`admin/public/branding/`,
`collect/public/branding/`). A deployment replaces it at runtime, without rebuilding the images,
by mounting its own folder over `/app/branding` in the container:

```yaml
admin:
  volumes:
    - ./branding/admin:/app/branding:ro
collect:
  volumes:
    - ./branding/collect:/app/branding:ro
```

nginx serves `/branding/` with `Cache-Control: no-cache`, so a change shows up on the next page load.

## Folder content

| File | Purpose |
|---|---|
| `branding.js` | Sets `window.branding` (see below) |
| `branding.css` | Brand palettes: `:root { --brand-primary-25 … --brand-primary-950; --brand-secondary-25 … --brand-secondary-950 }` (steps 25, 50, 100…900, 950). Missing ones fall back to the neutral defaults of `src/css/app.scss`. The primary colour is used as a surface with secondary-coloured text on it, so choose a light primary. |
| `favicon.svg` | Browser tab icon |
| `logo.svg`, `logo-dark.svg` | Brand logo for light and dark backgrounds |
| `logo-alt.svg` | Logo of the generated report (admin) |
| `pattern.svg`, `pattern-dark.svg` | Decorative background, light and dark themes |
| `pattern-accent.svg` | Report page background (admin) |
| `wheel-en.svg`, `wheel-fr.svg` | Mobility demands wheel, shown in the report and the docs (admin) |

All files must be present: the defaults show what each one looks like.

## `branding.js`

```js
window.branding = {
  // i18n messages merged over the built-in ones, per locale
  messages: {
    en: {
      main: {
        brand: 'Mobilyse', // product name, used throughout the texts
        operator: 'the Modus Foundation', // legal party of the terms of use
        authors: 'the Modus Foundation and EPFL', // who made the tool
        links: { website: 'https://…', terms: 'https://…', privacy: 'https://…' },
      },
      footer: { modus_name: 'Fondation Modus' }, // keys used by the partners below
    },
    fr: { /* … */ },
  },
  // Footer partner columns; the logo is a single-colour SVG painted with the footer text colour
  partners: [
    {
      logo: '/branding/modus.svg', // '/admin/branding/…' in the admin app
      width: 104, // px, the height is 32px
      alt: 'Modus',
      url: 'https://modus-ge.ch/',
      name: 'footer.modus_name', // optional i18n key
      links: [{ label: 'footer.modus_tagline', url: 'https://modus-ge.ch/' }], // label is an i18n key
    },
  ],
  menuSide: 'left', // header menu button and drawer side (admin): 'left' (default) or 'right'
}
```

Any other i18n message can be overridden the same way, for instance the consent texts. In the built-in
messages, the brand is referenced as `@:{'main.brand'}` (vue-i18n linked message), and in the admin
docs markdown as `{brand}`, `{terms_url}` and `{privacy_url}`. An empty `terms` or `privacy` link hides it.

The Mobilyse branding lives in its deployment repository (`lasur-platyp-modus`, `branding/`).
