// Deployment branding, loaded before the app (see branding/README.md at the repo root).
// Replace this folder (e.g. with a docker volume on /app/branding) to rebrand without rebuilding.
window.branding = {
  // i18n messages merged over the built-in ones, per locale (see main.* in src/i18n)
  messages: {},
  // Footer partner columns: { logo, width, alt, url, name?, links?: [{ label, url }] }
  partners: [],
  // Side of the header menu button (the drawer it opens is always on the left side): 'left' (default) or 'right'
  menuSide: 'left',
}
