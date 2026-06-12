interface MergeImageWithLogoOptions {
  padding?: number
  logoWidthRatio?: number
}

export async function mergeImageWithLogo(
  baseImageSrc: string,
  logoSrc: string,
  options: MergeImageWithLogoOptions = {},
): Promise<string> {
  const [baseImage, logoImage] = await Promise.all([loadImage(baseImageSrc), loadImage(logoSrc)])

  const canvas = document.createElement('canvas')
  canvas.width = baseImage.naturalWidth || baseImage.width
  canvas.height = baseImage.naturalHeight || baseImage.height

  const ctx = canvas.getContext('2d')
  if (!ctx) {
    throw new Error('Canvas context unavailable')
  }

  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, 0, canvas.width, canvas.height)
  ctx.drawImage(baseImage, 0, 0, canvas.width, canvas.height)

  const padding = options.padding ?? 24
  const logoWidthRatio = options.logoWidthRatio ?? 0.12
  const logoWidth = Math.round(canvas.width * logoWidthRatio)
  const logoHeight = Math.round(
    ((logoImage.naturalHeight || logoImage.height) / (logoImage.naturalWidth || logoImage.width)) *
      logoWidth,
  )

  ctx.drawImage(logoImage, canvas.width - logoWidth - padding, padding, logoWidth, logoHeight)

  return canvas.toDataURL('image/png')
}

export function loadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const image = new Image()
    image.onload = () => resolve(image)
    image.onerror = () => reject(new Error(`Failed to load image: ${src}`))
    image.src = src
  })
}

export function downloadDataUrl(dataUrl: string, fileName: string) {
  const link = document.createElement('a')
  link.href = dataUrl
  link.download = fileName
  link.click()
}
