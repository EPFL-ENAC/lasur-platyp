export function generateToken(length: number): string {
  const PASSWORD_CHARACTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  const PASSWORD_CHARACTERS_LENGTH: number = PASSWORD_CHARACTERS.length
  const PASSWORD_MX_LENGTH = length

  let generated = ''

  for (let i = 0; i < PASSWORD_MX_LENGTH; i++) {
    generated += PASSWORD_CHARACTERS.charAt(Math.floor(Math.random() * PASSWORD_CHARACTERS_LENGTH))
  }

  return generated
}
